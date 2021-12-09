from selenium import webdriver
import os
driver = webdriver.Firefox()
driver.get("https://www.calgary.ca/election/information-for-voters/candidates.html?district=&officeType=separateSchoolTrustee")

elems = driver.find_elements_by_css_selector("table > tbody > tr")
for elem in elems:
    name = elem.find_element_by_css_selector("td:nth-of-type(3)").text
    elem2 = elem.find_element_by_css_selector("td:nth-of-type(5)")
    labels = elem.find_elements_by_class_name("label")
    if (len(labels) > 0):
        if labels[0].text == "Website:":
            msg = elem.find_element_by_class_name("detail").text
            msg = "http://" + msg + "," + name
            print(msg)

