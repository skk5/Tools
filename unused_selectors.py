#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse


def _inner_process(line_map_path: str, executable_file_path: str):
    selrefs_file = os.popen("otool -v -s __DATA __objc_selrefs {}".format(executable_file_path))
    
    selref_reg_exp = re.compile(r'(?:__TEXT:__objc_methname:)(\w*)')
    object_number_reg_exp = re.compile(r'(?:\s*\[\s*)(\d+)(?:\s*\])(?:\s*/.*/)(\S*)')
    symbols_reg_exp = re.compile(r'(?:\s*)(0x\d+)(?:\s*)(0x\d+)(?:\s*\[\s*)(\d+)(?:\s*\]\s*[+-]\[)(\w*)(?:\s*)([^\]]*)(?:\])')


def main():
    test_s = "0x00008CD0	0x000002E4	[  1] +[QBarEncode encodeQRCodeWithStr:version:errLev:pData:pWidth:]"
    symbols_reg_exp = re.compile(r'(0x\d+)(?:\s*)(0x\d+)(?:\s*\[\s*)(\d+)(?:\s*\]\s*[-+]\[)(\w*)(?:\s*)([^\]]*)(?:\])')
    print(symbols_reg_exp)
    m = symbols_reg_exp.search(test_s)
    print(m.groups())

if __name__ == "__main__":
    main()