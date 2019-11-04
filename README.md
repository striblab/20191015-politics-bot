# Politics bot

An app that exists for two important reasons.

1. Scrapin' sites, checking for updated data, and sending Slack alerts about that.
2. Tellin' (and responding to) knock-knock jokes.

Both routines use the Slack Events API.

## Scrapin' sites
Current sites the bot monitors:
 - Minnesota Campaign Finance and Public Disclosure Board
    - [Recent candidate filings]("https://cfb.mn.gov/reports/current-lists/#/recent-candidate-registrations/all/")
    - [Recent lobbyist filings]("https://cfb.mn.gov/reports/current-lists/#/recent-lobbyist-registrations/all/")

The bot is designed to mostly run by calling the `update_lists` management command from a cron job.

```
python manage.py update_lists
```

The bot grabs filings from the CFB's site and adds or updates records in the database. If it finds entries that have not been sent to Slack, it sends a message to the #polgov channel.

## Bad jokes
The bot also can tell or respond to knock-knock jokes through the Slack Events API.

All incoming requests from Slack are handled by the `SlackAPIResponderView` in `candidates.views`. The logic for handling jokes is handled by methods in `jokes.utils.joke_methods`. When a request is sent to the API endpoint from Slack, the `is_this_a_joke` method determines if any joke-related reply should be generated, and if so will create temporary `JokeTeller` or `JokeResponder` model instances to keep multistep jokes on track. If a response is returned, the main `SlackAPIResponderView` will send the actual Slack message.

If you want to add a new interactive chat module, it should follow a similar pattern of taking the request, determining if a response is needed, and returning either a text response or `False` to `SlackAPIResponderView`.

# To build a (Dockerized) website:
docker build -t politics_bot .
docker run --detach=false --publish=8000:80 --env-file .env.prod politics_bot
