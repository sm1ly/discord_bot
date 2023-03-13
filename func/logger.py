import logging

# создаем логгер с именем 'bot'
logger = logging.getLogger('bot')
# logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

# создаем обработчик для записи логов в файл
file_handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
file_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s'))
logger.addHandler(file_handler)

# создаем обработчик для записи логов в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s'))
logger.addHandler(console_handler)

# выводим логи в файл и в консоль
logger.info('Logging started!')
