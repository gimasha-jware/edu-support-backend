from app import create_app
from app.utils.db_utills import create_database, create_tables, alter_columns, create_default_users, apply_schema_updates

create_database()
create_tables()
alter_columns()
create_default_users()
apply_schema_updates()

app = create_app('development')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)