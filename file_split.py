#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
from utilities import convertFromReadable
from math import ceil
import argparse

read_chunk_size = 2048

def split(original_file_path, max_single_file_size=None, max_file_count=2):
    original_file_path = path.expanduser(original_file_path)
    ori_file_size = path.getsize(original_file_path)
    size_per_file = 0
    if max_single_file_size:
        size_per_file = convertFromReadable(max_single_file_size)
        if size_per_file == 0:
            print("Input split files size wrong.")
            return
        if size_per_file >= ori_file_size:
            print("File size is less than splited file size. Nothing happended.")
            return
    elif max_file_count > 0:
        size_per_file = ori_file_size / max_file_count
    else:
        print("Please input valid file size or count.")
        return
    
    all_files_and_size = {}
    with open(original_file_path, 'rb') as in_file:
        for file_number in range(ceil(ori_file_size / size_per_file)):
            file_name, ext = path.splitext(original_file_path)
            file_name = "{}_{}_{}".format(file_name, ext, file_number)
            file_size = int(min(ori_file_size - file_number * size_per_file, size_per_file))
            read_times = ceil(file_size / read_chunk_size)
            with open(file_name, 'wb') as out_file:
                for read_time in range(read_times):
                    read_size = int(min(read_chunk_size, file_size - read_chunk_size * read_time))
                    out_file.write(in_file.read(read_size))


def concat(splited_files: [str]) -> str:
    if len(splited_files) == 0:
        return
    splited_files = sorted(splited_files)
    concat_file_name = path.expanduser("{}{}".format(*(splited_files[0].split("_")[:2])))
    with open (concat_file_name, 'wb') as out_file:
        for file in splited_files:
            file = path.expanduser(file)
            with open(file, 'rb') as f:
                b = f.read(read_chunk_size)
                while b:
                    out_file.write(b)
                    b = f.read(read_chunk_size)

def main():
    arg_parser = argparse.ArgumentParser()
    sub_commands = arg_parser.add_subparsers(help="commands", dest="command")

    split_parser = sub_commands.add_parser("split", help='split file to several small files.')
    split_parser.add_argument("file", help="path to file that want to split")
    split_parser.add_argument("spe", nargs="?", help="specify splited file max size or amount. If not specified, treats num as 2.\nsize format: \d+[kKmMgGtTpP].\nnum format: \d+")
    
    cat_parser = sub_commands.add_parser("cat", help="concat files to one.")
    cat_parser.add_argument("files", nargs="+", help="path to files that be concatenated")

    args = arg_parser.parse_args()
    print(args)
    if args.command == 'split':
        if args.spe:
            try:
                cnt = int(args.spe)
                split(args.file, max_file_count=cnt)
            except:
                split(args.file, max_single_file_size=args.spe)
        else:
            split(args.file)
    elif args.command == 'cat':
        concat(args.files)
    else:
        pass

if __name__ == "__main__":
    main()

