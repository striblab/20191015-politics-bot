from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from candidates.models import NewCandidate
from candidates.utils.slack import send_slack_message

class Command(BaseCommand):
    help = 'Checks for candidates that have not been slacked and Slacks them.'


    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def format_candidate(self, candidate_inst):
        c = candidate_inst.__dict__
        c["district_clean"] = ' {district}'.format(c) if c["district"] != '' else ''
        c["registration_date_clean"] = datetime.strftime(c["registration_date"], '%a, %b %-d, %Y')
        c["cand_link"] = 'https://cfb.mn.gov/reports-and-data/viewers/campaign-finance/candidates/{entity_id}/'

        return '\n\n{office_sought}{district_clean}: {entity_full_name} ({party_name}) {registration_date_clean}\n{cand_link}'.format(c)

    def handle(self, *args, **options):
        unslacked_candidates = NewCandidate.objects.filter(bool_alert_sent=False)
        if unslacked_candidates.count() > 0:
            response_text = "You heard it here first: there's {} new candidates on the CFB site.".format(unslacked_candidates.count())
            for uc in unslacked_candidates:
                response_text += self.format_candidate(uc)

            bool_message_sent = send_slack_message(response_text, '#polgov')
            if bool_message_sent:
                unslacked_candidates.update(bool_alert_sent=True)
