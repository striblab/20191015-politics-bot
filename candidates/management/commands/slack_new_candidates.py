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
        c["district_clean"] = f' {c["district"]}'.format(c) if c["district"] != '' else ''
        c["registration_date_clean"] = datetime.strftime(c["registration_date"], '%a, %b %-d, %Y')
        c["cand_link"] = f'https://cfb.mn.gov/reports-and-data/viewers/campaign-finance/candidates/{c["entity_id"]}/'

        return f'\n\n{c["office_sought"]}{c["district_clean"]}: {c["entity_full_name"]} ({c["party_name"]}) {c["registration_date_clean"]}\n{c["cand_link"]}'

    def handle(self, *args, **options):
        unslacked_candidates = NewCandidate.objects.filter(bool_alert_sent=False)
        if unslacked_candidates.count() > 0:
            response_text = f"You heard it here first: there's {unslacked_candidates.count()} new candidates on the CFB site."
            for uc in unslacked_candidates:
                response_text += self.format_candidate(uc)

            bool_message_sent = send_slack_message(response_text, '#polgov')
            if bool_message_sent:
                unslacked_candidates.update(bool_alert_sent=True)
