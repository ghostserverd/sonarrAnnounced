import datetime
import logging
import utils

import requests

import config

logger = logging.getLogger("SONARR")
logger.setLevel(logging.DEBUG)
cfg = config.init()


def wanted(title, download_link, indexer):
    global cfg
    approved = False

    logger.debug("Notifying Sonarr of release from %s: %s @ %s", indexer, title, download_link)

    headers = {'X-Api-Key': cfg['sonarr.apikey']}
    params = {
        'title': utils.replace_spaces(title, '.'),
        'downloadUrl': download_link,
        'protocol': 'Torrent',
        'publishDate': datetime.datetime.now().isoformat(),
        'indexer': indexer
    }

    resp = requests.post(url="{}/api/release/push".format(cfg['sonarr.url']), headers=headers, params=params).json()
    logger.debug(resp)
    if 'approved' in resp:
        approved = resp['approved']

    return approved
