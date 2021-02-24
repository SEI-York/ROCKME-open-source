# ROCK ME

ROCKME is an innovative MREL tool for the Monitoring, Reporting, Evaluation of the impacts of the outcome of  actions connected with large scale EU demonstration projects and for learning from the experience. It is used by city decision makers, city policy makers, leaders in private enterprises and in not-for-profit organisations to define KPIs and to monitor, report on, evaluate the impact of the outcome of actions from conception stage to implementation and finally to post implementation evaluation on the long term.

The tool was imagined, conceptualised and designed by Corrado Topi and Howard Cambridge at the Stockholm Environment Institute Research Centre at the University of York. The lead software developer was Guozhong “Douglas” Wang and Innes Anderson-Morrison and David Green were part of the team. The tool is based on Outcome Mapping, and was developed as part of the EC funded large scale demonstrator project ROCK.   

ROCK develops an innovative, collaborative and circular systemic approach for
regeneration and adaptive reuse of historic city centres. Implementing a
repertoire of successful heritage-led regeneration initiatives, ROCK test the
replicability of the spatial approach and of successful models addressing the
specific needs of historic city centres.  ROCK is a Horizon 2020 funded project. 

See the official website [about](https://rockproject.eu/about) page for more
details.

## How to quote ROCKME

If you ever need to quote the tool in papers or reports the correct way of reporting is:

Topi, C., Cambridge, H., Wang, G., Anderson-Morris, I., Green D., 2021, ROCKME: A monitoring reporting evaluation and leanring tool for large scale EU demostration projects. Stockholm Environment Institute at the University of York. York. UK. https://github.com/SEI-York/ROCKME-open-source/   

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