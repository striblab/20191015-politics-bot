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
        c["l_link"] = 'https://cfb.mn.gov/reports-and-data/viewers/lobbying/lobbyists/{lobbyist_id}/'.format(c)

        return '\n\n{lobbyist_full_name}: {association_full_name} ({registration_date_clean})\n{l_link}'.format(c)

    def handle(self, *args, **options):
        unslacked_lobbyists = NewLobbyist.objects.filter(bool_alert_sent=False)
        if unslacked_lobbyists.count() > 0:
            if unslacked_lobbyists.count() == 1:
                response_text = "You heard it here first: there's a new lobbyist on the CFB site."
            else:
                response_text = "You heard it here first: there are {} new lobbyists on the CFB site.".format(unslacked_lobbyists.count())

            for uc in unslacked_lobbyists:
                response_text += self.format_lobbyist(uc)

            bool_message_sent = send_slack_message(response_text, '#polgov')
            if bool_message_sent:
                unslacked_lobbyists.update(bool_alert_sent=True)
