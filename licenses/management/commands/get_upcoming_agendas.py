import os
import re
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
#from candidates.models import NewCandidate, NewLobbyist

class Command(BaseCommand):
    help = 'Checks for new license/permit applications, imports.'

    api_endpoint_upcoming = 'https://lims.minneapolismn.gov/Home/UpcomingMeetings'
    api_endpoint_past = 'https://lims.minneapolismn.gov/Home/MarkedAgendas'

    agenda_record_root_past = 'https://lims.minneapolismn.gov/MarkedAgenda'

    COMMITTEE_NAMES = ['Committee of the Whole', 'Economic Development & Regulatory Services Committee']

    INTERESTING_PHRASES = [r'brewery', r'restaurant', r'liquor license']

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def get_agenda_links(self):
        agenda_results= []
        agendas = json.loads(requests.get(self.api_endpoint_past).content)
        print(agendas)
        for a in agendas:
            # print(a['Id'], a['CommitteeName'])
            commitee_name = a['CommitteeName']
            if commitee_name in self.COMMITTEE_NAMES:
                agenda_link = os.path.join(self.agenda_record_root_past, a['Abbreviation'], str(a['AgendaId']))
                a.update({'agenda_link': agenda_link})
                # print(commitee_name, agenda_link)
                agenda_results.append(a)
                # https://lims.minneapolismn.gov/MarkedAgenda/ZP/1199
        return agenda_results

    def find_agenda_items(self, meeting_obj):
        agenda = requests.get(meeting_obj['agenda_link']).content
        soup = BeautifulSoup(agenda, "html.parser")

        interesting_items = []
        subject_headings = soup.find_all("h4", class_="caption-subject")
        for heading in subject_headings:
            action_type = heading.text.strip()

            items = heading.parent.parent.find_next_sibling().find('ol')
            for item in items.find_all('li', recursive=False):
                item_text = item.text.strip()
                item_text = re.sub(r'\n{2,}', '\n', item_text)
                item_text = re.sub(r'\n\s{2,}', '\n', item_text)
                item_text = item_text.replace('\nThis link open a new window', ' ')

                item_title = item.find_all('span')[1].text
                item_link = item.find('a')['href']

                # Check for interesting phrases
                for regex in self.INTERESTING_PHRASES:
                    if re.search(regex, item_text, re.IGNORECASE):
                        report_back = {
                            'item_title': item_title,
                            'item_link': item_link,
                            'item_text': item_text,
                            'action_type': action_type
                        }
                        # TODO: send back a nicely formatted list view
                        if report_back not in interesting_items:
                            interesting_items.append(report_back)

        return interesting_items

    def handle(self, *args, **options):
        # agendas = self.get_agenda_links()

        # Feed it a manual agenda
        agendas = [
            {'agenda_link': 'https://lims.minneapolismn.gov/MarkedAgenda/EDRS/1188'}
        ]
        for a in agendas:
            matching_items = self.find_agenda_items(a)
            print(matching_items)
