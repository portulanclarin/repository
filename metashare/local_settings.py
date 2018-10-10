# coding=utf-8
from os.path import abspath, realpath, dirname, join
import os
import tempfile

print "CODE_DIR=" + repr(os.environ["CODE_DIR"])
print "DATA_DIR=" + repr(os.environ["DATA_DIR"])

CODE_DIR = os.getenv("CODE_DIR", abspath(realpath(join(dirname(__file__), '..'))))
DATA_DIR = os.getenv("DATA_DIR", abspath(join(CODE_DIR, '..', 'data')))
LOGS_DIR = os.getenv("LOGS_DIR", abspath(join(CODE_DIR, '..', 'logs')))
LOCK_DIR = os.getenv("LOCK_DIR", abspath(join(CODE_DIR, '..', 'lock')))

# The URL for this META-SHARE node django application.  Do not use trailing /.
# This URL has to include DJANGO_BASE (without its trailing /)!
DJANGO_URL = 'http://portulanclarin.net'

# Name of the resource collection harvested through OAI-PMH.
# This name is used for the Collection facet in the VLO (http://vlo.clarin.eu/).
COLLECTION_DISPLAY_NAME = "PORTULAN / CLARIN"

# TSV file containing the metadata PID for each resource PID.
# This file should have a column named "MD PID" which contains the metadata PID
# for any resource IDs present in any other column(s) of the same line.
PIDDATA_FILENAME = join(DATA_DIR, 'resource-pids.tsv')

# The base path under which django is deployed at DJANGO_URL.  Use trailing /.
# Do not use leading / though.  Leave empty if META-SHARE is deployed directly
# under the given DJANGO_URL.
DJANGO_BASE = ''

# Required if deployed with lighttpd.
FORCE_SCRIPT_NAME = ''

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
USE_L10N = True
LANGUAGE_CODE = 'en-us'

# Path to the local storage layer path used for persistent object storage.
STORAGE_PATH = join(DATA_DIR, 'storage')

# Debug settings, setting DEBUG=True will give exception stacktraces.
DEBUG = os.getenv("DEBUG", "no").lower() not in {"0", "no", "false", "n", "f", ""}
TEMPLATE_DEBUG = DEBUG
DEBUG_JS = DEBUG

LOG_FILENAME = join(LOGS_DIR, 'metashare.log')

# Configure administrators for this django project.  If DEBUG=False, errors
# will be reported as emails to these persons...
ADMINS = (
    ('Luis Gomes', 'luis.gomes@di.fc.ul.pt'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(DATA_DIR, 'db.sqlite3'),
        'TEST_NAME': join(DATA_DIR, 'test-db.sqlite3'),
                                         # mandatory when using Selenium tests
    }
}

# the URL of the Solr server (or server core) which is used as a search backend
SOLR_URL = 'http://127.0.0.1:8983/solr/main'
# the URL of the Solr server (or server core) which is used as a search backend
# when running tests
TESTING_SOLR_URL = 'http://127.0.0.1:8983/solr/testing'

# Instead of using an email server, print emails to server console:
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# For testing, use a builtin email server (not for production use):
#EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'admin@portulanclarin.net'
EMAIL_HOST = 'smtp.portulanclarin.net'
EMAIL_PORT = 25

# For production use, you have to configure a proper mail server:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#
# See the Django documentation for more details:
# - https://docs.djangoproject.com/en/1.3/topics/email/#smtp-backend

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Lisbon'

# The location of the xdiff tool to compare XML files.
XDIFF_LOCATION = join(CODE_DIR, 'misc', 'tools', 'xdiff-src', 'xdiff')

# The web browser to use for the Selenium tests; possible values are:
# Firefox, Ie, Opera, Chrome
SELENIUM_DRIVER = 'Firefox'

# The port of the Selenium test server;
# this must be the same port as used in DJANGO_URL
SELENIUM_TESTSERVER_PORT = 8000


