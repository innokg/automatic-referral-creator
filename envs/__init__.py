from environs import Env
import os

from loguru import logger

try:
    os.mkdir("logs")
except:
    pass

env = Env()

try:
    env.read_env(".env")

    REDIS_HOST = env.str("REDIS_HOST")
    REDIS_PORT = env.int("REDIS_PORT")
    REDIS_PASSWORD = env.str("REDIS_PASSWORD")

except Exception as e:
    print(e)
    exit()


def get_logger(name: str) -> logger:
    logger.add(f'./logs/{name}_error.log', format="{time} {level} {name}:{function}:{line} {message}",
               level="ERROR")
    logger.add(f'./logs/{name}_warning.log', format="{time} {level} {name}:{function}:{line} {message}",
               level="WARNING")
    logger.add(f'./logs/{name}_debug.log', format="{time} {level} {name}:{function}:{line} {message}",
               level="DEBUG")
    logger.add(f'./logs/{name}_info.log', format="{time} {level} {name}:{function}:{line} {message}",
               level="INFO")
    return logger