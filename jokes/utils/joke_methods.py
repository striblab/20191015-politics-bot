import re
import random

from jokes.models import JokeTeller, JokeResponder

JOKES_THE_BOT_KNOWS = [
    ['Doctor', 'Oooooo wee ooooooooooooo!'],
    ['A bot user', 'A bot user who likes you and just wants you to be happy.'],
    ['Hatch', 'Gesundheit.'],
    ['Mustache', 'I mustache you to get back to work.'],
    ['Aida', 'Aida a sandwich for lunch today.'],
    ['A little old lady', "We've worked together all this time, and I didn't know you could yodel."],
    ['Lettuce', "Lettuce at some point soon do more with this bot than tell silly jokes."],
]

def is_this_a_joke(event):
    try:
        # Don't get high on your own supply, i.e. make the bot respond to itself.
        if event['subtype'] == 'bot_message':
            bot_message = True
    except:
        bot_message = False

    # App mentions
    if not bot_message and event['type'] == "app_mention":

        if "tell me a joke" in event["text"].lower():
            # Start this person over in a given channel, even if they didn't finish the previous joke
            joke_responder, jr_created = JokeResponder.objects.update_or_create(
                username=event["user"],
                channel=event["channel"],
                defaults = {
                    'step': 0,
                    'which_joke': random.randint(0,len(JOKES_THE_BOT_KNOWS)-1)
                }
            )
            response_text = "Hello <@{user}>! Knock, knock...".format(**event)
            return response_text, event["channel"]
        elif re.search(r'knock.*knock', event["text"].lower()):
            # Start this person over in a given channel, even if they didn't finish the previous joke
            joke_teller, jt_created = JokeTeller.objects.update_or_create(
                username=event["user"],
                channel=event["channel"],
                defaults = {
                    'step': 0
                }
            )
            response_text = "Hello <@{user}>! Who's there?".format(**event)
            return response_text, event["channel"]

    # Other message types
    elif not bot_message and event["type"] == "message":
        incoming_joke_response = respond_to_incoming_joke(event)
        if incoming_joke_response:
            return incoming_joke_response, event["channel"]

        outgoing_joke_response = tell_outgoing_joke_step(event)
        if outgoing_joke_response:
            return outgoing_joke_response, event["channel"]

    return False, None


def respond_to_incoming_joke(event):
    # if this user is known to currently be telling a joke
    try:
        persistent_joke_teller = JokeTeller.objects.get(username=event["user"], channel=event["channel"])
    except:
        persistent_joke_teller = None
        return False

    if persistent_joke_teller.step == 0:
        persistent_joke_teller.step = 1
        persistent_joke_teller.save()
        return "{text} who?".format(**event)

    elif persistent_joke_teller.step == 1:
        persistent_joke_teller.delete()

        joke_responses = [
          'Aha ha ha ha. Ha ha ha ha ha!',
          'LOL',
          "OMG you did not. That's hilarious.",
          'You are a true original, <@{user}>!'.format(**event),
          "Dying. On the floor about to pass out because I am laughing so hard."
        ]
        return random.choice(joke_responses)


def tell_outgoing_joke_step(event):
    # if this user is known to currently be responding to a joke
    try:
        persistent_joke_responder = JokeResponder.objects.get(username=event["user"], channel=event["channel"])
    except:
        persistent_joke_responder = None
        return False

    if re.search(r'who.*s there', event["text"].lower()):
        persistent_joke_responder.step = 1  # Not usually necessary, but this will prevent user from accidentally skipping ahead by mentioning who. Also enables multistep (more than 2) jokes (maybe)
        persistent_joke_responder.save()
        return JOKES_THE_BOT_KNOWS[persistent_joke_responder.which_joke][0]
    elif persistent_joke_responder.step > 0 and re.search(r'[a-z]+ who', event["text"].lower()):
        current_step = persistent_joke_responder.step
        # if this is the last step in this joke, end the routine by deleting the JokeResponder
        if current_step == len(JOKES_THE_BOT_KNOWS[persistent_joke_responder.which_joke]) - 1:
            persistent_joke_responder.delete()
        else:
            persistent_joke_responder.step += 1
            persistent_joke_responder.save()
        return JOKES_THE_BOT_KNOWS[persistent_joke_responder.which_joke][current_step]
    return False
