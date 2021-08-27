import logging
import os
import signal
from time import sleep
from typing import Optional

from requests import sessions
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


class URIHelper:
    NUMBER_OF_TIMES_TO_RETRY_PAGE_LOAD = 3
    EMPTY_HTML_PAGE = '<html><head></head><body></body></html>'.encode('ascii', 'ignore')
    BACKOFF_NUM = 5
    BROWSER_WINDOW_SIZE = 400, 300

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def resolves(self, url, timeout=60):
        """
            Returns a boolean indicating whether the site resolves or not
            :param url:
            :param timeout:
            :return:
            NOTE: If we are using auth, requests library will not resend auth on a redirect (will result in a 401),
            so we need to manually check for one and re-issue the get with the redirected url and the auth credentials
            """
        try:
            with sessions.Session() as session:
                bad_site = session.request(method='GET', url=url, timeout=timeout)
                status = str(bad_site.status_code)
                if status[0] in ["1", "2", "3"]:
                    return True
                return status in ["406", "403"]
        except Exception as e:
            self._logger.error(
                "Error in determining if url resolves {} : {}".format(url, e))
            return False

    def get_site_data(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Returns the sourcecode string for the url provided
        :param url: string
        :param timeout: int value of page load timeout
        :return: string of sourcecode or None
        """
        sourcecode = None
        for _ in range(self.NUMBER_OF_TIMES_TO_RETRY_PAGE_LOAD):
            try:
                options = webdriver.FirefoxOptions()
                options.headless = True
                profile = webdriver.FirefoxProfile()
                options.set_preference("javascript.enabled", False)
                browser = webdriver.Firefox(options=options, firefox_profile=profile)
                browser.set_window_size(*self.BROWSER_WINDOW_SIZE)
                browser.set_page_load_timeout(timeout)
                browser.get(url)
                sourcecode = self._backoff(browser)
            except Exception as e:
                self._logger.error(f"Error while scraping source code for {url}: {e}")
            finally:
                try:
                    browser.quit()
                    os.kill(browser.service.process.pid, signal.SIGTERM)
                except Exception:
                    pass
            if sourcecode:
                break
        if isinstance(sourcecode, bytes):
            sourcecode = sourcecode.decode()
        return sourcecode

    def _backoff(self, browser):
        """
        Returns the source code from the last request page of a selenium driver instance.
        :param browser:
        :return:
        """
        sourcecode = None
        for i in range(self.BACKOFF_NUM):
            sourcecode = browser.page_source.encode('ascii', 'ignore')
            try:
                WebDriverWait(browser, i).until(
                    lambda driver: driver.execute_script('return document.readyState') == 'complete')
                source = browser.page_source.encode('ascii', 'ignore')
                if source != self.EMPTY_HTML_PAGE:
                    break
            except Exception:
                pass
            sleep(i)
        return sourcecode
