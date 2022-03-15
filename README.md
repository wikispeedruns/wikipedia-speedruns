# Competitive Wikipedia Speedrunning

This repository holds the code for [wikispeedruns.com](https://wikispeedruns.com).

## 1. Prerequisites

- Python 3.7 or greater
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

#### Install Requirements
Then install the requirements (with your virtual environment activated)
```
pip install -r requirements.txt
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

#### Start the server
From the top level directory
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