import datetime
import logging
import time

import config
import db
import sonarr
import radarr
import utils

cfg = config.init()

############################################################
# Tracker Configuration
############################################################
name = "PreToMe"
irc_host = "irc.pretome.info"
irc_port = 6697
irc_channel = "#announce"
invite_cmd = None
irc_tls = True
irc_tls_verify = False

# these are loaded by init
auth_key = None
torrent_pass = None
delay = 0

logger = logging.getLogger(name.upper())
logger.setLevel(logging.DEBUG)


############################################################
# Tracker Framework (all trackers must follow)
############################################################
# Parse announcement message
@db.db_session
def parse(announcement):
    global name

    decolored = utils.strip_irc_color_codes(announcement)
    if 'https://pretome.info/details.php' not in decolored:
        return

    # extract required information from announcement
    torrent_substr = utils.substr(decolored, '] ', ' https', True)
    torrent_title = utils.replace_spaces(utils.substr(torrent_substr, '', ' ::', True), '.')
    torrent_id = utils.get_id(decolored, 0)

    if 'TV|' in decolored:
        notify_pvr(torrent_id, torrent_title, auth_key, torrent_pass, name, 'Sonarr')
    elif 'Movies|' in decolored:
        notify_pvr(torrent_id, torrent_title, auth_key, torrent_pass, name, 'Radarr')



def notify_pvr(torrent_id, torrent_title, auth_key, torrent_pass, name, pvr_name):
    if torrent_id is not None and torrent_title is not None:
        download_link = get_torrent_link(torrent_id, torrent_title)

        announced = db.Announced(date=datetime.datetime.now(), title=torrent_title,
                                 indexer=name, torrent=download_link, pvr=pvr_name)

        if delay > 0:
            logger.debug("Waiting %s seconds to check %s", delay, torrent_title)
            time.sleep(delay)

        if pvr_name == 'Sonarr':
            approved = sonarr.wanted(torrent_title, download_link, name)
        elif pvr_name == 'Radarr':
            approved = radarr.wanted(torrent_title, download_link, name)

        if approved:
            logger.debug("%s approved release: %s", pvr_name, torrent_title)
            snatched = db.Snatched(date=datetime.datetime.now(), title=torrent_title,
                                   indexer=name, torrent=download_link, pvr=pvr_name)
        else:
            logger.debug("%s rejected release: %s", pvr_name, torrent_title)

    return

# Generate torrent link
def get_torrent_link(torrent_id, torrent_name):
    torrent_link = "https://pretome.info/download.php/{}/{}/{}.torrent".format(torrent_id,
                                                                               torrent_pass,
                                                                               torrent_name)
    return torrent_link


# Initialize tracker
def init():
    global auth_key, torrent_pass, delay

    auth_key = ""
    torrent_pass = cfg["{}.torrent_pass".format(name.lower())]
    delay = cfg["{}.delay".format(name.lower())]

    # check torrent_pass was supplied
    if not torrent_pass:
        return False

    return True
