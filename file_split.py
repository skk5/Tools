#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
from utilities import convertFromReadable
from math import ceil

def split(original_file_path, max_single_file_size=None, max_file_count=2):
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
    
    read_chunk_size = 2048
    all_files_and_size = {}
    with open(original_file_path, 'rb') as in_file:
        for file_number in range(ceil(ori_file_size / size_per_file)):
            file_name, ext = path.splitext(original_file_path)
            file_name = "{}_{}_{}".format(file_name, ext, file_number)
            file_size = ori_file_size - file_number * size_per_file
            read_times = ceil(file_size / read_chunk_size)
            with open(file_name, 'wb') as out_file:
                for read_time in range(read_times):
                    read_size = min(read_chunk_size, file_size - read_chunk_size * read_time)
                    out_file.write(in_file.read(read_size))


def concat(splited_files: [str]) -> str:
    pass


def main():
    pass

if __name__ == "__main__":
    main()

