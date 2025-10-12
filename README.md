# NUTCS Scraper

This is the scraper used to scrape the Northeastern University Transfer Credits website.
Using Selenium, the data has been scraped into JSON format and organized with institutions 
with course data and institutions without course data. The data is then converted using
sqlalchemy and normalized using pandas into PostgreSQL data. Docker is used to containerize
the data set.

## Scraper

To run the scraper, use the terminal and run:

```
python main.py
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
python sql_conv.py
```

## Connect to the database

To connect to the database, we should set up our connection with these settings:

```
Host: localhost
Port: your_local_host_port
Database: your_database_name
User: postgres
Password: your_password

NMake sure public schema is checked off.
```

## Debugging

To complete remove the data from the database, run the following commands inside terminal.

```
docker compose down -v
docker system prune -f 
docker volume prune -f
```