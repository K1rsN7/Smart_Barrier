import asyncio
import decimal
import json
import time
import traceback
import datetime
from typing import List
import cv2
import torch
import numpy as np

import aiohttp
from aiohttp import web
from loguru import logger

import config as cfg
from loader import manager, app, db, best_model, device
from database import DictRecord


async def check_parameters_in_json(ws: web.WebSocketResponse, needed_params: List[str], json_data: dict) -> bool:
    """
    :param ws: WebSocket object
    :param needed_params: Список ключей, которые должны присутствовать в json_data
    :param json_data: данные, представленные в JSON формате
    :return: Truе - Все параметры присутствуют | False - какого-то параметра не хватает
    """
    for par in needed_params:
        if par not in json_data.keys():
            await manager.send_personal_message(ws, f"Параметр \"{par}\" отсутствует!")
            return False

    return True


def json_encoder(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, DictRecord):
        return obj.to_dict()
    elif isinstance(obj, decimal.Decimal):
        return int(obj)

    raise TypeError(f"{obj} is not JSON serializable")


async def ws_handler(request):
    ws = web.WebSocketResponse()
    try:
        await ws.prepare(request)
    except:
        traceback.print_exc()

    await manager.add(ws)

    async for msg in ws:
        msg: aiohttp.http_websocket.WSMessage
        if msg.type == web.WSMsgType.TEXT:
            ##==> Check data
            try:
                data = json.loads(msg.data)
            except json.JSONDecodeError:
                await manager.send_personal_message(ws, f"Invalid message, please send JSON data.")
                continue

            if not await check_parameters_in_json(ws, ["method"], data):
                logger.info("нет параметра mehod")
                continue

            match data["method"]:
                case "get_history":
                    response = await db.get_history()
                    await manager.send_personal_message(
                        ws,
                        json.dumps(
                            dict(
                                method="get_history",
                                history=response
                            ),
                            default=json_encoder
                        )
                    )

                case "open_barrier":
                    cfg.barrier_is_opened = True
                    await db.add_history("user", True)
                    await manager.broadcast_without_ws(
                        json.dumps(dict(method="change_barrier_button", status=True, who="user")),
                        ws
                    )
                    logger.info(f"Кнопку активировали {cfg.barrier_is_opened}")

                case "close_barrier":
                    cfg.barrier_is_opened = False
                    await db.add_history("user", False)
                    await manager.broadcast_without_ws(
                        json.dumps(dict(method="change_barrier_button", status=False, who="user")),
                        ws
                    )
                    logger.info(f"Кнопку деактивировали {cfg.barrier_is_opened}")

                case "ai_enable":
                    cfg.ai_is_enabled = True
                    await manager.broadcast_without_ws(json.dumps(dict(method="change_ai_button", status=True)), ws)
                    logger.info("Искусственный интеллект включен!")

                case "ai_disable":
                    cfg.ai_is_enabled = False
                    await manager.broadcast_without_ws(json.dumps(dict(method="change_ai_button", status=False)), ws)
                    logger.info("Искусственный интеллект выключен!")

                case "get_status_barrier_button":
                    await manager.send_personal_message(
                        ws,
                        json.dumps(dict(method="get_status_barrier_button", status=cfg.barrier_is_opened))
                    )

                case "get_status_ai_button":
                    await manager.send_personal_message(
                        ws,
                        json.dumps(dict(method="get_status_ai_button", status=cfg.ai_is_enabled))
                    )

                case _:
                    await manager.send_personal_message(ws, "Данного метода не существует...")

        elif msg.type == web.WSMsgType.ERROR:
            logger.error(f"Ws connection closed with error: {str(ws.exception())}")

    manager.delete(ws)
    return ws


def setup_routers(app):
    app.router.add_route('GET', '/barrierapp/ws', ws_handler)
    logger.success("Роутеры установлены!")


async def ai_working():
    while True:
        await asyncio.sleep(4)

        if cfg.ai_is_enabled:
            start_time = time.time()
            X = []
            src = cv2.imread(cfg.PATH_TO_IMAGE, cv2.IMREAD_COLOR)
            dst = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
            X.append(cv2.resize(dst, dsize=(200, 200), interpolation=cv2.INTER_AREA))
            X = np.array(X)
            X = X.astype('float32')
            X = X / 255.0
            X = X.reshape(-1, 3, 200, 200)

            if isinstance(device, torch.device):
                X = torch.from_numpy(X).float().to(device)
            else:
                X = torch.from_numpy(X).float()

            result = bool(best_model(X).argmax(-1).item())

            if cfg.barrier_is_opened != result:
                cfg.barrier_is_opened = result
                await db.add_history("ai", cfg.barrier_is_opened)
                await manager.broadcast(message=json.dumps(dict(method="change_barrier_button", status=cfg.barrier_is_opened, who="ai")))

            logger.info(
                f"Нейросеть думает, что на изображении {'служебная' if result else 'обычная'} машина | "
                f"Время распознования - {str(time.time()-start_time)[:5]}"
            )


async def on_startup(_):
    await db.init_database()
    asyncio.create_task(ai_working())


if __name__ == '__main__':
    setup_routers(app)
    app.on_startup.append(on_startup)
    web.run_app(
        app=app,
        host=cfg.host,
        port=cfg.port,
        print=logger.success("Сервер запущен!")
    )
