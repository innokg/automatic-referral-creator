import time

from envs import get_logger
from utils.rs import Cache
import uuid

logger = get_logger('Air_main')


class Orchestrator:
    """
    class for Orchestrator
    """
    cache_0 = Cache(0)
    cache_1 = Cache(1)

    def __init__(self):
        self.queue = []

    def create_queue(self):
        self.queue = []
        for i in range(int(self.cache_0.red.get("required_accounts"))):
            uid = str(uuid.uuid4())
            logger.info(f'New task: {uid}')

            self.queue.append(uid)
            self.cache_0.red.rpush("queue_worker", uid)

    def run(self):
        """
        function that run queue
        """
        while True:
            if self.cache_0.red.get("run") == "1":
                if self.cache_0.red.llen('queue_worker') == 0:
                    self.create_queue()

                while self.cache_0.red.get("run") == "1":
                    time.sleep(0.01)
                    if self.cache_0.red.llen("queue_orchestrator") == 0:
                        continue

                    result = self.cache_0.red.lpop("queue_orchestrator")
                    uid, email, result = result.split("###")
                    try:
                        self.queue.remove(uid)
                    except:
                        pass
                    self.cache_1.red.set(email, email)
                    if result != 'False':
                        self.cache_0.red.incr("numbers_of_account", 1)
                    else:
                        self.cache_0.red.incr("bad_attempts", 1)
                        self.cache_0.red.rpush('queue_worker', uid)
                        self.queue.append(uid)



                bad_queue = len(self.queue)
                self.queue = []
                self.cache_0.red.set("bad_queue", bad_queue)

            time.sleep(1)


if __name__ == "__main__":
    o = Orchestrator()
    o.run()
