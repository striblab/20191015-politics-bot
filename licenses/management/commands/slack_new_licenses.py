import json
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from licenses.models import AgendaItem
from candidates.utils.slack import send_slack_message, build_slack_mrkdwn_block

class Command(BaseCommand):
    help = 'Checks for agenda items that have not been slacked and Slacks them.'


    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def slackify_text(self, str_message):
        output = str_message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        return output

    def format_item(self, item_instance):
        i = item_instance.__dict__
        return '\n\n*<https://lims.minneapolismn.gov{item_link}|{item_title}>*\n{item_description}\n_{action_taken} ({action_type})_'.format(**i)

    def handle(self, *args, **options):
        unslacked_items = AgendaItem.objects.filter(bool_alert_sent=False)
        if unslacked_items.count() > 0:
            blocks = []
            for committee_name in unslacked_items.values_list('committee_name', flat=True).distinct():
                if unslacked_items.count() == 1:
                    response_text = "You heard it here first: there's a new {} agenda item RE: food.".format(committee_name)
                else:
                    response_text = "You heard it here first: there are {} new {} agenda items RE: food.".format(unslacked_items.count(), committee_name)
                blocks.append(build_slack_mrkdwn_block(response_text))

                for uc in unslacked_items:
                    blocks.append(build_slack_mrkdwn_block(self.format_item(uc)))
                    blocks.append({"type": "divider"})

            bool_message_sent = send_slack_message(blocks, '#foodtips')
            # bool_message_sent = send_slack_message(blocks)  # dojo
            if bool_message_sent:
                unslacked_items.update(bool_alert_sent=True)
