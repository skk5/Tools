#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import source_code_process
import utilities
from os import path, makedirs
from shutil import copy

def test_source_process():
    file_path = ""
    out_path = ""

    def walk_func(f: str):
        print(f)
        bn = path.basename(f)
        out_file_path = f.replace(file_path, out_path, 1)
        out_file_dirs = path.dirname(out_file_path)
        if not path.exists(out_file_dirs):
            makedirs(out_file_dirs)
        if bn.endswith('.h') or bn.endswith('.m') or bn.endswith('.mm') or bn.endswith('.cpp') or bn.endswith('.c'):
            with open(f, 'r', errors='ignore') as in_file:
                with open(out_file_path, 'w+') as out_file:
                    source_code_process.filter_objc_source_file(in_file, out_file)
        else:
            copy(f, out_file_path)

    utilities.walk_files(walk_func, file_path)
    
    
def test_walk_file():
    file_path = "/Users/shenkuikui/Desktop/unused/"

    utilities.walk_files(lambda f: print(f), file_path)

test_source_process()
