#!/usr/bin/env python
from bottle import route
from slackclient import SlackClient


@route('/talk')
def talk_to_slack(message='kabooom'):
    token = "xoxp-51486140640-51539345538-51521267030-30b33fdd8a"      # found at https://api.slack.com/web#authentication
    sc = SlackClient(token)
    print sc.api_call(
        "chat.postMessage", channel="#general", text=message,
        username='alex', icon_emoji=':o)'
    )


@route('/destroyawsinstance')
def destroyawsinstance():
    return 'will terminated random instance i-12345'


if __name__ == '__main__':
    run(host='0.0.0.0', port=80, quiet=False)

# pick random instance (but not myself)
