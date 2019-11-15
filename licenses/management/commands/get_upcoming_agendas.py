import os
import re
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from licenses.models import AgendaItem

class Command(BaseCommand):
    help = 'Checks for new license/permit applications, imports.'

    api_endpoint_upcoming = 'https://lims.minneapolismn.gov/Home/UpcomingMeetings'
    api_endpoint_past = 'https://lims.minneapolismn.gov/Home/MarkedAgendas'

    agenda_record_root_upcoming = 'https://lims.minneapolismn.gov/Agenda'
    agenda_record_root_past = 'https://lims.minneapolismn.gov/MarkedAgenda'

    COMMITTEE_NAMES = ['Economic Development & Regulatory Services Committee']

    INTERESTING_PHRASES = ['restaurant', r'brewery', r'distillery', r'cafe', r'liquor', r'bar', r'beer', r'eatery', r'coffee shop', r'bakery', r'butcher', r'co-op', r'grocery', r'deli']

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def get_agenda_links(self, sked_endpoint, agenda_endpoint):
        agenda_results= []
        agendas = json.loads(requests.get(sked_endpoint).content)
        # print(agendas)
        for a in agendas:
            commitee_name = a['CommitteeName']
            if commitee_name in self.COMMITTEE_NAMES:
                if a['AgendaId'] != "0":  # Ignore if no agenda yet
                    agenda_link = os.path.join(agenda_endpoint, a['Abbreviation'], str(a['AgendaId']))
                    a.update({'agenda_link': agenda_link})
                    agenda_results.append(a)
        return agenda_results

    def strip_line_breaks(self, input_str):
        input_str = re.sub(r'\n{2,}', '\n', input_str).strip()
        input_str = re.sub(r'\n\s{2,}', '\n', input_str)
        input_str = input_str.replace('\nThis link open a new window', ' ')
        return input_str


    def find_agenda_items(self, meeting_obj, meeting_type='p'):
        agenda = requests.get(meeting_obj['agenda_link']).content
        soup = BeautifulSoup(agenda, "html.parser")
        # print(soup)
        interesting_items = []
        subject_headings = soup.find_all("h4", class_="caption-subject")

        for heading in subject_headings:
            action_type = heading.text.strip()

            items = heading.parent.parent.find_next_sibling().find('ol')
            for item in items.find_all('li', recursive=False):
                item_text = self.strip_line_breaks(item.text.strip())

                item_title = item.find_all('span')[1].text
                item_link = item.find('a')['href']

                # Check for interesting phrases
                for regex in self.INTERESTING_PHRASES:
                    if re.search(regex, item_text, re.IGNORECASE):

                        # check for text blob description
                        try:
                            item_description = self.strip_line_breaks(item.find('div', class_="markedAgenda nopadding print_row").text)
                        except:
                            # list type items
                            item_description = ''
                            # item_description = item.find_all('span')[1].text
                            list_items = item.find('ol').find_all('li')
                            for index, li in enumerate(list_items):
                                item_description += '\n    {}. {}'.format(str(index+1), self.strip_line_breaks(li.text))

                        if meeting_type == 'past':
                            action_taken = item.find('b').text.replace('Action Taken: ', '').strip()
                        else:
                            action_taken = ''

                        report_back = {
                            'item_title': item_title,
                            'item_link': item_link,
                            # 'item_text': item_text,
                            'item_description': item_description,
                            'action_type': action_type,
                            'action_taken': action_taken
                        }
                        # TODO: send back a nicely formatted list view
                        if report_back not in interesting_items:
                            interesting_items.append(report_back)

        return interesting_items

    def load_item(self, meeting, item, meeting_type):
        # This is a small dataset, so update or create based on meeting link and item title
        obj, created = AgendaItem.objects.update_or_create(
            meeting_link=meeting['agenda_link'],
            item_title=item['item_title'],
            defaults={
                'committee_name': meeting['CommitteeName'],
                'meeting_id': meeting['AgendaId'],
                'meeting_type': meeting_type,
                'item_link': item['item_link'],
                'item_description': item['item_description'],
                'action_type': item['action_type'],
                'action_taken': item['action_taken'],
            },
        )

    def handle(self, *args, **options):
        # # Feed it a manual agenda
        # upcoming_agendas = [
        #     {'agenda_link': 'https://lims.minneapolismn.gov/MarkedAgenda/EDRS/1188'}
        # ]

        # Upcoming items ...
        upcoming_agendas = self.get_agenda_links(self.api_endpoint_upcoming, self.agenda_record_root_upcoming)
        for a in upcoming_agendas:
            matching_items = self.find_agenda_items(a, 'u')
            for mi in matching_items:
                self.load_item(a, mi, 'u')

        # Items already acted on...
        past_agendas = self.get_agenda_links(self.api_endpoint_past, self.agenda_record_root_past)
        for a in past_agendas:
            matching_items = self.find_agenda_items(a, 'p')
            for mi in matching_items:
                self.load_item(a, mi, 'p')
