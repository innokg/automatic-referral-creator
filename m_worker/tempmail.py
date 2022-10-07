import os
import time
from playwright.sync_api import BrowserContext

import envs
from utils.rs import Cache
from utils.wait import wait_element_for_click


logger = envs.get_logger('tempmail')
proxy = {
    "server": "http://usa.rotating.proxyrack.net:333",
    "username": "introlabanastasiia",
    "password": "e0003f-673bef-be8f3f-359b92-fee75e"
}


class TempMail:
    """
    Class for working with tempmailo.com
    """
    cache_0 = Cache(0)
    URL = "https://tempmailo.com/"

    def __init__(self, playwright, cache_1: Cache) -> None:
        try:
            os.rmdir('./profile/tempmail')
        except:
            pass
        self.tempmail_context: BrowserContext = playwright.chromium.launch_persistent_context(
            user_data_dir='./profile/tempmail', proxy=proxy, headless=True)
        self.tempmail_context.clear_cookies()
        self.tempmail_page = self.tempmail_context.new_page()
        self.tempmail_page.goto(self.URL, timeout=500000)
        self.cache_1 = cache_1

    def get_email(self):
        """
        Function to get invitation link from tempmaiilo.com
        """

        logger.info("TempMail Wait change element.")
        if not wait_element_for_click(self.tempmail_page, '//*[@id="apptmo"]/div/div[1]/div[2]/div[3]/button'):
            logger.error("TempMail Error change element.")

        logger.info("TempMail Wait confirm change element.")
        if not wait_element_for_click(self.tempmail_page, '//*[@id="apptmo"]/div[2]/div/div[3]/button[1]'):
            logger.error("TempMail Error confirm change element.")
        time.sleep(7)
        attempts = 5
        while attempts:

            email = self.tempmail_page.input_value('//*[@id="i-email"]')

            logger.info(f'Email: {email}')
            if not self.cache_1.red.get(email):
                self.cache_0.red.incr("task_progress", 1)
                return email
            wait_element_for_click(self.tempmail_page, '//*[@id="apptmo"]/div/div[1]/div[2]/div[3]/button')
            wait_element_for_click(self.tempmail_page, '//*[@id="apptmo"]/div[2]/div/div[3]/button[1]')

    @staticmethod
    def get_iframe(iframes: list):
        """
        function to get iframe from the tempmailo.com
        """
        for i in iframes:
            if i.name == "fullmessage":
                return i
        return None

    def get_invite_link(self):
        """
        function to accepting invitation link
        """
        attempts = 5
        while attempts:
            logger.info(f'TempMail check email. Attempts: {attempts}')
            self.tempmail_page.reload(timeout=60_000)
            wait_element_for_click(self.tempmail_page,
                                   '//*[@id="apptmo"]/div/div[2]/div[1]/ul/li/div[2]/div')
            iframe = self.get_iframe(self.tempmail_page.frames)
            try:
                a = iframe.locator("//html/body/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]/a")

                logger.info('Accept invite link')
                href = a.get_attribute("href")
                logger.info(f'TempMail get invite link: {href}')
                self.cache_0.red.incr("task_progress", 1)
                return href
            except:
                pass
            self.tempmail_page.screenshot(path='./profile/bad_invite.png')
            if attempts:
                attempts -= 1
                time.sleep(5)

        logger.error(f'TempMail Error check email. Attempts: {attempts}')
        return False
