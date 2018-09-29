# django_datacollector

## Software requirements

- MySQL: https://dev.mysql.com/downloads/
This is the version I have: 
```mysql --version
Ver 14.14 Distrib 5.7.18, for macos10.12 (x86_64)
```


- Python: This is the version I have: 
```python --version
Python 2.7.10
```

- For managing Python libraries and dependencies, I recommend using a package manager like `pip` or `conda`

## Set up database:
- Run mysql.
- Load schema:
```
mysql -u [USERNAME] -p [DATABASE_NAME] < [SCHEMA_FILE].sql
mysql -u [USERNAME] -p [DATABASE_NAME] < [CLIENT_FILE].sql
mysql -u [USERNAME] -p [DATABASE_NAME] < [TASK_FILE].sql
```

- Copy the contents of `settings.local.py` into `settings.py` and modify accordingly. Change the database name, username, and password so that it matches your local setup.
- Copy the contents of `wsgi.local.py` into `wsgi.py` and modify accordingly.
- Copy the contents of `crypto.local.py` into `crypto.py` and set `HASH_PEPPER` to the hash of your choice.

## Installing dependencies
- Create a virtual environment and install the dependencies. 
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the application
- Load your virtual environment: `source venv/bin/activate`
- Start the Django server: `python manage.py runserver`


## Testing, syntax, etc (optional)
- When adding a new feature, add a unit test and make sure none of the previous tests are broken. To run tests:
`python manage.py test datacollector/tests`
- Use PyLint to make sure proper Python syntax is used:
`pylint path/to/file`

## Pushing changes to the server
- Merge new changes to the `master` branch.
- Pull changes from Github master branch to colony.cs.toronto.edu master branch
- On the colony.cs.toronto.edu server, restart the web application: `~/site/bin/apache2ctl restart` [can only be done by those who have access to the server]
