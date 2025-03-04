from logging import error as log_info
from src.pages.generic.positions import Positions
from src.exceptions.exceptions import WebDriverError, CrawlerError
from os import environ
from src.helper.helper import save_description_to_database, Connection


class Generic:

    def __init__(self, locator):
        """
        This is what the name says: a generic crawler. It is intended to be used if the company's
            page that has all the links of positions available in a single page without pagination.
            Take the page bellow:
            (...)
                <div class="menu-container">
                    <a class = "menu" herf="www.fake.com">
                </div>
                <div class="positions-container>
                    <a class = "positions" href="www.fake.com/jobs/position_1">
                    <a class = "positions" href="www.fake.com/jobs/position_2">
                    <a class = "positions" href="www.fake.com/jobs/position_3">
                </div>
            (...)
            The locators a.positions (css locator) are the ones we are looking for.
        Arsg:
            locator (str): the locator of the links of positions, e.g. a.positions
        """
        self._url = None
        self._positions = None
        self.locator = locator

    def set_driver(self, driver):
        self._positions = Positions(driver)

    def set_url(self, url):
        self.url = url

    def run(self):
        links = self._get_link_by_browser()
        return self._get_info_from_links(links)

    def _get_link_by_browser(self):
        return self._positions.get_link_of_all_positons(self.locator)

    def _get_info_from_links(self, links):
        for link in links:
            try:
                print(f"Collecting data from postion '{link}'")
                self._positions.go_to_page(link)
                save_description_to_database(
                    Connection.get_connection_string(),
                    link,
                    self._positions.get_description()
                )
            except WebDriverError as error:
                message = f"Skipping process. Failed to get data from {link}"
                print(message)
                log_info(message)
                if environ.get("DEBUG") == "on":
                    raise CrawlerError(str(error)) from error
            except Exception as error:
                raise CrawlerError(str(error))
        return True
