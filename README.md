# Competitive Wikipedia Speedrunning

This repository holds the code for [wikispeedruns.com](https://wikispeedruns.com).

## 1. Prerequisites

- Python 3.7 or greater
- Node
- MySQL Server 8 [Download here](https://dev.mysql.com/downloads/)

## 2. Python Setup

#### Setup Virtual Environment (optional)
We recommend creating a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html)
for running the server.
```
python -m venv env
```

For Windows Powershell:
```
./env/Scripts/Activate.ps1
```

For Linux
```
source env/bin/activate
```

#### Install Python Requirements
Then install the requirements (with your virtual environment activated)
```
pip install -r requirements.txt
```

#### Install npm packages
Then install the requirements (with your virtual environment activated)
```
npm install
```


## 3. App Setup
There are a number of scripts to help setup the web app in [scripts](scripts).

Once the MySQL server is running, you will need to create an account. By
default we assume an account `user` with no password (see
[`default.json`](config/default.json)). If you wish to use a different MySQL
setup, you can create `prod.json` with the relevant MySQL fields in
[`config`](config) which will override `default.json`.

Then create the database and tables using the provided script.
```
cd scripts
python create_db.py
```

There is also an interactive script (with instructions in the scripts) which
can be used to set up a local admin account. Through the admin account,
prompts can be managed through `/manage`.
```
cd scripts
python create_admin_account.py
```

(Optional) Finally, there is also a script to populate the database with data
for local development
```
cd scripts
python populate_db.py
```
## 4. Running

#### (Optional) Set environment variables for development
Set the environment variable `FLASK_ENV` in whaterver command prompt you use plan to use
for running the flask server. This will allow the local instance to reload automatically
when files are changed.

For example, in Linux
```
export FLASK_ENV="development"
```

Or in Windows Powershell
```
$env:FLASK_ENV="development"
```

#### Start the frontend build
From the top level directory
```
npm run start
```

#### Start the server
In a separate shell, from the top level directory
```
flask run
```

## 5. Testing Locally

In order to run the [tests](test) locally, you need to create another account in MYSQL
with username `testuser` and password `testpassword`. Our tests are configured to run
against this account by default.

Then, simply run pytest from the `test` directory.
```
cd test
pytest
```

Note that these tests are also run in Docker upon making a PR using Github workflows.
In the future we may setup docker to run tests as well.


## (Optional) Scraper Setup

The asynchronous task queue for scraper tasks are supported by 2 extra tools, celery
and redis. Celery is installed as a python requirement, but redis (https://redis.io/)
needs to be installed and run separately (similar to the SQL server, see website
for instructions). The scraper task_queue also requires the `scraper_graph`,
which can be downloaded locally (contact one of the maintainers)

Rather than computing the path as part of the request, which freezes up the server,
flask passes off the scraper tasks to another process managed by celery (and
communicates through redis). These tasks are defined using python decorators, examples
of which can be seen [here](https://github.com/wikispeedruns/wikipedia-speedruns/blob/scraper_task_queue/apis/scraper_api.py).

#### Windows setup

Unfortunately, neither celery nor redis are supported on windows. So if you have
a windows development machine, you will have to run the server through WSL. Note
that if you want to keep your windows MySQL instance, you need to figure out
which port the host windows machine is exposed on in WSL. See [this Stack Overflow
post](https://superuser.com/questions/1536619/connect-to-mysql-from-wsl2). Note
that this changes everytime WSL is restarted.

