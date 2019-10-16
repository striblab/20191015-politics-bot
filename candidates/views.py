import json

from django.http import HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from candidates.utils.slack import send_slack_message


class SlackAPIResponderView(View):
    ''' How to receive and respond to interactive Slack traffic. '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SlackAPIResponderView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        # <view logic>
        return HttpResponse('GET is not really a thing around here. Try POST.')

    def post(self, request):
        # print(request.body)
        json_params = json.loads(request.body.decode('utf-8'))

        # Slack events API url verification
        if json_params['type'] == 'url_verification':
            return HttpResponse(json_params['challenge'])

        # For now pretty much everything else comes through the event dict.
        event = json_params['event']
        response_text = None

        # App mentions
        if event['type'] == "app_mention":
            try:
                # Don't get high on your own supply, i.e. make the bot respond to itself.
                if event['subtype'] == 'bot_message':
                    bot_message = True
            except:
                bot_message = False

            if not bot_message and "tell me a joke" in event["text"].lower():
                response_text = "(Disabled after this.) Hello <@{user}>! Knock, knock...".format(**event)

        if response_text:
            send_slack_message(response_text, "#robot-dojo")

        return HttpResponse('Generic POST POST POST.\n')

# if (payload.event.type === "app_mention") {
#
# if (payload.event.text.toLowerCase().includes("tell me a joke")) {
# console.log('attempting to tell a joke');
# // bool_sent = await app.sendReply(jokes.tell_a_new_joke(payload.event));
# //bool_sent = app.sendReply(jokes.tell_a_new_joke(payload.event));
# response_text = jokes.tell_a_new_joke(payload.event);
# } else if (payload.event.text.toLowerCase().match(/knock.*knock/g)) {
# response_text = jokes.respond_to_new_joke(payload.event);
# // bool_sent = await app.sendReply(jokes.respond_to_new_joke(payload.event));
# // bool_sent = app.sendReply(jokes.respond_to_new_joke(payload.event));
# }
#
# } else if (payload.event.type === "message") {
# // console.log(payload.event.subtype);
# if (payload.event.subtype != 'bot_message') {
# let [response_text, app.which_outgoing_joke] = jokes.am_i_joking(payload.event, app.which_outgoing_joke);
# // console.log(`Received a message event: user ${event.username} in channel ${event.channel} says ${event.text}`);
#
# // bool_sent = await app.sendReply(jokes.are_they_joking(payload.event));
#
# // let [reply_text, new_outgoing_joke] = jokes.am_i_joking(payload.event, app.which_outgoing_joke);
# // app.which_outgoing_joke = new_outgoing_joke;
# // console.log(app.which_outgoing_joke, new_outgoing_joke);
# // bool_sent = await app.sendReply(reply_text)
# // bool_sent = await app.sendReply(jokes.am_i_joking(payload.event));
#
# }
# }
