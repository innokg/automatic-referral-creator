import sys
import time
from playwright.sync_api import sync_playwright

from envs import get_logger
from m_worker.get_airtable import AirTable
from m_worker.tempmail import TempMail
from utils.rs import Cache

playwright = sync_playwright().start()
logger = get_logger('Air_main')


class Worker:
    """
    Class for main worker
    """
    def __init__(self):
        self.cache_0 = Cache(0)
        self.cache_1 = Cache(1)
        self.airtable = None
        self.tempmail = None



    def main(self, referal_link, password):
        """
        main method
        :param referal_link:
        :param password:
        """
        try:
            sys.path.append('/app/profile/airtableinvite')
            sys.path.remove('/app/profile/airtableinvite')
            logger.info(f"Deleted 'airtableinvite' path.")
        except Exception as ex:
            logger.error(f"Can't delete 'airtableinvite' path. {ex}")
            pass

        self.airtable = AirTable(referal_link, playwright)
        self.tempmail = TempMail(playwright, self.cache_1)

        if not (email := self.tempmail.get_email()):
            self.cache_0.red.set("task_progress", 0)
            return None, False

        if not (self.airtable.register(email, password)):
            self.cache_0.red.set("task_progress", 0)
            return email, False

        if not (invite_link := self.tempmail.get_invite_link()):
            self.cache_0.red.set("task_progress", 0)
            return email, False

        if not self.airtable.verify_account(email, password, invite_link):
            self.cache_0.red.set("task_progress", 0)
            return email, False
        self.cache_0.red.incr("task_progress", 1)
        return email, True

    def exit(self):
        time.sleep(10)
        self.airtable.airtable_invite_context.close()
        self.tempmail.tempmail_context.close()
        self.cache_0.red.incr("task_progress", 1)


    def run(self):
        while True:
            if self.cache_0.red.llen('queue_worker') > 0:
                logger.info('Start task.')
                time.sleep(0.5)
                referral_link = self.cache_0.red.get("referral_link")
                uid = self.cache_0.red.lpop('queue_worker')
                if (referral_link is not None) and (uid is not None):
                    from utils.password import get_password
                    password = get_password()
                    email, result = self.main(referral_link, password)
                    self.exit()
                    queue_orchestrator = f'{uid}###{email}###{result}'
                    self.cache_0.red.rpush('queue_orchestrator', queue_orchestrator)
            else:
                time.sleep(3)
                self.cache_1.red.set('run', '0')

            time.sleep(60)



if __name__ == "__main__":
    worker = Worker()
    worker.run()