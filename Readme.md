﻿# Welcome to IntelliGate!
Наше приложение - это **удобный** и **инновационный** способ открыть шлагбаумы. Теперь вы можете открыть шлагбаумы самостоятельно, без необходимости ждать, когда кто-то другой сделает это за вас. Наша нейросеть также обеспечивает безопасность, автоматически открывая шлагбаумы для автомобилей специальных служб. Больше не нужно тратить время на ожидание, наше приложение позволяет вам быстро и легко пройти через шлагбаумы, обеспечивая максимальный комфорт и безопасность.


# Установка сервера
### Установка зависимостей
Переходим в каталог `Server`
Для работы нам потребуется **[PyTorch](https://pytorch.org/get-started/locally/)**.
Скачиваем с официального сайта версию с CUDA 11.8
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```
Для ускорения вычислений во множество раз, при установленной видеокарте на сервере, советуем вам повторить настройку PyTorch с данного **[видео](https://youtu.be/xTF_n1jp9n8?si=YYqVOaoARA-GYKq-)**.
- - - 
Устанавливаем остальные библиотеки 
```bash
pip3 install -r requirements.txt
```
### Настройки программы
В дирректории `Server` создаем файл с названием `.env`, его же нам и предстоит настроить.
Скопируйте этот код, и подставьте настройки.
```
PATH_TO_IMAGE=images/test_image.jpg
HOST=localhost
PORT=5000

DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=123456789
DB_NAME=IntelliGate
```
**PATH_TO_IMAGE** - Путь до изображения, которое предстоит считывать нейросети 
**HOST** - IP адрес, на котором будет размещен python сервер
**PORT** - Порт, на котором будет открыт python сервер

**DB_HOST** - IP адрес, на котором находится PostgreSQL
**DB_PORT** - Порт, на котором находится PostgreSQL
**DB_USER** - Имя пользователя от базы данных PostgreSQL
**DB_PASSWORD** - Пароль от базы данных PostgreSQL
**DB_NAME** - Название базы данных PostgreSQL (Перед запуском сервера, вам предстоит ее создать)
# Билд приложения
**! Предварительно необходимо установить NodeJS !**<br>
1 - Открываем данный файл в любом редакторе `App/assets/main/js`<br>
2 - На 110 строке находим `const ws = new WebSocket("wss://example.ru/ws")`<br>
3 - Заменяем `example.ru` на свое доменное имя<br>
4 - Открываем  консоль в  корневой директории каталога App<br>
5 - Выполняем команду `androidjs build --release`
6 - Собранное приложение будет лежать в каталоге `dist`
