import redis

import envs


class Cache:
    """
    Class for create cache using Redis
    """
    def __init__(self, db: int = 0):
        self.red = redis.StrictRedis(
            host=envs.REDIS_HOST,
            port=envs.REDIS_PORT,
            password=envs.REDIS_PASSWORD,
            decode_responses=True,
            db=db,
        )
