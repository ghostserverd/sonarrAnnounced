import datetime
import logging
import re
from pathlib import Path

import requests
from unidecode import unidecode

logger = logging.getLogger("UTILS")
logger.setLevel(logging.DEBUG)


#############################################################
# Useful reusable methods
#############################################################

def get_id(text, group=1, pattern=None):
    torrent_id = None
    try:
        if pattern is not None:
            m = re.search(pattern, text)
            if m:
                torrent_id = m.group(group)
        else:
            m = re.findall('id=(\S*)', text)
            if m:
                torrent_id = m[group]

    except Exception as ex:
        logger.exception("Exception while get_id:")

    return torrent_id


def substr(data, first, last, strip):
    val = None
    try:
        if strip:
            lasti = data.find(last)
            # if last is not present in the string, return from first to the end of data
            if lasti == -1:
                lasti = len(data)
            val = data[data.find(first) + len(first):lasti]
        else:
            val = data[data.find(first):data.find(last) + len(last)]

    except Exception as ex:
        logger.exception("Exception while substr:")

    return val


def str_before(data, before):
    val = None
    try:
        val = data[0:data.find(before) - 1]
    except Exception as ex:
        logger.exception("Exception while str_before:")

    return val


def get_urls(text):
    return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)


def strip_irc_color_codes(line):
    line = re.sub("\x03\d\d?,\d\d?", "", line)
    line = re.sub("\x03\d\d?", "", line)
    line = re.sub("[\x01-\x1F]", "", line)
    return line


# credits: http://stackoverflow.com/a/4391978
def find_tracker(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return dic
    return None


def replace_spaces(text, new):
    return re.sub('[ ]{1,}', new, text)


def replace_periods(text, new):
    return re.sub('[.]{1,}', new, text)


def formatted_torrent_name(torrent_name):
    chars = {
        # strip chars
        '?': '',
        "'": '',
        '\\': '',
        '/': '',
        ':': '',
        ';': '',
        # replace chars
        '@': 'at.',
        '&': 'and.'
    }

    formatted = unidecode(torrent_name)
    for look, replace in chars.items():
        formatted = formatted.replace(look, replace)

    # replace date hypons with .'s (some release titles will have - in it, e.g. Hawaii.Five-O.S01E01...)
    date_pattern = '(\d{4}-\d{2}-\d{2})'
    m = re.search(date_pattern, formatted)
    if m:
        formatted = formatted.replace(m.group(0), m.group(0).replace('-', '.'))

    formatted = replace_periods(formatted, '.')
    return formatted


# credits: http://code.activestate.com/recipes/576880-convert-datetime-in-python-to-user-friendly-repres/
def human_datetime(date_time):
    """
    converts a python datetime object to the
    format "X days, Y hours ago"

    @param date_time: Python datetime object

    @return:
        fancy datetime:: string
    """
    current_datetime = datetime.datetime.now()
    delta = str(current_datetime - date_time)
    if delta.find(',') > 0:
        days, hours = delta.split(',')
        days = int(days.split()[0].strip())
        hours, minutes = hours.split(':')[0:2]
    else:
        hours, minutes = delta.split(':')[0:2]
        days = 0
    days, hours, minutes = int(days), int(hours), int(minutes)
    datelets = []
    years, months, xdays = None, None, None
    plural = lambda x: 's' if x != 1 else ''
    if days >= 365:
        years = int(days / 365)
        datelets.append('%d year%s' % (years, plural(years)))
        days = days % 365
    if days >= 30 and days < 365:
        months = int(days / 30)
        datelets.append('%d month%s' % (months, plural(months)))
        days = days % 30
    if not years and days > 0 and days < 30:
        xdays = days
        datelets.append('%d day%s' % (xdays, plural(xdays)))
    if not (months or years) and hours != 0:
        datelets.append('%d hour%s' % (hours, plural(hours)))
    if not (xdays or months or years):
        datelets.append('%d minute%s' % (minutes, plural(minutes)))
    return ', '.join(datelets) + ' ago.'


def download_torrent(tracker, torrent_id, cookies, url):
    torrent_path = ''

    try:
        # generate filename
        torrents_dir = Path('torrents', tracker)
        if not torrents_dir.exists():
            torrents_dir.mkdir(parents=True)
        torrent_file = "{}.torrent".format(torrent_id)
        torrent_path = torrents_dir / torrent_file

        # download torrent
        response = requests.get(url, cookies=cookies, stream=True)
        with torrent_path.open('wb') as handle:
            if not response.ok:
                logger.debug("Unexpected response from %s while download_torrent: status_code: %d", tracker,
                             response.status_code)
                return None

            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    handle.write(chunk)

        return torrent_path

    except Exception as ex:
        logger.exception("Exception %s while download_torrent: %s to %s", ex, url, torrent_path)

    return None
