#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from hashlib import md5
import re
from os import path, listdir


def get_file_md5(file_path: str):
    file_md5 = md5()
    with open (file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            file_md5.update(chunk)
    return file_md5.hexdigest()


def convert2Readable(size, base=10) -> str:
    if type(size) is str:
        size_int = int(size, base)
    else:
        size_int = size

    if size_int < 1024:
        return "{}B".format(size_int)
    elif size_int < 1024 ** 2:
        return "{}KB".format(size_int / 1024)
    elif size_int < 1024 ** 3:
        return "{}MB".format(size_int / 1024 ** 2)
    elif size_int < 1024 ** 4:
        return "{}GB".format(size_int / 1024 ** 3)
    elif size_int < 1024 ** 5:
        return "{}TB".format(size_int / 1024 ** 4)
    else:
        return "{}PB".format(size_int / 1024 ** 5)


def convertFromReadable(size: str) -> int:
    if re.match(r'(0[box])?\d+[kKmMgGtTpP]', size):
        prefix_2_base = {
            '0b': 2,
            '0o': 8,
            '0x': 16
        }
        real_base = 10
        for prefix, base in prefix_2_base.items():
            if size.startswith(prefix):
                real_base = base
                break

        real_measure = 1
        postfix_2_measure = {
            'k': 1024,
            'm': 1024 ** 2,
            'g': 1024 ** 3,
            't': 1024 ** 4,
            'p': 1024 ** 5
        }
        for postfix, measure in postfix_2_measure.items():
            if size[-1].lower() == postfix:
                real_base = measure
                size = size[:-1]
                break
        return int(size, real_base) * real_measure
    else:
        return 0


def walk_files(process_func, dir_or_file_path, include_hidden_files=False):
    dir_or_file_path = path.expanduser(dir_or_file_path)

    if path.basename(dir_or_file_path).startswith('.') and not include_hidden_files:
        return

    if path.isdir(dir_or_file_path):
        files = listdir(dir_or_file_path)
        for file in [path.join(dir_or_file_path, f) for f in files]:
            walk_files(process_func, file, include_hidden_files)
    elif path.isfile(dir_or_file_path):
        process_func(dir_or_file_path)