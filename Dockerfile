FROM python:3.11-slim

WORKDIR /app

COPY ../pipeline/requirements.txt ../pipeline/requirements.txt

RUN pip install --no-cache-dir -r ../pipeline/requirements.txt

COPY . .

RUN mkdir -p /app/data

CMD ["sh", "-c", "python pipeline/scraper.py && python pipeline/convert_to_sql.py"]
