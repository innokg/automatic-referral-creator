import time

from playwright.sync_api import Page


def wait_element(page: Page, element: str, timeout: int = 100):
    """function to wait elements from tempmailo.com"""
    try:
        if page.wait_for_selector(element, timeout=timeout):
            return True
    except:
        return False


def wait_element_for_send(page: Page, element: str, data: str, attempts: int = 20):
    """function to wait elements from tempmailo.com and break if captcha will come out"""
    while attempts:
        if wait_element(page, '//*[@id="px-captcha"]'):
            break
        if wait_element(page, element):
            page.locator(element).fill(data)
            return True

        attempts -= 1
        time.sleep(1)
    return False


def wait_element_for_click(page: Page, element: str, attempts: int = 20):
    """function to wait elements from tempmailo.com and clicking"""
    while attempts:
        if wait_element(page, '//*[@id="px-captcha"]'):
            break
        if wait_element(page, element):
            page.locator(element).click()
            return True

        attempts -= 1
        time.sleep(1)
    return False
