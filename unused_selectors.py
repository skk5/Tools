#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse
from collections import namedtuple
from utilities import convert2Readable

method_black_list = ['.cxx_destruct']

def _read_all_used_selrefs(executable_file_path: str) -> [str]:
    selrefs_file = os.popen("otool -v -s __DATA __objc_selrefs {}".format(executable_file_path))
    
    selref_reg_exp = re.compile(r'(?:__TEXT:__objc_methname:)(\S*)')
    all_used_selectors = set()

    for line in selrefs_file:
        m = selref_reg_exp.search(line)
        if m:
            all_used_selectors.add(m.group(1))
    selrefs_file.close()

    return all_used_selectors


def _read_all_selrefs(link_map_path: str):
    object_number_reg_exp = re.compile(r'(?:\s*\[\s*)(\d+)(?:\s*\])(?:\s*\.*/.*/)(\S*)')
    symbols_reg_exp = re.compile(r'(0x[0-9A-F]+)(?:\s*)(0x[0-9A-F]+)(?:\s*\[\s*)(\d+)(?:\s*\]\s*[-+]\[)(\w*)(?:\s*)([^\]]*)(?:\])')

    file_id_2_name = {}
    file_name_2_selectors = {}
    with open(link_map_path, 'r', errors='ignore') as f:
        for line in f:
            m = object_number_reg_exp.search(line)
            if m:
                (file_id, file_name) = m.groups()
                file_id_2_name[file_id] = file_name
                continue
            
            # if len(file_id_2_name) > 0:
            #     print(file_id_2_name)
            #     exit(0)
            
            m = symbols_reg_exp.search(line)
            if m:
                print("find one")
                (address, size, file_id, class_name, selector) = m.groups()
                file_name = file_id_2_name[file_id]
                if file_name in file_name_2_selectors:
                    selectors = file_name_2_selectors[file_name]
                    selectors.append((class_name, selector, size))
                else:
                    selectors = [(class_name, selector, size)]
                    file_name_2_selectors[file_name] = selectors

    return file_name_2_selectors


def _inner_process(link_map_paths: [str], executable_file_path: str):
    all_used_sels = _read_all_used_selrefs(os.path.expanduser(executable_file_path))
    print(all_used_sels)
    all_used_sels_list = [x for y in all_used_sels.values() for x in y]
    unused_sels = {}
    size_result = {}
    for lmp in link_map_paths:
        link_map_path = os.path.expanduser(lmp)
        link_map_name = os.path.basename(link_map_path)
        file_name_2_selectors = _read_all_selrefs(link_map_path)
        unused_sels_i = []
        file_name_2_total_size = {}
        for k, v in file_name_2_selectors.items():
            total_size = 0
            for (class_name, selector, size) in v:
                if selector not in all_used_sels_list:
                    unused_sels_i.append((class_name, selector, size))
                total_size += int(size, 16)
            file_name_2_total_size[k] = total_size
        unused_sels[link_map_name] = unused_sels_i
        size_result[link_map_name] = file_name_2_total_size

    output_file_path = os.path.join(os.path.dirname(os.path.expanduser(executable_file_path)), "result.txt")
    while os.path.exists(output_file_path):
        output_file_path = output_file_path[:-4] + "0.txt"
    with open(output_file_path, 'w') as of:
        of.write("##unused_selectors\n")
        for k, v in unused_sels.items():
            of.write(k)
            of.write("\n")
            for (class_name, selector, size) in v:
                of.write("[{} {}];({})\n".format(class_name, selector, convert2Readable(size, 16)))
            
            lib_size_result = {}
            file_name_2_total_size = size_result[k]
            for file_name, total_size in file_name_2_total_size.items():
                if '(' in file_name:
                    lib_name = file_name[:file_name.find('(')]
                    if lib_name in lib_size_result:
                        lib_size_result[lib_name] += total_size
                    else:
                        lib_size_result[lib_name] = total_size
            
            of.write("\n\n")
            for file_name in sorted(file_name_2_total_size.keys()):
                of.write("{}:\t{}\n".format(file_name, convert2Readable(file_name_2_total_size[file_name])))

            of.write("lib size:\n")
            for lib_name, size in lib_size_result.items():
                of.write("{}:\t{}".format(lib_name, convert2Readable(size)))
    


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("exc_file", help="excutable file in ipa->payload. you can get it at: unzip xx.ipa -> payload -> show content of package -> find the executable file.")
    arg_parser.add_argument("-l", "--link_map", action="append", help="link map path(s)")
    # arg_parser.add_argument("-c", "--calc_size", action="store_true", help="calc object size")

    args = arg_parser.parse_args()
    if len(args.link_map) == 0:
        print("Need link map file(s).")
        exit(0)
    
    _inner_process(args.link_map, args.exc_file)

if __name__ == "__main__":
    main()