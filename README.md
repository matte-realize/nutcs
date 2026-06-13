# NUTCS Data Service

This is the scraper used to scrape the Northeastern University Transfer Credits website.
Using Selenium, the data has been scraped into JSON format and organized with institutions 
with course data and institutions without course data. The data is then converted using
sqlalchemy and normalized using pandas into PostgreSQL data. Docker is used to containerize
the data set. SQL files are used to query out the data.

## Scraper

To run the scraper, use the terminal and run:

```
python pipeline/scraper.py
```

In PyCharm, click the play button to run the scraper.

## Docker setup and SQL conversion

Before setting up Docker containers, change the parameters of .env.example to suit your 
PostgreSQL database. To set up the Docker containers, run the following command in terminal:

```
docker compose up -d
```

To run the conversion, run the following command in terminal:

``` 
python pipeline/sql_conv.py
```

## Build the search database (for deployment)

The deployed app does **not** use Postgres. It ships a single read-only SQLite
file that the Next.js API queries on Vercel (no database server, no hosting cost).

To (re)build it from the scraped JSON + `genuni.csv`, run:

```
python pipeline/build_db.py
```

This applies the same join + filter logic as `database/cleanup.sql` and writes
`data/nutcs.db` (one denormalized, indexed `courses` table). It uses only the
Python standard library — no `pip install` needed. After rebuilding, commit
`data/nutcs.db` and redeploy.

The Postgres pipeline below (`sql_conv.py`, `csvtosql.py`, Docker) remains for
local analysis and is not part of the Vercel deployment.

## Connect to the database

To connect to the database, we should set up our connection with these settings:

```
Host: localhost
Port: your_local_host_port
Database: your_database_name
User: postgres
Password: your_password

Make sure public schema is checked off.
```

## Debugging

To complete remove the data from the database, run the following commands inside terminal.

```
docker compose down -v
docker system prune -f 
docker volume prune -f
```