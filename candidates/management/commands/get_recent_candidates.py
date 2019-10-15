import requests
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from candidates.models import NewCandidate

class Command(BaseCommand):
    help = 'Checks for new candidates, imports.'

    candidate_api = 'https://cfb.mn.gov/reports/api/'

    data = {
        'action': 'grid_data',
        'data[action]': 'recent-candidate-registrations',
        'data[params][0]': 'all',
        'data[type]': 'current-lists'
    }

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def strip_blank_time(self, input_str):
        return input_str.replace(' 00:00:00.000', '')

    def null_to_blank(self, input_str):
        if not input_str:
            return ''
        return input_str

    def handle(self, *args, **options):
        response = requests.post('https://cfb.mn.gov/reports/api/', data=self.data)
        if response.status_code == 200:
            candidate_list = response.json()['data']
            for candidate in candidate_list.items():
                candidate_data = candidate[1][0]
                # print(candidate[1][0])
                # This is a small dataset, so update or create based on candidate ID
                obj, created = NewCandidate.objects.update_or_create(
                    entity_id=candidate_data[1],
                    defaults={
                        'entity_full_name': candidate_data[0].strip(),
                        'party_name': candidate_data[2].strip(),
                        'office_sought': candidate_data[3],
                        'district': self.null_to_blank(candidate_data[4]),
                        'registration_date': self.strip_blank_time(candidate_data[5]),
                        'termination_date': candidate_data[6],
                    },
                )
