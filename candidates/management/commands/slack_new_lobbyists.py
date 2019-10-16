from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from candidates.models import NewLobbyist
from candidates.utils.slack import send_slack_message

class Command(BaseCommand):
    help = 'Checks for lobbyists that have not been slacked and Slacks them.'


    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def format_lobbyist(self, lobbyist_inst):
        c = lobbyist_inst.__dict__
        c["registration_date_clean"] = datetime.strftime(c["registration_date"], '%a, %b %-d, %Y')
        c["l_link"] = f'https://cfb.mn.gov/reports-and-data/viewers/lobbying/lobbyists/{c["lobbyist_id"]}/'

        return f'\n\n{c["lobbyist_full_name"]}: {c["association_full_name"]} ({c["registration_date_clean"]})\n{c["l_link"]}'

    def handle(self, *args, **options):
        unslacked_lobbyists = NewLobbyist.objects.filter(bool_alert_sent=False)
        if unslacked_lobbyists.count() > 0:
            response_text = f"You heard it here first: there's {unslacked_lobbyists.count()} new lobbyists on the CFB site."
            for uc in unslacked_lobbyists:
                response_text += self.format_lobbyist(uc)

            bool_message_sent = send_slack_message(response_text, '#polgov')
            if bool_message_sent:
                unslacked_lobbyists.update(bool_alert_sent=True)
