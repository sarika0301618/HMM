import csv
import json
import time
import undetected_chromedriver as uc
from openpyxl import Workbook
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
)

s = Service(ChromeDriverManager().install())
driver = uc.Chrome(service=s)
driver.maximize_window()

url = 'https://www.hmm21.com/e-service/general/trackNTrace/TrackNTrace.do'
driver.get(url)

input_bl = driver.find_element(By.XPATH, '//input[@name="srchBlNo1"]')
input_bl.send_keys("TSNA10098200")# hardcoded as it is only container number
retrieve = driver.find_element(By.XPATH, '//button[contains(text(), "Retrieve")]')
retrieve.click()
time.sleep(10)


# Extracting location data
locations = driver.find_elements(By.XPATH, '//div[@class="location"]')
location_data = {}

if len(locations) >= 2:
    location_data["origin"] = locations[0].text
    location_data["destination"] = locations[-1].text
    transitions = driver.find_elements(By.XPATH, '//ul[@class="progress-bar"]/li/div[@class="text"]')
    location_data["transitions"] = [transition.text.strip() for transition in transitions if transition.text.strip()]
else:
    print("Insufficient location data found!")


# Function to extract table data dynamically
def extract_table_data(table_xpath):
    table = driver.find_element(By.XPATH, table_xpath)
    headers = [header.text.strip() for header in table.find_elements(By.XPATH, './/thead/tr/th') if header.text.strip()]
    rows = table.find_elements(By.XPATH, './/tbody/tr')
    table_data = []

    for row in rows:
        row_data = {}
        cells = row.find_elements(By.XPATH, './/td')
        for i in range(len(cells)):
            cell_text = cells[i].text.strip()
            if i < len(headers):
                row_data[headers[i]] = cell_text if cell_text else None
        table_data.append(row_data)
    return table_data


# Extracting all tables
tables_data = {
    "cntr_table": extract_table_data('//div[@id="cntrChangeArea"]//table'),
    "container_table": extract_table_data('//div[@id="containerStatus"]//table'),
    "Current_Location_table": extract_table_data('//div[text()="Current Location"]/following::table[1]'),
    "Vessel_Movement_table": extract_table_data('//div[text()="Vessel Movement"]/following::table[1]'),
    "Customs_Status_table": extract_table_data('//div[text()="Customs Status"]/following::table[1]'),
    "Empty_Container_Return_Location_table": extract_table_data(
        '//div[text()="Empty Container Return Location"]/ancestor::table'),
    "shipmentProgress_table": extract_table_data('//div[@id="shipmentProgress"]//table')
}

final_data = {
    "location_data": location_data,
    "tables_data": tables_data
}

final_json = json.dumps(final_data, indent=4)

print(final_json)

with open("shipment_data.json", "w", encoding="utf-8") as json_file:
    json_file.write(final_json)

print("Data saved to shipment_data.json successfully!")