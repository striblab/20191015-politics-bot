import json
import requests
from django.conf import settings

def send_slack_message(text, channel):
    endpoint = 'https://slack.com/api/chat.postMessage'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer {}'.format(settings.SLACK_AUTH_TOKEN)
    }
    payload = {
        'text': text,
        'channel': channel
    }
    r = requests.post(endpoint, data=json.dumps(payload), headers=headers)
    if r.status_code == 200:
        return True
    return False