# Settings for synchronization:
# Time interval settings. It sets the intervals when the synchronization
# task will be triggered. Uses "crontab" conventions.
# Defaults will run the synchronization task once an hour.
SYNC_INTERVALS = {
    'MINUTE' : '25',      # 0-59 - Default is 25
    'HOUR' : '*',         # 0-23 - Default is *
    'DAY_OF_MONTH' : '*', # 1-31 - Default is *
    'MONTH' : '*',        # 1-12 - Default is *
    'DAY_OF_WEEK' : '*',  # 0-6 (0 is Sunday) - Default is *
}

# Settings for digest updating:
# Time interval settings. It sets the intervals when the digest updating
# task will be triggered. Uses "crontab" conventions.
# Defaults will run the updating task twice a day.
# The update intervals should roughly be half of the MAX_DIGEST_AGE as
# defined below
UPDATE_INTERVALS = {
    'MINUTE' : '*',      # 0-59 - Default is *
    'HOUR' : '*/12',         # 0-23 - Default is */12
    'DAY_OF_MONTH' : '*', # 1-31 - Default is *
    'MONTH' : '*',        # 1-12 - Default is *
    'DAY_OF_WEEK' : '*',  # 0-6 (0 is Sunday) - Default is *
}

# Maximum age of digests in storage folder in seconds
MAX_DIGEST_AGE = 60 * 60 * 24

# List of other META-SHARE Managing Nodes from which the local node imports
# resource descriptions. Any remote changes will later be updated
# ("synchronized"). Use this if you are a META-SHARE Managing Node!
# Important: make sure to use node IDs which are unique across both CORE_NODES
#            and PROXIED_NODES!
CORE_NODES = {
#    'node_id_1': {
#        'NAME': 'AUNI',                       # The short name of the node.
#        'DESCRIPTION': 'xxx',                 # A short descpription of the node.
#        'URL': 'metashare.example.com:8000',  # The URL of the other META-SHARE
#                                              # Managing Node (also include the
#                                              # port if needed).
#        'USERNAME': 'sync-user-1',            # The name of a sync user on
#                                              # the META-SHARE Managing Nodes.
#        'PASSWORD': 'sync-user-pass',         # Sync user's password.
#    },
#    'node_id_2': {
#        'NAME': 'BUNI',
#        'DESCRIPTION': 'xxx',
#        'URL': 'metashare.test.com',
#        'USERNAME': 'sync-user-2',
#        'PASSWORD': 'sync-user-pass-2',
#    },
}

# User accounts with the permission to access synchronization information on
# this node; whenever you change this setting, make sure to run
# "manage.py syncdb" for the changes to take effect!
SYNC_USERS = {
    #'syncuser1': 'secret',
    #'syncuser2': 'alsosecret',
}

# List of other META-SHARE Nodes from which the local node imports resource
# descriptions. Any remote changes will later be updated ("synchronized"). Any
# imported resource descriptions will also be shared with other nodes that
# synchronize with this local node, i.e., this node acts as a proxy for the
# listed nodes. This setting is meant to be used by META-SHARE Managing Nodes
# which make normal META-SHARE Node resource descriptions available on the
# META-SHARE Managing Nodes.
# Important: make sure to use node IDs which are unique across both CORE_NODES
#            and PROXIED_NODES!
PROXIED_NODES = {
#    'proxied_node_id_1': {
#        'NAME': 'Proxied Node 1',
#        'DESCRIPTION': 'xxx',
#        'URL': 'metashare.example.org',
#        'USERNAME': 'sync-user-3',
#        'PASSWORD': 'sync-user-pass-3',
#    },
}

# Analytics application sample settings. More analytics services are available.
# For more options, check http://packages.python.org/django-analytical/
#GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-XXXXXXXX-X'
#GOOGLE_ANALYTICS_SITE_SPEED = True


SECRET_KEY='5cf5f44eb077c2ca02eab22680424dac'


PRIVACY_INFO = {
    'service_name': 'PORTULAN / CLARIN applications and services',
    'service_desc': 'Infrastructure for Science and Technology of the Portuguese Language.',
    'entity_id': 'https://portulanclarin.net',
    'jurisdiction': 'Portugal',
    'behalf_of_url': 'https://portulanclarin.net/',
    'behalf_of_name': 'PORTULAN / CLARIN',
    'admin_name': 'Luís Gomes',
    'admin_email': 'luis.gomes@di.fc.ul.pt',
}
