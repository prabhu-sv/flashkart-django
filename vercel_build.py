import os
import django
from django.core.management import call_command
from django.db import connection

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flashkart.settings')
django.setup()

# Ensure database connection
with connection.cursor() as cursor:
    cursor.execute("SELECT 1")

# Run migrations
print("Running migrations...")
call_command('migrate', '--noinput')

# Create necessary tables if they don't exist
with connection.cursor() as cursor:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS django_session (
            session_key varchar(40) NOT NULL PRIMARY KEY,
            session_data text NOT NULL,
            expire_date timestamp with time zone NOT NULL
        );
    """)

# Collect static files
print("Collecting static files...")
call_command('collectstatic', '--noinput') 