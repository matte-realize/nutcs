import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape():
    driver = webdriver.Chrome()
    driver.get("https://ugadmissions.northeastern.edu/transfercredit/TransferCreditEvaluatedStudent2.asp")
    wait = WebDriverWait(driver, 20)

    wait.until(EC.element_to_be_clickable((By.ID, "button1"))).click()
    print("Clicked 'Proceed to Rules Search' button")

    wait.until(lambda d: len(Select(d.find_element(By.ID, "FICE")).options) > 1)
    institution_select = Select(driver.find_element(By.ID, "FICE"))
    institution_count = len(institution_select.options)

    institutions = {}

    for i in range(1, institution_count):
        institution_select = Select(driver.find_element(By.ID, "FICE"))
        inst_opt = institution_select.options[i]
        inst_name = inst_opt.text.strip()
        institutions[inst_name] = {"departments": []}
        print(f"Institution: {inst_name}")

        institution_select.select_by_index(i)
        time.sleep(0.5)

        wait.until(lambda d: Select(d.find_element(By.ID, "tseg")).options)
        dept_select = Select(driver.find_element(By.ID, "tseg"))

        if len(dept_select.options) <= 1:
            print("  No departments found, skipping.")
            continue

        for j in range(1, len(dept_select.options)):
            dept_name = dept_select.options[j].text.strip()
            institutions[inst_name]["departments"].append(dept_name)
            print(f"  Department: {dept_name}")

    with open("institutions.json", "w", encoding="utf-8") as f:
        json.dump(institutions, f, indent=2, ensure_ascii=False)

    driver.quit()
    print("Department scraping complete!")

if __name__ == "__main__":
    scrape()




