import time
import selenium
import selenium.common
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import pprint

# To Scrape Row Data

def get_info(sect,feature):
    lists_of_list = sect.find_elements(By.CSS_SELECTOR,'.cgrid .clist')
    # for ind,lists in enumerate(lists_of_list):
    titles = [title.find_element(By.CSS_SELECTOR,".clist__title").text.lower() for title in lists_of_list]
    try:
        the_index = titles.index(feature)
        the_element = lists_of_list[the_index]
        the_element = the_element.find_elements(By.CSS_SELECTOR,".clist__item")
        return ", ".join([element.text for element in the_element])

    except ValueError:
        return ""

class number_of_sections(object):
    def __init__(self, locator, num):
        self.locator = locator
        self.num = num

    def __call__(self, driver):
        element = driver.find_elements(*self.locator)

        if len(element) == self.num:
            return self.num
        else:
            return False

class element_has_text(object):
    def __init__(self, locator, attribute):
        self.locator = locator
        self.text = attribute

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        if element.text.lower() == self.text:
            return self.text
        else:
            return False

def load_all(driver):
    #Check for 'load more' button and scroll functionality
    locator = (By.CSS_SELECTOR, ".facetwp-load-more.filters__load-more.button--outline-default.button--medium")
    the_text = "load more"
    more_button_present = True  
    while more_button_present:
        try:
            try:
                WebDriverWait(driver, 10).until(element_has_text(locator, the_text))
                load = driver.find_element(By.CSS_SELECTOR, ".facetwp-load-more.filters__load-more.button--outline-default.button--medium")
                driver.execute_script('arguments[0].scrollIntoView(true)', load)
                time.sleep(4)
                load.click()
                more_button_present = driver.find_element(*locator).is_displayed()  # Check if button is still displayed after click
            except selenium.common.exceptions.TimeoutException:
                more_button_present = False  # Break if timeout occurs
        except selenium.common.exceptions.NoSuchElementException:
            more_button_present = False  # Break if element not found

    #To capture the last few companies
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(2)


    #To navigate to row elements
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(2)

def capture_rows(driver,data):
    rows = driver.find_elements(By.CSS_SELECTOR,"tr.aos-init.aos-animate")
    print(len(rows))
    #Iterate over each row
    for ind,row in enumerate(rows):
        wait = WebDriverWait(driver, 20)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'tr.aos-init.aos-animate')))

        # To Scrape Company_names
        cname = row.find_element(By.TAG_NAME, 'th').text
        data["name"].append(cname)
        # print(f"Name : {data["name"]}")

        #To Scrape Company Stage
        cstage = row.find_element(By.CSS_SELECTOR,'td.u-lg-hide').text
        data["stage"].append(cstage)
        # print(f"Stage : {data['stage']}")
        
        # wait_button.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'span.company-listing__toggle')))
        d = row.find_element(By.CSS_SELECTOR,'span.company-listing__toggle')
        driver.execute_script('arguments[0].scrollIntoView(true)', row)
        time.sleep(2)
        d.click()
        wait = WebDriverWait(driver, 20)
        wait.until(number_of_sections((By.CSS_SELECTOR,'section.company'),ind+1))

        company_section = driver.find_elements(By.CSS_SELECTOR,'section.company')[-1]
        #To Scrape Company URL
        curl = company_section.find_element(By.CSS_SELECTOR, 'a.button.button--outline-light.button--small')
        curl = curl.get_attribute('href')
        data["url"].append(curl)
        # print(f"Url :{data["url"]}")

        #To Scrape Company Category
        cats = company_section.find_elements(By.CSS_SELECTOR,'a.pill.pill--facet.pill--active.pill--passive')
        cats = ", ".join([cat.text for cat in cats])
        data["category"].append(cats)
        # print(f"Category : {data["category"]}")

        #To Scrape Company Milestones
        milestones = get_info(company_section,"milestones")
        data["milestones"].append(milestones)
        # print(f"Milestone : {data["milestones"]}")
        
        #To Scrape Company Team
        team = get_info(company_section,"team")
        data["team"].append(team)
        # print(f"Team : {data["team"]}")

        #To Scrape Company Partners
        partner = get_info(company_section,"partner")
        data["partners"].append(partner)
        # print(f"Partners : {data["partners"]}")

        #To Scrape Top Company Jobs
        elements = company_section.find_elements(By.CSS_SELECTOR,'.u-d-flex.u-flex-column.u-gy-5 .clist')
        found_job = False
        for element in elements:
            if element.find_element(By.CSS_SELECTOR,".clist__title").text.lower() == "jobs":
                found_job = True
                job_elements = element.find_elements(By.CSS_SELECTOR,".clist__item")
                job = [element.text for element in job_elements]
                job = ", ".join(job)
                data["jobs"].append(job)
                break
        if not found_job:
            data["jobs"].append("")
        # print(f"Job : {data["jobs"]}")
        # print("\n")
        d.click()
        time.sleep(2)
    return data

def store_companies(filename):
    driver = webdriver.Chrome()
    #Dictionary to hold data
    url = "https://www.sequoiacap.com/our-companies/#all-panel"
    driver.get(url)

    #To Increase PageView to "FullScreen"
    driver.maximize_window()

    SequoiaData = {
        "name": [],
        "url": [],
        "stage": [],
        "category": [],
        "milestones": [],
        "team": [],
        "jobs": [],
        "partners": []
    }
    load_all(driver)
    SequoiaData = capture_rows(driver,SequoiaData)
    SequoiaData = pd.DataFrame(SequoiaData)
    SequoiaData.to_csv(filename,index=False)

filename = 'sequoia_data.csv'

store_companies(filename)