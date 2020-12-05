import datetime
import logging
import utils

import requests

import config

logger = logging.getLogger("RADARR")
logger.setLevel(logging.DEBUG)
cfg = config.init()


def wanted(title, download_link, indexer):
    global cfg
    approved = False

    logger.debug("Notifying Radarr of release from %s: %s @ %s", indexer, title, download_link)

    headers = {'X-Api-Key': cfg['radarr.apikey']}
    params = {
        'title': utils.replace_spaces(title, '.'),
        'downloadUrl': download_link,
        'protocol': 'Torrent',
        'publishDate': datetime.datetime.now().isoformat(),
        'indexer': indexer
    }
    requestUrl = "{}/api/release/push".format(cfg['radarr.url'])

    logger.debug(headers)
    logger.debug(params)
    logger.debug(requestUrl)

    resp = requests.post(url=requestUrl, headers=headers, data=params, params=params)
    logger.debug(resp)
    respJson = resp.json()
    logger.debug(respJson)

    if 'approved' in resp:
        approved = resp['approved']

    return approved
