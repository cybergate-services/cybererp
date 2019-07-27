# -*- coding: utf-8 -*-

import logging
import random
import unicodedata
import re
import string
from odoo.exceptions import Warning, ValidationError, UserError
from odoo.tools import ustr

logger = logging.getLogger(__name__)

RANDOM_PASSWORD_LENGTH = 8

def remove_empty_lines(data):
    res = ''
    for line in data.split('\n'):
        if not line:
            continue
        else:
            new_line = '{}\n'.format(line)
            res += new_line
    return res


def generate_password(length=RANDOM_PASSWORD_LENGTH):
    chars = string.letters + string.digits
    password = ''
    while True:
        password = ''.join(map(lambda x: random.choice(chars), range(length)))
        if filter(lambda c: c.isdigit(), password) and \
                filter(lambda c: c.isalpha(), password):
            break
    return password


def slugify(s, max_length=None):
    s = ustr(s)
    uni = unicodedata.normalize('NFKD', s).encode(
                                            'ascii', 'ignore').decode('ascii')
    slug_str = re.sub('[\W_]', ' ', uni).strip().lower()
    slug_str = re.sub('[-\s]+', '-', slug_str)
    return slug_str[:max_length]
