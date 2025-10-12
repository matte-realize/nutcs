import os
import json
import time
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
LOCAL_PORT = os.getenv('LOCAL_PORT')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "../data")
COURSES_JSON = os.path.join(DATA_DIR, "institutions_and_courses.json")

print("Awaiting PostgreSQL...")
time.sleep(8)

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{LOCAL_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)

with open(COURSES_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

rows = []
for institution_name, institution_data in data.items():
    departments = institution_data.get("departments", {})
    for dept_name, courses in departments.items():
        for course_code, course_info in courses.items():
            row = {
                "institution_name": institution_name,
                "department": dept_name,
                "course_code": course_code,
                "transfer_credit": course_info[0],
                "effective_date": course_info[1],
                "nucore": course_info[2],
                "nupath": course_info[3]
            }
            rows.append(row)

df = pd.DataFrame(rows)

df.to_sql("NUTCS_RAW", engine, schema="public", if_exists="replace", index=False)

print("Table created successfully!")
