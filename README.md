# She-ra fanfiction database

A front-end for a database created to keep track of the numerous fanfictions recommended on AO3 user [silkarc](https://archiveofourown.org/users/silkarc/)'s discord server.

- Backend: Python using Bottle micro-framework
- Frontend: HTML with CSS from Bootstrap
- Database: PostgreSQL server hosted on Heroku
- Entire site hosted on Heroku

Site found at [shera-fanfiction-database.onrender.com](https://she-ra-fanfiction-database.onrender.com/)

## Running locally

The app needs to be started once and shutdown to allow Postgres to create the database in a Docker Volume.

To get the app working properly, run:

```
git clone https://github.com/odddollar/Shera-fanfiction-database.git
cd Shera-fanfiction-database
docker compose up -d
docker compose down
docker compose up -d
```

Navigate to ```localhost:8080``` to see the site.

To stop the Docker containers, run the following command in the cloned directory:

```
docker compose stop
```