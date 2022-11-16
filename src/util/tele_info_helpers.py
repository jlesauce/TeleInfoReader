import re
from datetime import datetime

TELE_INFO_MSG_REGEX = r'(\w+)\s+(\S+)\s+(.)'


def is_valid_tele_info(entry: str):
    return re.match(TELE_INFO_MSG_REGEX, entry)


def extract_value_from_entry(entry: str) -> (str, str):
    matches = re.search(TELE_INFO_MSG_REGEX, entry)
    return matches.group(1), matches.group(2)


def get_current_timestamp():
    time_stamp = datetime.now().timestamp()
    return str(datetime.fromtimestamp(time_stamp))


def flatten_json(json_str):
    return json_str.replace('\n', ' ').replace(' ', '')
