#!/usr/bin/env python
from os import path, getcwd
from re import search
from urlparse import urlparse
from soco import SoCo
from bottle import route, run, request, response


MAX_VOLUME = 30
DEFAULT_VOLUME = 10
DEFAULT_VOLUME_DELTA = 5


class SonosCoordinatorNotFound(Exception):
    pass


class SonosCoordinator(object):

    def __init__(self, speakers, debug=False):
        self.debug = debug
        self.speakers = speakers
        self.set_coordinator()

    def set_coordinator(self):
        self.coordinator = None
        for speaker in self.speakers:
            coordinator_temp = SoCo(speaker)
            if coordinator_temp.is_coordinator:
                if self.debug:
                    print 'Using {0} as coordinator'.format(coordinator_temp)
                self.coordinator = coordinator_temp
                break
        if not self.coordinator:
            raise SonosCoordinatorNotFound

    def change_volume(self, delta=0):
        for sonos in [SoCo(speaker) for speaker in self.speakers]:
            if sonos.is_visible and 0 <= (sonos.volume + delta) <= MAX_VOLUME:
                sonos.volume += delta

    def volumeup(self):
        self.change_volume(DEFAULT_VOLUME_DELTA)

    def volumedown(self):
        self.change_volume(-DEFAULT_VOLUME_DELTA)

    def enforce_default_settings(self):
        self.coordinator.partymode()
        for sonos in [SoCo(speaker) for speaker in self.speakers]:
            if sonos.is_visible:
                sonos.volume = DEFAULT_VOLUME

    def is_playing(self):
        status = self.coordinator.get_current_transport_info()
        return True if status.get('current_transport_state') == 'PLAYING' else False

    def start(self, url=None):
        self.enforce_default_settings()
        if url:
            self.coordinator.play_uri(url)
        else:
            self.coordinator.play()

    def stop(self):
        self.enforce_default_settings()
        self.coordinator.stop()

    def pause(self):
        self.enforce_default_settings()
        self.coordinator.pause()

    def exited(self):
        self.pause()

    def playpause(self):
        if self.is_playing():
            self.pause()
        else:
            self.play()

    def entered(self):
        self.start()

    def play(self, url=None):
        self.start(url)

    def add_uri_to_queue(self, url):
        self.coordinator.add_uri_to_queue(url)


def get_regexp_from_host(host):
    regexp_map = {
        'www.spreaker.com': 'id="track_download" href="(.*?)"',
        'sysadministrivia.com': '<enclosure url="(.*?)"',
    }
    return regexp_map.get(host, '###~NOTEXISTENT~###')


def get_mp3_link_from_feed_item(url):
    '''Parse RSS feed item and return mp3 link'''
    import requests

    host = urlparse(url).netloc
    html = requests.get(url).text
    mp3_match = search(get_regexp_from_host(host), html)
    if mp3_match:
        mp3 = mp3_match.group(1)
        if mp3.endswith('.mp3'):
            return mp3
    print 'Something wrong parsing "{0}", aborting'.format(url)
    return False


def get_speakers_from_txt():
    textfile = path.realpath(
        path.join(
            getcwd(),
            path.dirname(__file__),
            'speakers.txt',
        )
    )
    with open(textfile) as speakersfile:
        return [line.rstrip() \
            for line in speakersfile.readlines() if not line.startswith('#')]


def add_item_to_sonos_queue(is_feed_item=False):
    try:
        item = request.query.url
        if is_feed_item:
            mp3_link = get_mp3_link_from_feed_item(item)
        else:
            mp3_link = item
        COORDINATOR.add_uri_to_queue(mp3_link)
        return 'Command executed successfully\n'
    except Exception:
        response.status = 400
        return 'Error parsing url "{0}"\n'.format(item)


@route('/health')
def healh_check():
    return 'I am healthy!\n'


@route('/is_playing')
def is_sonos_playing():
    return '{0}\n'.format(COORDINATOR.is_playing())


@route('/add_uri_to_queue')
def sonos_add_uri_to_queue():
    return add_item_to_sonos_queue()


@route('/add_rss_episode_to_queue')
def sonos_add_rss_episode_to_queue():
    return add_item_to_sonos_queue(is_feed_item=True)


@route('/<command>')
def sonos_command(command='playpause'):
    try:
        assert command in (
            'play',
            'entered',  # Start
            'start',
            'stop',
            'exited',  # Pause
            'pause',
            'playpause',
            'volumeup',
            'volumedown',
        )
    except Exception:
        response.status = 404
        return 'Command not found\n'
    eval('COORDINATOR.{0}()'.format(command))
    return 'Command executed successfully\n'


if __name__ == '__main__':
    COORDINATOR = SonosCoordinator(get_speakers_from_txt())
    run(host='0.0.0.0', port=9999, quiet=True)
