import json

from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from candidates.utils.slack import send_slack_message, verify_slack_request
from jokes.utils.joke_methods import is_this_a_joke


class SlackAPIResponderView(View):
    ''' How to receive and respond to interactive Slack traffic. '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SlackAPIResponderView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        # <view logic>
        return HttpResponse('GET is not really a thing around here. Try POST.')

    def post(self, request):
        # Check if this is a geniune Slack request
        if not verify_slack_request(request):
            return HttpResponse('This does not appear to be a real Slack request.\n')
        else:
            # print(request.body)
            json_params = json.loads(request.body.decode('utf-8'))

            # Slack events API url verification
            if type in json_params:
                if json_params['type'] == 'url_verification':
                    return HttpResponse(json_params['challenge'])

            # For now pretty much everything else comes through the event dict.
            event = json_params['event']
            response_text = None

            response_text, channel = is_this_a_joke(event)

            if response_text:
                send_slack_message(response_text, channel)
                return HttpResponse('{}\n'.format(response_text))

        return HttpResponse('Generic POST POST POST.\n')
