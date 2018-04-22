from django.core.management.base import BaseCommand, CommandError
from traceroute.models import Target
import subprocess


class Command(BaseCommand):
    help = "Performs traceroutes and updates all databases."

    def handle(self, *args, **options):
        directory = '/var/www/html/django/traceroute/rrdpy'
        for target in Target.objects.all():
            try:
                subprocess.Popen(["sudo", "python3", directory + "/update_sub.py", target.ip_address])
            except Target.DoesNotExist:
                raise CommandError('Target "%s" does not exist.' % target)

