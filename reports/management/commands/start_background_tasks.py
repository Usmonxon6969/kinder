from django.core.management.base import BaseCommand
import subprocess
import sys
import os
import signal
import time


class Command(BaseCommand):
    help = 'Start Celery worker and beat for background tasks'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processes = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-beat',
            action='store_true',
            help='Do not start Celery Beat (scheduler)',
        )

        parser.add_argument(
            '--no-worker',
            action='store_true',
            help='Do not start Celery Worker',
        )

    def handle(self, *args, **options):
        # Set environment variable for Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kindergarten_meal_system.settings')

        try:
            # Check if Redis is running
            self.stdout.write(self.style.WARNING('Checking if Redis is running...'))
            try:
                import redis
                r = redis.Redis(host='localhost', port=6379, db=0)
                r.ping()
                self.stdout.write(self.style.SUCCESS('Redis is running'))
            except:
                self.stdout.write(self.style.ERROR('Redis is not running! Please start Redis first.'))
                return

            # Start Celery worker
            if not options['no_worker']:
                self.stdout.write(self.style.WARNING('Starting Celery worker...'))
                worker_cmd = [
                    'celery',
                    '-A',
                    'kindergarten_meal_system',
                    'worker',
                    '--loglevel=info'
                ]
                worker_process = subprocess.Popen(worker_cmd)
                self.processes.append(worker_process)
                self.stdout.write(self.style.SUCCESS('Celery worker started'))

            # Start Celery Beat
            if not options['no_beat']:
                self.stdout.write(self.style.WARNING('Starting Celery Beat...'))
                beat_cmd = [
                    'celery',
                    '-A',
                    'kindergarten_meal_system',
                    'beat',
                    '--loglevel=info'
                ]
                beat_process = subprocess.Popen(beat_cmd)
                self.processes.append(beat_process)
                self.stdout.write(self.style.SUCCESS('Celery Beat started'))

            self.stdout.write(self.style.SUCCESS('Background tasks are running! Press Ctrl+C to stop.'))

            # Keep command running
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\nStopping background tasks...'))

            # Stop all processes
            for process in self.processes:
                if sys.platform == 'win32':
                    process.terminate()
                else:
                    os.kill(process.pid, signal.SIGTERM)

            # Wait for processes to terminate
            for process in self.processes:
                process.wait()

            self.stdout.write(self.style.SUCCESS('Background tasks stopped'))