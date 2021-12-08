# Competitive Wikipedia Speedrunning

This repository holds the code for the code for [wikispeedruns.com](https://wikispeedruns.com).

## 1. Prerequisites

- Python 3.7 or greater 
- MySQL Server [Download here](https://dev.mysql.com/downloads/)

## 2. Python Setup

#### Setup Virtual Environment (optional)
We recommend creating a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html)
for running the server. 
```
python -m venv env
```

For Windows:
```
.\env\scripts\activate.bat
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

Once the MySQL server is running, you need to create the database and tables
```
cd scripts
python createDB.py
```

There is also an interactive script (follow the instructions in the scripts)
to create a configuration file and set up and admin account.
```
cd scripts
python configure.py
```

## 4. Running

#### (Optional) Set environment variables for development
Set the environment variable `FLASK_ENV` in whaterver command prompt you use plan to use
for running the flask server.

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

