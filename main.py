import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Firefox()

driver.get("https://ugadmissions.northeastern.edu/transfercredit/TransferCreditevaluatedstudent2.asp")
wait = WebDriverWait(driver, 10)

'Proceed to Rules Search button input'
ptrs = driver.find_element(By.ID, "button1")

ptrs.click()

'Institution options HTML'
sio = Select(driver.find_element(By.ID, "FICE"))

sio_options = sio.options

option_values = []
institution_and_courses = []
for option in sio_options:
    id = option.get_attribute("value")
    institution_name = option.get_attribute("innerHTML")
    option_values.append(id)
    institution_and_courses.append(institution_name)
    print(institution_name)

with open('options.json', 'w') as f:
    json.dump(option_values, f, indent=4)

with open('institution_and_courses.json', 'w') as f:
    json.dump(institution_and_courses, f, indent=4)

for value in option_values:
    select_element = wait.until(
        EC.presence_of_element_located((By.ID, "FICE"))
    )
    select = Select(select_element)
    select.select_by_value(value)