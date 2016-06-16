#!/usr/bin/env python
from bottle import route, run
from slackclient import SlackClient
import threading


@route('/test')
def talk_to_slack(message):
    json = '''[{
        "fallback": "Required plain-text summary of the attachment.",

        "color": "#36a64f",

        "author_name": "Anarchy monkey",
        "author_link": "http://flickr.com/bobby/",

        "title": "Terminating instance %s",
        "title_link": "https://eu-central-1.console.aws.amazon.com/ec2/v2/home?region=eu-central-1",

        "image_url": "http://popcrush1057.com/files/2013/07/369_40932711230_9148_n.jpg",
        "thumb_url": "http://example.com/path/to/thumb.png",

        "footer": "Slack API",
        "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
        "ts": 123456789
    }]''' % message
    token = "xoxp-51486140640-51539345538-51521267030-30b33fdd8a"      # found at https://api.slack.com/web#authentication
    sc = SlackClient(token)
    print sc.api_call(
        "chat.postMessage", channel="#general", text='',
        username='ANARCHYMONKEY', attachments=json,
    )


class BackgroundSomething(threading.Thread):
    """Manage Nuimo process"""

    def __init__(self):
        super(BackgroundSomething, self).__init__()
        self.instance = 'i-wljdfaljdljas'
        # self.instance = None

    def get_terminated_instance(self):
        # pick the right instance
        # self.instance = the real value from APIs
        # terminate
        # poll for terminated state
        return self.instance

    def run(self):
        from time import sleep  # TODO remove
        sleep(10)
        talk_to_slack(message=self.get_terminated_instance())


@route('/destroyawsinstance')
def destroyawsinstance():
    thread = BackgroundSomething()
    thread.start()
    return 'random instance will be terminated'


if __name__ == '__main__':
    run(host='0.0.0.0', port=80, quiet=False)
