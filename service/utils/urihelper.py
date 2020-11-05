import logging
import signal

from requests import sessions
from selenium import webdriver


class URIHelper:
    NUMBER_OF_TIMES_TO_RETRY_PAGE_LOAD = 3

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
                "Error in determining if url resolves {} : {}".format(
                    url, e.message))
            return False

    def get_site_data(self, url, timeout=10):
        """
        Returns the sourcecode string for the url provided
        :param url: string
        :param timeout: int value of page load timeout
        :return: string of sourcecode
        """
        sourcecode = None
        for i in range(self.NUMBER_OF_TIMES_TO_RETRY_PAGE_LOAD):
            browser = None
            try:
                browser = webdriver.PhantomJS()
                browser.set_page_load_timeout(timeout)
                browser.get(url)
                sourcecode = browser.page_source.encode('ascii', 'ignore')
            except Exception as e:
                self._logger.error("Error while taking snapshot and/or source code for {}: {}".format(url, e))
            finally:
                try:
                    if browser:
                        browser.service.process.send_signal(signal.SIGTERM)
                        browser.close()
                        browser.quit()
                except Exception:
                    pass
            if sourcecode:
                break
        return sourcecode
