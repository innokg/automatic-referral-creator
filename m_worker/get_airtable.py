import time

from playwright.sync_api import BrowserContext
from playwright_stealth import stealth_sync

from envs import get_logger
from utils.rs import Cache
from utils.wait import wait_element_for_click, wait_element_for_send

logger = get_logger('airtable')
proxy = {
    "server": "http://usa.rotating.proxyrack.net:333",
    "username": "introlabanastasiia",
    "password": "e0003f-673bef-be8f3f-359b92-fee75e"
}


class AirTable:
    """
    Class for login to Airtable page
    """
    cache_0 = Cache(0)


    def __init__(self, referal_link, playwright) -> None:
        self.link = referal_link

        self.airtable_invite_context: BrowserContext = playwright.chromium.launch_persistent_context(proxy=proxy, user_data_dir='./profile/airtableinvite', headless=False)
        self.airtable_invite_context.clear_cookies()
        self.airtable_invite_page = self.airtable_invite_context.new_page()
        stealth_sync(self.airtable_invite_page)
        self.airtable_invite_page.goto('https://httpbin.org/ip', timeout=500_000)


    def register(self, email, password):
        """
        function that register on Airtable page
        :param email:
        :param password:
        """
        try:
            logger.info("AirTable open referral link.")
            self.airtable_invite_page.goto(self.link, timeout=500_000)
        except:
            logger.error("AirTable Error bad referral link.")
            return False

        time.sleep(3)
        logger.info("AirTable Wait new email element1.")
        if not wait_element_for_send(self.airtable_invite_page, '//*[@id="emailSignup"]', email):
            self.airtable_invite_page.screenshot(path='./profile/new_name1.png')
            logger.error("AirTable Error new email element1.")
            return False
        self.cache_0.red.incr("task_progress", 1)

        time.sleep(4)

        email = email.split('@')[0]
        fullname = f'{email[:len(email) // 2].title()} {email[len(email) // 2:].title()}'


        logger.info("AirTable Wait new email element2.")
        if not wait_element_for_send(self.airtable_invite_page, '//*[@id="signUpForm"]/div[2]/div[1]/input', fullname):
            self.airtable_invite_page.screenshot(path='./profile/new_name2.png')
            logger.error("AirTable Error new email element2.")
            return False
        self.cache_0.red.incr("task_progress", 1)

        time.sleep(5)
        logger.info("AirTable Wait new password element.")
        if not wait_element_for_send(self.airtable_invite_page, '//*[@id="signUpForm"]/div[3]/div/input', password):
            self.airtable_invite_page.screenshot(path='./profile/new_password.png')
            logger.error("AirTable Error new password element.")
            return False
        time.sleep(6)
        logger.info("AirTable Wait create button element.")
        if not wait_element_for_click(self.airtable_invite_page, '//*[@id="signUpForm"]/button'):
            self.airtable_invite_page.screenshot(path='./profile/create_button.png')
            logger.error("AirTable Error create button element.")
            return False
        self.cache_0.red.incr("task_progress", 1)

        """
        Press 'Skip' button 2 times after created account 
        """
        time.sleep(20)
        logger.info("After complete creating Account press 'skip' button 2 times")
        self.airtable_invite_page.screenshot(path='./profile/skip.png')
        if not wait_element_for_click(self.airtable_invite_page, '//*[@id="wizardLeft"]/div/form/div[2]/div[2]/button') \
                    and not wait_element_for_click(self.airtable_invite_page, '//*[@id="wizardLeft"]/div/form/div[2]/div[2]/button'):
            self.airtable_invite_page.screenshot(path='./profile/press_skip.png')
            logger.error("Airtable Error skip button")
            return False
        self.cache_0.red.incr("task_progress", 1)
        return True

    def verify_account(self, email, password, invite_link):
        """
        function that verify account
        """
        try:
            logger.info("AirTable open accept link.")
            self.airtable_invite_page.goto(invite_link, timeout=500_000)
        except:
            logger.error("AirTable Error bad accept link.")
            return False

        self.cache_0.red.incr("task_progress", 1)

        return True
