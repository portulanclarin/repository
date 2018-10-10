from django.core.management.base import BaseCommand
from django.conf import settings
from json import dumps

class Command(BaseCommand):
    
    args = '<var>'
    help = 'Dump the contents of specified variable'
    
    def handle(self, varname, **options):
        value = getattr(settings, varname, None)
        if value is not None:
            print dumps(value)
