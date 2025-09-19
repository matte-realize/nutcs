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

    for i in range(1, min(institution_count, 2750)):
        institution_select = Select(driver.find_element(By.ID, "FICE"))
        inst_opt = institution_select.options[i]
        inst_name = inst_opt.text.strip()
        inst_val = inst_opt.get_attribute("value")

        institution_select.select_by_index(i)
        time.sleep(0.001)

        wait.until(lambda d: Select(d.find_element(By.ID, "tseg")).options)
        dept_select = Select(driver.find_element(By.ID, "tseg"))

        if len(dept_select.options) <= 1:
            print(f"Skipping {inst_name} (no departments found)")
            continue

        institutions[inst_name] = {
            "institution_value": inst_val,
            "departments": {}
        }

        print(f"Institution: {inst_name}")

        for j in range(1, len(dept_select.options)):
            dept_select = Select(driver.find_element(By.ID, "tseg"))
            dept_opt = dept_select.options[j]
            dept_code = dept_opt.text.strip()

            print(f"  Department: {dept_code}")
            dept_courses = {}

            dept_select.select_by_index(j)
            time.sleep(0.001)

            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//table[@border='1']")))
                table = driver.find_element(By.XPATH, "//table[@border='1']")
                rows = table.find_elements(By.XPATH, ".//tr")

                for row in rows:
                    tds = row.find_elements(By.TAG_NAME, "td")
                    if not tds:
                        continue

                    first_cell = tds[0].text.strip()
                    if not first_cell:
                        continue
                    if first_cell.lower().startswith("transfer course"):
                        continue

                    mapped_courses = [td.text.strip() if td.text.strip() else "" for td in tds[1:]]
                    dept_courses[first_cell] = mapped_courses

                if dept_courses or len(rows) > 0:
                    institutions[inst_name]["departments"][dept_code] = dept_courses

            except Exception as e:
                print(f"    No courses found for {dept_code}: {e}")

            if dept_courses:
                institutions[inst_name]["departments"][dept_code] = dept_courses

    with open("institutions_and_courses.json", "w", encoding="utf-8") as f:
        json.dump(institutions, f, indent=2, ensure_ascii=False)

    driver.quit()
    print("Course scraping complete!")

if __name__ == "__main__":
    scrape()
