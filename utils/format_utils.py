from typing import Union

import time


def get_refined_message(raw_message):
    refined_msg = escape_dict(raw_message)
    refined_msg['timestamp'] = int(time.time() * 1000)
    return refined_msg


def escape(plain_str):
    """正常可以直接 json.dumps， 但加上 emoji 就得先转义一下了"""
    return plain_str.encode('unicode-escape').decode()


def escape_dict(dct: Union[dict, None] = None):
    for k, v in dct.items():
        if type(k) != str:
            continue
        if type(v) != str:
            continue
        dct[escape(k)] = escape(v)
    return dct


def unescape(escaped_str):
    return escaped_str.encode().decode('unicode-escape')


def unescape_dict(dct: Union[dict, None] = None):
    for k, v in dct.items():
        if type(k) != str:
            continue
        if type(v) != str:
            continue
        dct[unescape(k)] = unescape(v)
    return dct
