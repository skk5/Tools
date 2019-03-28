#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from hashlib import md5

def get_file_md5(file_path: str):
    file_md5 = md5()
    with open (file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            file_md5.update(chunk)
    return file_md5.hexdigest()
