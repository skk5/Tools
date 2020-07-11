#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from utilities import get_file_md5
from source_code_process import filter_objc_source_file, StateType
from io import StringIO
import argparse
from sys import stdout

default_resource_exts = ['.png', '.jpg', '.caf', '.mp4', '.txt']
default_code_exts = ['.c', '.h', '.m', '.cpp', '.mm']
default_resource_ext = '.png'


def find_resource_and_code(path, resource_exts, code_exts):
    resource_files = []
    code_files = []

    def file_judge(file):
        file_ext = str.lower(os.path.splitext(file)[-1])

        if file_ext in resource_exts:
            resource_files.append(file)
        elif file_ext in code_exts:
            code_files.append(file)

    def search_iterator(file_path):
        if os.path.split(file_path)[-1].startswith('.'):
            # ignore hidden files and dirs
            return
        elif file_path.find('.appiconset/') != -1 or file_path.find('.launchimage/') != -1 or os.path.exists(file_path) == False:
            # ignore xcode appiconset and launchimage assets
            return
        elif os.path.isfile(file_path):
            file_judge(file_path)
        else:
            files = os.listdir(file_path)
            for file in files:
                sub_file_path = os.path.join(file_path, file)
                search_iterator(sub_file_path)

    search_iterator(path)

    return resource_files, code_files


def check_same_resource(resource_files):
    file_md5_2_paths = {}
    for file in resource_files:
        md5_hex = get_file_md5(file)

        if md5_hex in file_md5_2_paths:
            file_list = file_md5_2_paths[md5_hex]
        else:
            file_list = []
        file_list.append(file)
        file_md5_2_paths[md5_hex] = file_list

    repeated_files = []
    for k, v in file_md5_2_paths.items():
        if len(v) > 1:
            repeated_files.append(v)

    return repeated_files


def get_str_pure_content(s: str):
    while s.endswith('\n'):
        s = s[:-1]

    if s.startswith('@"'):
        s = s[2:]
    elif s.startswith('"'):
        s = s[1:]

    if s.endswith('"'):
        s = s[:-1]

    name, ext = os.path.splitext(s)
    if name.endswith('@2x') or s.endswith('@3x'):
        name = name[:-3]
        s = name + ext

    return s


def find_unused_resource_file(project_root_path, resource_exts=default_resource_exts, code_exts=default_code_exts, check_duplication=False):
    """
    Find unused resource file in project of Xcode.
    :param project_root_path: project root path.
    :param resource_exts: extensions for resource file, should starts with '.'.
    :param code_exts: extensions for code file, should starts with '.'.
    :return: list of unused file with full path.
    """

    project_root_path = os.path.expanduser(project_root_path)
    if os.path.isfile(project_root_path):
        print('You should attach a dir, not a file.')
        exit(1)

    print("Scanning...", end='')
    stdout.flush()

    resource_files, code_files = find_resource_and_code(project_root_path, resource_exts, code_exts)
    resource_file_names = set()
    for rf in resource_files:
        file_name = os.path.split(rf)[-1]
        file_name_without_ext, file_ext = os.path.splitext(file_name)
        if file_name_without_ext.endswith('@2x') or file_name_without_ext.endswith('@3x'):
            file_name_without_ext = file_name_without_ext[:-3]
        resource_file_names.add(file_name_without_ext + file_ext)

    print("\nScan Done!")

    same_files = []
    if check_duplication:
        same_files = check_same_resource(resource_files)

    if len(resource_file_names) > 0 and len(code_files) > 0:
        print("resource file: {}; code file: {}".format(len(resource_file_names), len(code_files)))
    elif len(resource_file_names) == 0:
        print("can't find any resource file.")
        exit(0)
    elif len(code_files) == 0:
        print("can' find any code file.")
        exit(0)

    print("Analyzing...")
    process_file_ctn = 0
    last_process = 0
    for code_file in code_files:
        last_string = None
        with open(code_file, 'r', errors='ignore') as cf:
            string_file = StringIO()
            filter_objc_source_file(cf, string_file, StateType.STRING)
            string_file.seek(0)
            for line in string_file:
                line = get_str_pure_content(line)
                if last_string is not None:
                    if (line.startswith('.') and line in resource_exts) or ('.' not in line and ('.' + line) in resource_exts):
                        file_full_name = last_string + line
                        if '.' not in line:
                            file_full_name = last_string + '.' + line

                        if file_full_name in resource_file_names:
                            resource_file_names.remove(file_full_name)
                            last_string = None
                            continue
                    elif (last_string + default_resource_ext) in resource_file_names:
                        resource_file_names.remove(last_string + default_resource_ext)
                        last_string = None
                        continue
                last_string = None

                possible_file_name = os.path.split(line)[-1]
                if possible_file_name in resource_file_names:
                    resource_file_names.remove(possible_file_name)
                else:
                    last_string = line

            string_file.close()

        process_file_ctn += 1
        cur_process = process_file_ctn / len(resource_files)
        if cur_process - last_process >= 1 / 42:
            print('#', end='', file=stdout)
            stdout.flush()
            last_process = cur_process
    print("100.0%")
    print("Analyze Done!")

    left_files = [x for x in resource_files if os.path.split(x)[-1] in resource_file_names]

    return left_files, same_files


def main():
    release = 1
    if release:
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument("path_to_project_root", help="path to project that you want to find unused resource files.")
        arg_parser.add_argument("-c", "--code_exts", help="exts for code file, string separated by white space.")
        arg_parser.add_argument("-i", "--resource_exts", help="exts for resource file, string separated by white space.")
        arg_parser.add_argument("-o", "--out_file", help="path to out file. defaults STDOUT")
        arg_parser.add_argument("-d", "--deduplication", action="store_true", default=False, help="point out resource files with same content.")

        args = arg_parser.parse_args()

        print("Warning!!!  The output of this script is for reference only. Please confirm carefully before deleting resources.")

        def ext_check(exts):
            ret = []
            for e in exts:
                if e.startswith('.'):
                    ret.append(e)
                else:
                    ret.append('.' + e)
            return ret

        print("test: args: {}".format(args))
        format_args = {}
        if args.code_exts:
            format_args['code_exts'] = ext_check(args.code_exts.split(' '))
        if args.resource_exts:
            format_args['resource_exts'] = ext_check(args.resource_exts.split(' '))
        format_args["check_duplication"] = args.deduplication

        unused_files, same_files = find_unused_resource_file(args.path_to_project_root, **format_args)
        if args.out_file:
            with open(os.path.expanduser(args.out_file), 'w+') as f:
                f.write("Unused Files: \n")
                f.write("\n".join(unused_files))

                if len(same_files) > 0:
                    f.write("\n\nFiles with same content:\n")
                    f.write('\n'.join(same_files))
        else:
            print("Unused Files:")
            print("\n".join(unused_files))
            if len(same_files) > 0:
                print("\n\nFiles with same content:\n")
                print('\n'.join(same_files))
    else:
        unused_files = find_unused_resource_file('/Users/ewingshen/Documents/TestMachO/')
        print("\n".join(unused_files))


if __name__ == '__main__':
    main()
