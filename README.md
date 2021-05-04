# She-ra fanfiction database

A front-end for a database created to keep track of the numerous fanfictions recommended on AO3 user [silkarc](https://archiveofourown.org/users/silkarc/)'s discord server.

- Backend: Python using Bottle micro-framework
- Frontend: HTML with CSS from Bootstrap
- Database: PostgreSQL server hosted on Heroku
- Entire app hosted on Heroku

Site found at [shera-fanfiction-database.herokuapp.com](https://shera-fanfiction-database.herokuapp.com/)

## Running locally

On the off chance someone wants to run this locally, ensure Docker is installed and added to the system ```PATH``` (if on Windows) and the Docker service is running.

The app need to be started once and shutdown to allow Postgres to create the database in a Docker Volume. This initial bootup will cause an error, but this is ok. 

Run:

```
docker compose up -d
docker compose down
docker compose up -d
```

Navigate to ```localhost:8080``` to see the site.
