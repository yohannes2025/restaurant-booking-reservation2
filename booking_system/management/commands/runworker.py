# booking_system/management/commands/runworker.py
import os
from django.core.management.base import BaseCommand
from django_rq.management.commands.rqworker import Command as RqWorkerCommand

class Command(BaseCommand):
    help = 'Starts an RQ worker for the default queue.'

    def handle(self, *args, **options):
        # Set environment variable to make sure Redis is accessible for worker
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "booking_system.settings")
        self.stdout.write(self.style.SUCCESS('Starting RQ worker...'))
        try:
            RqWorkerCommand().handle('default', *args, **options)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('RQ worker stopped.'))