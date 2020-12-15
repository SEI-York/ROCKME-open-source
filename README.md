# ROCK ME

_An Outcome Mapping tool from SEI-York._

![ROCK](rock_me/static/images/logo.png)

_Regeneration and Optimisation of Cultural heritage in creative and Knowledge cities_

This is implementation of DeCart for the EU [ROCK project](https://rockproject.eu/).

ROCK develops an innovative, collaborative and circular systemic approach for
regeneration and adaptive reuse of historic city centres. Implementing a
repertoire of successful heritage-led regeneration initiatives, ROCK test the
replicability of the spatial approach and of successful models addressing the
specific needs of historic city centres.  ROCK is a Horizon 2020 funded project. 


See the official website [about](https://rockproject.eu/about) page for more
details.

## Setting up a Development environment
Modify the `.env.example` file according to your environment and rename it to `.env`.
Then place it in the root of the repository (next to `manage.py`).

Next, create your virtual environment and install the site dependencies:
```bash
$ make os_install  # OPTIONAL!: On Ubuntu this will install the required packages
                   #            for running DeCart locally. See scripts/os-depts.apt
                   #            for details if you need to do a manual install.
                   #            You DO NOT need to run this if you already have
                   #            python3.6 and Postgres installed.
$ make install
```

Next, set up the development database name and password. These are used by
`ROCK_ME` to access the development database when working locally. To set up the
database, first ensure that Postgres is installed (run `make os_install` if
not), then type the following to get an interactive postgres shell:

```bash
$ sudo su - postgres
$ psql
```

Once you are at the psql prompt, run the following commands to set up the
development database:

```sql
CREATE DATABASE <db name from .env>;
CREATE USER <username from .env> WITH PASSWORD '<password from .env>';
ALTER ROLE <username from .env> SET client_encoding TO 'utf8';
ALTER ROLE <username from .env> SET default_transaction_isolation TO 'read committed';
ALTER ROLE <username from .env> SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE <db name from .env> TO <username from .env>;
```

You should see a confirmation message following each command. If everything ran
OK then you can exit using `\q` and then  get back to your normal shell by
typing `exit`.

Finally, you need to create your site superuser and initialise the dev database
structure within Django:

```bash
$ cd <rock_me directory>
$ make migrations
$ make migrate
$ make superuser  # you will be prompted for details
$ make seed_db
```

From this point on, you should have a functional (but blank) database to work
with.
