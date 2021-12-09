# from browserupproxy import Server
from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os
import json
import datetime
import time

def clear_cache(driver):
    driver.get('chrome://settings/clearBrowserData')
    time.sleep(0.5)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB * 7) # send right combination
    actions.perform()
    actions.send_keys(Keys.ENTER) # confirm
    actions.perform()

bupFilePath = "C:/Users/TL/AppData/Local/Microsoft/WindowsApps/browsermob-proxy-2.1.4/bin/browsermob-proxy"
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

jsonDir = "Chrome jsonFiles" + datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")

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
msg = "Session started, Browser = Chrome, Time = " + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + "\n"
f.write(msg)

options = webdriver.ChromeOptions()
options.add_argument('ignore-certificate-errors')
options.add_argument('--proxy-server={}'.format(proxy.proxy))

driver = webdriver.Chrome(chrome_options=options)
driver.get("https://google.com")
clear_cache(driver)
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

    clear_cache(driver)
    driver.delete_all_cookies()

msg = "Session ended at " + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + "\n\n"
print(msg)
f.write(msg)
driver.quit()
proxy.close()
server.stop()
f.close()
