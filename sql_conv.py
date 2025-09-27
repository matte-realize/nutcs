import json
import psycopg2

with open("institutions_and_courses.json", "r", encoding="utf-8") as f:
    institutions = json.load(f)