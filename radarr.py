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
    requestUrl = f"{cfg['radarr.url']}/api/release/push"

    logger.debug(f"REQ_HEADERS: {headers}")
    logger.debug(f"REQ_PARAMS:  {params}")
    logger.debug(f"REQ_URL:     {requestUrl}")

    resp = requests.post(url=requestUrl, headers=headers, json=params)

    logger.debug(f"REQ_BODY:    {resp.request.body}")
    logger.debug(f"REQ_HEADERS: {resp.request.headers}")
    logger.debug(f"RESP:        {resp}")
    logger.debug(f"RESP_JSON:   {resp.json()}")

    if 'approved' in resp:
        approved = resp['approved']

    return approved
