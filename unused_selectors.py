#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse
from collections import namedtuple


def _read_all_used_selrefs(executable_file_path: str) -> [str]:
    selrefs_file = os.popen("otool -v -s __DATA __objc_selrefs {}".format(executable_file_path))
    
    selref_reg_exp = re.compile(r'(?:__TEXT:__objc_methname:)(\w*)')
    all_used_selectors = set()

    for line in selrefs_file:
        m = selref_reg_exp.search(line)
        if m:
            all_used_selectors.add(m.group(1))
    selrefs_file.close()

    return all_used_selectors


def _read_all_selrefs(link_map_path: str):
    object_number_reg_exp = re.compile(r'(?:\s*\[\s*)(\d+)(?:\s*\])(?:\s*/.*/)(\S*)')
    symbols_reg_exp = re.compile(r'(0x[0-9A-F]+)(?:\s*)(0x[0-9A-F]+)(?:\s*\[\s*)(\d+)(?:\s*\]\s*[-+]\[)(\w*)(?:\s*)([^\]]*)(?:\])')

    file_id_2_name = {}
    file_id_2_size = {}
    reading_file_id = True
    with open(link_map_path, 'r', errors='ignore') as f:
        for line in f:
            if reading_file_id:
                m = object_number_reg_exp.search(line)
                if m:
                    (file_id, file_name) = m.groups()
                    file_id_2_name[file_id] = file_name
                    continue
                else:
                    reading_file_id = False
            
            m = symbols_reg_exp.search(line)
            if m:
                (address, size, file_id, class_name, selector) = m.groups()
                

def _inner_process(line_map_path: str, executable_file_path: str):
    
    
    





    


def main():
    test_s = "0x00008CD0	0x000002E4	[  1] +[QBarEncode encodeQRCodeWithStr:version:errLev:pData:pWidth:]"
    # r'(0x\d+)(?:\s*)(0x\d+)(?:\s*\[\s*)(\d+)(?:\s*\]\s*[-+]\[)(\w*)(?:\s*)([^\]]*)(?:\])'
    symbols_reg_exp = re.compile(r'(0x[0-9A-F]+)(?:\s*)(0x[0-9A-F]+)(?:\s*\[\s*)(\d+)(?:\s*\]\s*[-+]\[)(\w*)(?:\s*)([^\]]*)(?:\])')
    print(symbols_reg_exp)
    m = symbols_reg_exp.search(test_s)
    print(m.groups())

if __name__ == "__main__":
    main()