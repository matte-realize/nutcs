import json
import time
import atexit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

start_time = time.time()

def show_runtime():
    end_time = time.time()
    runtime = end_time - start_time
    print(f"\nProgram runtime: {runtime:.4f} seconds")

atexit.register(show_runtime)

def scrape():
    driver = webdriver.Chrome()
    driver.get("https://ugadmissions.northeastern.edu/transfercredit/TransferCreditEvaluatedStudent2.asp")
    wait = WebDriverWait(driver, 20)

    try:
        with open("institutions_and_courses.json", "r", encoding="utf-8") as f:
            institutions = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        institutions = {}

    try:
        with open("institutions_with_nothing.json", "r", encoding="utf-8") as f:
            institutions_with_nothing = set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        institutions_with_nothing = set()

    wait.until(EC.element_to_be_clickable((By.ID, "button1"))).click()
    print("Clicked 'Proceed to Rules Search' button")

    wait.until(lambda d: len(Select(d.find_element(By.ID, "FICE")).options) > 1)
    institution_select = Select(driver.find_element(By.ID, "FICE"))
    all_institutions = [
        (opt.text.strip(), opt.get_attribute("value"))
        for opt in institution_select.options[1:]
    ]

    already_done = set(institutions.keys()) | institutions_with_nothing

    for inst_name, inst_val in all_institutions:
        if inst_name in already_done:
            print(f"Skipping {inst_name} (already scraped or no departments)")
            continue

        institution_select = Select(driver.find_element(By.ID, "FICE"))
        institution_select.select_by_value(inst_val)
        time.sleep(0.1)

        wait.until(lambda d: Select(d.find_element(By.ID, "tseg")).options)
        dept_select = Select(driver.find_element(By.ID, "tseg"))

        if len(dept_select.options) <= 1:
            print(f"{inst_name} has no departments → adding to institutions_with_nothing")
            institutions_with_nothing.add(inst_name)
            with open("institutions_with_nothing.json", "w", encoding="utf-8") as f:
                json.dump(sorted(institutions_with_nothing), f, indent=2, ensure_ascii=False)
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

            if dept_code in institutions[inst_name]["departments"]:
                print(f"  Skipping department {dept_code} (already scraped)")
                continue

            print(f"  Department: {dept_code}")
            dept_courses = {}

            dept_select.select_by_index(j)
            time.sleep(0.1)

            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "//table[@border='1']")))
                table = driver.find_element(By.XPATH, "//table[@border='1']")
                rows = table.find_elements(By.XPATH, ".//tr")

                for row in rows:
                    tds = row.find_elements(By.TAG_NAME, "td")
                    if not tds:
                        continue

                    first_cell = tds[0].text.strip()
                    if not first_cell or first_cell.lower().startswith("transfer course"):
                        continue

                    mapped_courses = [td.text.strip() if td.text.strip() else "" for td in tds[1:]]
                    dept_courses[first_cell] = mapped_courses

                if dept_courses:
                    institutions[inst_name]["departments"][dept_code] = dept_courses
                    print(f"    Saved {len(dept_courses)} courses for {dept_code}")

            except Exception as e:
                print(f"    No courses found for {dept_code}: {e}")

        with open("institutions_and_courses.json", "w", encoding="utf-8") as f:
            json.dump(institutions, f, indent=2, ensure_ascii=False)
        print(f"Saved progress for {inst_name}")

    driver.quit()
    print("Course scraping complete!")


if __name__ == "__main__":
    scrape()