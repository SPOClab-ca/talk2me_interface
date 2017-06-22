# django_datacollector

## Local setup

1. Install MySQL: https://dev.mysql.com/downloads/
2. Load schema and dummy data:
```
mysql -u Chloe -p mydatabase < talk2me_schema_{MOST_RECENT}.sql
mysql -u Chloe -p mydatabase < user{ID}.sql
mysql -u Chloe -p mydatabase < datacollector_client_{MOST_RECENT}.sql
mysql -u Chloe -p mydatabarse < mysqldump_task{MOST_RECENT}.sql
```
3. Copy the contents of `settings.local.py` into `settings.py` and modify accordingly.
4. Create a virtual environment and install the dependencies.
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
5. Start the Django server: 
`python manage.py runserver`

## Running tests

`python manage.py test datacollector/tests`

## PyLint

`pylint path/to/file`

## Development Cycle

1. Develop feature in separate branch

2. Add unit tests for feature

3. PyLint

4. Push changes to Github

5. Pull request from feature branch to master branch

6. Push changes from Github master branch to colony.cs.toronto.edu master branch