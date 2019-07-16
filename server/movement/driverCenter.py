from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
from selenium.webdriver.support.ui import WebDriverWait
import time

chrome_options = Options()
chrome_options.add_extension("movement/driver/IO_log_collector.crx")  # .crx file


class Driver:
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path="movement/driver/chromedriver.exe", chrome_options=chrome_options)
        self.method_list = {
            "id": self.driver.find_element_by_id,
            "name": self.driver.find_element_by_name,
            "xpath": self._xpath_find,
            "partial_link_text": self.driver.find_element_by_partial_link_text,
            "link_text": self.driver.find_element_by_link_text,
        }
        self.try_times = 0

    def get(self, url):
        self.driver.get(url)

    def click_sequence(self, clicks):
        for i in clicks:
            self.driver.find_element_by_partial_link_text(i).click()

    def fill_in_sequence_name(self, info):
        for i in info:
            self.driver.find_element_by_name(i).send_keys(info[i])

    def fill_in_sequence_id(self, info):
        for i in info:
            self.driver.find_element_by_id(i).send_keys(info[i])

    def _xpath_find(self, argument):
        return self.driver.find_element(By.XPATH, argument)

    def find_element(self, type_is, argument):
        """
        :param type_is:
        :param argument:
        :return: element
        """
        try:
            return self.method_list[type_is](argument)
        except Exception as arg:  # try 5s times to wait page
            if type(arg) == NoSuchElementException and self.try_times < 5:
                time.sleep(1)
                self.try_times += 1
                return self.find_element(type_is, argument)
            else:
                raise Exception(arg)

    def run_activities(self, activities):
        """
        :param activities: a sequence of activities
        {
            "act": "click, send_keys",
            "send_keys": "demo",
            "element_fetch":{
                "type":"method_list's type is",
                "argument":"argument"
            }
            "sleep":seconds
        }

        :return:
        """
        for i in activities:
            self.try_times = 0
            if i["act"] == "click":
                try:
                    self.find_element(i["element_fetch"]["type"], i["element_fetch"]["argument"]).click()
                except Exception as arg:
                    if type(arg) == ElementNotVisibleException:  # some animation make the element is invisible
                        time.sleep(1)
                        self.find_element(i["element_fetch"]["type"], i["element_fetch"]["argument"]).click()
                    else:
                        raise Exception(arg)

            elif i["act"] == "send_keys":
                self.find_element(i["element_fetch"]["type"], i["element_fetch"]["argument"]).send_keys(i["send_keys"])

            if "sleep" in i.keys():
                time.sleep(i['sleep'])


if __name__ == '__main__':
    drive = Driver()
    drive.get('http://localhost:8080/camunda/app/tasklist/default/#/login')
    activities = [{
        "act": "send_keys",
        "send_keys": "demo",
        "element_fetch": {
            "type": "xpath",
            "argument": "//input[@placeholder='Username']"
        }
    },
        {
            "act": "send_keys",
            "send_keys": "demo",
            "element_fetch": {
                "type": "xpath",
                "argument": "//input[@placeholder='Password']"
            }
        },
        {
            "act": "click",
            "element_fetch": {
                "type": "xpath",
                "argument": "//button[@type='submit']"
            }
        }]
    drive.run_activities(activities)

