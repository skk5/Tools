#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path, listdir, stat
from utilities import get_file_md5
import argparse

def _search(dir: str, target_file_path: str, recursive=False) -> [str]:
    #check
    if not path.isdir(dir) or not path.isfile(target_file_path):
        return None
    
    target_size = path.getsize(target_file_path)
    target_md5 = get_file_md5(target_file_path)
    
    same_files = []
    def _search_iterator(file_path: str):
        if path.isfile(file_path):
            if path.getsize(file_path) == target_size and target_md5 == get_file_md5(file_path):
                same_files.append(file_path)
        elif path.isdir(file_path):
            for sub_file_path in listdir(file_path):
                full_sub_file_path = path.join(file_path, sub_file_path)
                if not recursive and path.isdir(full_sub_file_path):
                    continue
                _search_iterator(full_sub_file_path)
    
    _search_iterator(dir)

    return same_files


def main():
    #test
    # file = "/Users/ewing/Desktop/image_1.png"
    # print(get_file_md5(file))
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("target", help="path of target file that contains content you want to search")
    arg_parser.add_argument("search_dir", help="path of dir that you want to search in")
    arg_parser.add_argument('-r', '--recursive', action="store_true", help="search directory recursively")

    args = arg_parser.parse_args()

    target = path.expanduser(args.target)
    search_dir = path.expanduser(args.search_dir)
    same_files = _search(search_dir, target, args.recursive)

    print("Files with same content:")
    print('\n'.join(same_files))


if __name__ == '__main__':
    main()