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