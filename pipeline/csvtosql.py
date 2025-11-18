import os
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
CSV_FILE = os.path.join(DATA_DIR, "genuni.csv")

df = pd.read_csv(CSV_FILE)

engine = create_engine(
    f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{LOCAL_PORT}/{POSTGRES_DB}'
)

df.to_sql(
    'institutions_detailed',
    con=engine,
    if_exists='replace',
    index=False
)
