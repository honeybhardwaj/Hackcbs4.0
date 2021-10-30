from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from pynput.keyboard import Key, Controller
import time
import getpass
from selenium.webdriver.common.alert import Alert
class JoinMeet:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        opt = Options()
        opt.add_argument("--start-maximized")
        opt.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.geolocation": 1,
            "profile.default_content_setting_values.notifications": 1
        })
        opt.add_experimental_option('excludeSwitches',['test-type'])
        s = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=s, options=opt)

    def google_login(self):
        self.driver.get(
            'https://accounts.google.com/ServiceLogin?hl=en&passive=true&continue=https://www.google.com/&ec=GAZAAQ')

        # input Gmail
        self.driver.find_element_by_id("identifierId").send_keys(self.email)
        self.driver.find_element_by_id("identifierNext").click()
        self.driver.implicitly_wait(10)

        # input Password
        self.driver.find_element_by_xpath(
            '//*[@id="password"]/div[1]/div/div[1]/input').send_keys(self.password)
        self.driver.implicitly_wait(10)
        self.driver.find_element_by_id("passwordNext").click()
        self.driver.implicitly_wait(10)

        # go to google home page
        self.driver.get('https://google.com/')
        self.driver.implicitly_wait(100)

    def turn_off_mic(self):
        time.sleep(2)
        # turn off mic
        self.driver.find_element_by_xpath(
            '/html/body/div/c-wiz/div/div/div[9]/div[3]/div/div/div[3]/div/div/div[1]/div[1]/div/div[4]/div[1]/div/div/div').click()
        self.driver.implicitly_wait(3000)

        # turn off camera
        time.sleep(2)
        self.driver.find_element_by_xpath(
            '/html/body/div/c-wiz/div/div/div[9]/div[3]/div/div/div[3]/div/div/div[1]/div[1]/div/div[4]/div[2]/div/div').click()
        self.driver.implicitly_wait(3000)

    def ask_to_join(self):
        # Ask to Join meet
        time.sleep(5)
        self.driver.implicitly_wait(2000)
        self.driver.find_element_by_css_selector(
            'div.uArJ5e.UQuaGc.Y5sE8d.uyXBBb.xKiqt').click()
        # Ask to join and join now buttons have same xpaths
        # time.sleep(5)
        #attendees = driver.find_element_by_css_selector('div.uGOf1d')
        #print("no. of attendees are :",attendees.get_attribute("innerHTML"))

    def join_meet(self, meeting_link):
        # login to google account
        self.google_login()
        self.driver.get(meeting_link)
        self.turn_off_mic()
        attendees = self.driver.find_element_by_xpath(
            '/html/body/div[1]/c-wiz/div/div/div[9]/div[3]/div/div/div[3]/div/div/div[2]/div/div[1]/div[1]/div[2]/div[2]')
        print(attendees.text)
        self.ask_to_join()

    def record_meeting(self):
        time.sleep(2)
        self.driver.maximize_window()
        self.driver.execute_script(
            '''window.open("https://meet.google.com/cxi-egxi-sor","_blank");''')
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(2)
        self.turn_off_mic()
        self.ask_to_join()
        self.driver.find_element_by_xpath('/html/body/div[1]/c-wiz/div[1]/div/div[9]/div[3]/div[10]/div[2]/div/div[5]/div/div[2]/div[1]/span/button/i').click()
        self.driver.find_element_by_xpath('/html/body/div[3]/ul/li[3]').click()
        time.sleep(2)
        keyboard = Controller()
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)

        keyboard.press(Key.down)
        keyboard.release(Key.down)

        keyboard.press(Key.down)
        keyboard.release(Key.down)

        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

        self.driver.find_element_by_xpath('/html/body/div[1]/c-wiz/div[1]/div/div[9]/div[3]/div[10]/div[2]/div/div[6]/div/div[3]/div[1]/span/button/i').click()
        time.sleep(2)
        self.driver.find_element_by_xpath('/html/body/div[4]/ul/li[2]/span[3]').click()
        time.sleep(2)
        self.driver.find_element_by_xpath('/html/body/div[1]/c-wiz/div[1]/div/div[9]/div[3]/div[4]/div[2]/div[3]/div/div[2]/div/div/p/div/div/button').click()
        time.sleep(2)
        self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div[2]/div[3]/div/div[2]/span/span').click()
        

if __name__ == "__main__":
    obj = JoinMeet("email","pass")
    obj.join_meet("https://meet.google.com/uxp-mgmo-gxc")
    obj.record_meeting()
    