from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Run from cron, checks for multiple updates via other management commands.'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        call_command('get_recent_candidates', verbosity=0)
        call_command('slack_new_candidates', verbosity=0)
