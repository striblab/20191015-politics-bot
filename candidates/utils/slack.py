import json
import time
import hmac
import hashlib
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

def verify_slack_request(request):
    try:
        timestamp = request.headers['X-Slack-Request-Timestamp']
        print(timestamp)
        slack_signature = request.headers['X-Slack-Signature']
    except:
        return False

    if abs(time.time() - int(timestamp)) > 60 * 5:
         # The request timestamp is more than five minutes from local time. It could be a replay attack, so let's ignore it.
        return False

    request_body = request.body.decode('utf-8')
    sig_basestring = 'v0:' + timestamp + ':' + request_body

    hash = hmac.new(settings.SLACK_SIGNING_SECRET.encode('utf-8'), sig_basestring.encode('utf-8'), hashlib.sha256).hexdigest()
    my_signature = 'v0=' + hash

    if my_signature == slack_signature:
        # hooray, the request came from Slack!
        return True
    return False
