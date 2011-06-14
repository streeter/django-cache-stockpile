#!/usr/bin/env python
import sys
from os.path import dirname, abspath, join

from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASE_ENGINE='sqlite3',
        
        # Uncomment below to run tests with mysql
        #DATABASE_ENGINE='django.db.backends.mysql',
        #DATABASE_NAME='stockpile_test',
        #DATABASE_USER='stockpile_test',
        #DATABASE_HOST='/var/mysql/mysql.sock',
        INSTALLED_APPS=[
            'stockpile',
        ],
        ROOT_URLCONF='',
        DEBUG=False,
        STOCKPILE_TESTING=True,
    )

from django.test.simple import run_tests

def runtests(*test_args):
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()
    
    if not test_args:
        test_args = ['stockpile']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    failures = run_tests(test_args, verbosity=0, interactive=True)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])