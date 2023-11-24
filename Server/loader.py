import torch
from aiohttp import web
from loguru import logger

from ws_manager import WSManager
from database import DB

app = web.Application()
manager = WSManager()
db = DB()

logger.info("Загрузка модели... Пожалуйста подождите, данная операция может занять несколько минут времени!")

try:
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    best_model = torch.load('models/model.pth').to(device)
except:
    device = None
    best_model = torch.load('models/model.pth', map_location='cpu')

best_model.eval()

logger.success("Модель загружена!")
