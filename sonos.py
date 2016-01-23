#!/usr/bin/env python
from soco import SoCo
from os import path, getcwd
from bottle import route, run, request, response


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
                    print('Using {0} as coordinator'.format(coordinator_temp))
                self.coordinator = coordinator_temp
                break
        if not self.coordinator:
            raise SonosCoordinatorNotFound

    def enforce_default_settings(self):
        self.coordinator.partymode()
        for sonos in [SoCo(speaker) for speaker in self.speakers]:
            if sonos.is_visible:
                sonos.volume = 10

    def is_playing(self):
        status = self.coordinator.get_current_transport_info()
        return True if status.get('current_transport_state') == 'PLAYING' else False

    def stop(self):
        self.coordinator.stop()

    def exited(self, url=None):
        self.stop()

    def pause(self):
        self.coordinator.pause()

    def playpause(self):
        self.pause() if self.is_playing() else self.coordinator.play()

    def start(self, url=None):
        self.enforce_default_settings()
        if url:
            self.coordinator.play_uri(url)
        else:
            self.coordinator.play()

    def entered(self):
        self.start()

    def play(self, url=None):
        self.start(url)

    def add_uri_to_queue(self, url):
        self.coordinator.add_uri_to_queue(url)


def get_mp3_link(url, regexp):
    '''Parse RSS feed item and return mp3 link'''
    import requests
    from re import search
    html = requests.get(url).text
    mp3_match = search(regexp, html)
    if mp3_match:
        mp3 = mp3_match.group(1)
        if mp3.endswith('.mp3'):
            return mp3
    print('Something wrong parsing "{0}", aborting'.format(url))
    return False


def get_speakers_from_txt():
    textfile = path.realpath(
        path.join(
            getcwd(),
            path.dirname(__file__),
            'speakers.txt',
        )
    )
    with open(textfile) as f:
        return [line.rstrip() for line in f.readlines() if not line.startswith('#')]


def parse_rss_feed(regexp):
    try:
        raw_rss_url = request.query.url
        mp3_link = get_mp3_link(raw_rss_url, regexp)
        print mp3_link
        coordinator.add_uri_to_queue(mp3_link)
        return 'Command executed successfully\n'
    except:
        response.status = 400
        return 'Error parsing url "{0}"\n'.format(raw_rss_url)


@route('/health')
def healh_check():
    return 'I am healthy!\n'


@route('/is_playing')
def is_sonos_playing():
    return('{0}\n'.format(coordinator.is_playing()))


@route('/add_uri_to_queue')
def add_uri_to_queue():
    try:
        mp3_link = request.query.url
        coordinator.add_uri_to_queue(mp3_link)
        return 'Command executed successfully\n'
    except:
        response.status = 400
        return 'Error parsing url "{0}"\n'.format(mp3_link)


# TODO unify RSS routes adding regexp map based on host header
@route('/add_spreaker_rss_episode_to_queue')
def sonos_add_spreaker_rss_episode_to_queue():
    parse_rss_feed('id="track_download" href="(.*?)"')


@route('/add_sysadministrivia_rss_episode_to_queue')
def sonos_add_sysadministrivia_rss_episode_to_queue():
    parse_rss_feed('<enclosure url="(.*?)"')


@route('/<command>')
def sonos_command(command='playpause'):
    try:
        assert command in (
            'play',
            'entered', # Start
            'start',
            'stop',
            'exited', # Stop
            'pause',
            'playpause',
        )
    except:
        response.status = 404
        return 'Command not found\n'
    eval('coordinator.{0}()'.format(command))
    return 'Command executed successfully\n'


if __name__ == '__main__':
    coordinator = SonosCoordinator(get_speakers_from_txt())
    run(host='0.0.0.0', port=9999, quiet=True)
