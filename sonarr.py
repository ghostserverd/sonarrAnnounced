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
    requestUrl = "{}/api/release/push".format(cfg['sonarr.url'])

    logger.debug(headers)
    logger.debug(params)
    logger.debug(requestUrl)

    resp = requests.post(url=requestUrl, headers=headers, params=params)
    logger.debug(resp)
    respJson = resp.json()
    logger.debug(respJson)

    if 'approved' in resp:
        approved = resp['approved']

    return approved
