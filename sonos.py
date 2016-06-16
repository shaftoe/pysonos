#!/usr/bin/env python
from bottle import route, run
from slackclient import SlackClient

json = '''[{
    "title": "Slack API Documentation",
    "title_link": "https://api.slack.com/",

    "image_url": "http://popcrush1057.com/files/2013/07/369_40932711230_9148_n.jpg",
    "thumb_url": "http://example.com/path/to/thumb.png",
}]'''


@route('/test')
def talk_to_slack(message='kabooom'):
    token = "xoxp-51486140640-51539345538-51521267030-30b33fdd8a"      # found at https://api.slack.com/web#authentication
    sc = SlackClient(token)
    print sc.api_call(
        "chat.postMessage", channel="#general", text=message,
        username='ANARCHYMONKEY', attachments=json
    )


@route('/destroyawsinstance')
def destroyawsinstance():
    # get_random_instance()
    return 'will terminated random instance i-12345'


if __name__ == '__main__':
    run(host='0.0.0.0', port=80, quiet=False)

# pick random instance (but not myself)
