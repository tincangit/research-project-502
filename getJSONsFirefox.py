from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import os
import json
import datetime
import time
import psutil


def terminate_browsermob_processes(self):
    self._browsermob_proxy.close()
    self._browsermob_server.stop()

    # Find BrowserMob-Proxy processes that may still be alive and kill them
    for process in psutil.process_iter():
        try:
            process_info = process.as_dict(attrs=['name', 'cmdline'])
            if process_info.get('name') in ('java', 'java.exe'):
                for cmd_info in process_info.get('cmdline'):
                    if cmd_info == '-Dapp.name=browsermob-proxy':
                        process.kill()
        except psutil.NoSuchProcess:
            pass

dialog_selector = 'vbox.dialogOverlay:nth-child(1) > vbox:nth-child(1) > browser:nth-child(2)'

def get_clear_site_data_button(driver):
    return driver.find_element_by_css_selector('#clearSiteDataButton')


def get_clear_site_data_dialog(driver):
    return driver.find_element_by_css_selector(dialog_selector)

def clear_firefox_cache(driver, timeout=10):
    driver.get('about:preferences#privacy')
    wait = WebDriverWait(driver, timeout)

    # Click the "Clear Data..." button under "Cookies and Site Data".
    wait.until(get_clear_site_data_button)
    get_clear_site_data_button(driver).click()

    # Accept the "Clear Data" dialog by clicking on the "Clear" button.
    wait.until(get_clear_site_data_dialog)
    elem = driver.switch_to.active_element
    elem.send_keys(Keys.ENTER)

    # Accept the confirmation alert.
    wait.until(EC.alert_is_present())
    alert = Alert(driver)
    alert.accept()

bupFilePath = #path to BUP
server = Server(bupFilePath)
server.start()
proxy = server.create_proxy()

#parse sites.txt file
try:
    f = open("sites.txt", "r")
except:
    print("Error, cannot open sites.txt, quitting")
    quit()

sitesList = list()
lineCount = -1
for line in f:
    lineCount = lineCount + 1
    try:
        x = line.split(",")
        sitesList.append((x[0].strip(), x[1].strip()))
    except:
        print("Error, cannot parse sites.txt, issue at line index" + str(lineCount))
        f.close()
        quit()

f.close()
numSites = len(sitesList)

jsonDir = "Firefox jsonFiles" + datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")

#create or go to directory that will store the json files
try:
    os.chdir(jsonDir)
except:
    os.mkdir(jsonDir)
    os.chdir(jsonDir)

server = Server(bupFilePath, options={'captureHeaders': True})
server.start()
proxy = server.create_proxy()
siteCount = 0


f = open("log.txt", "a")
msg = "Session started, Browser = Firefox, Time = " + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + "\n"
f.write(msg)

profile = webdriver.FirefoxProfile()
profile.set_proxy(proxy.selenium_proxy())
driver = webdriver.Firefox(firefox_profile=profile)

driver.get("https://www.google.com/")

clear_firefox_cache(driver)
driver.delete_all_cookies()

for site in sitesList:
    siteCount = siteCount + 1
    proxy.new_har(site[1], options={'captureHeaders': True})

    timeStart = time.perf_counter()
    msg = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + ": "
    f.write(msg)
    try:
        driver.get(site[0])
    except:
        msg = "Error, problem opening site index " + str(siteCount) + ", url: " + site[0] + "\n"
        print(msg)
        f.write(msg)
        continue

    try:
        with open(site[1] + " " + datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S") + '.json', 'w') as har_file:
            json.dump(proxy.har, har_file)
    except:
        msg = "Error, problem dumping json site index " + str(siteCount) + ", url: " + site[0] + "\n"
        print(msg)
        f.write(msg)
        continue

    print("done with " + site[1] +", " + str(siteCount) + "/" + str(numSites))
    timeStop = time.perf_counter()
    msg = site[1] + " " + site[0] + " " + "{:.3f}".format(timeStop-timeStart) + " seconds \n"
    f.write(msg)

    clear_firefox_cache(driver)
    driver.delete_all_cookies()

msg = "Session ended at " + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + "\n\n"
print(msg)
f.write(msg)
driver.quit()
proxy.close()
server.stop()
f.close()
