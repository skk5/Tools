#! /usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os
import re


def patch_rename(file_or_dir: str, rename_fuc, recursive=False):
    file_or_dir_name = os.path.split(file_or_dir)
    if file_or_dir_name.startswith('.'):
        return

    if os.path.isfile(file_or_dir):
        file_path, file_name = os.path.split(file_or_dir)
        new_file_name = rename_fuc(file_name)
        new_file_path = os.path.join(file_path, new_file_name)

        os.popen("mv {} {}".format(file_or_dir, new_file_path))
    elif os.path.isdir(file_or_dir):
        files_under_path = os.listdir(file_or_dir)
        for file in files_under_path:
            file_path = os.path.join(file_or_dir, file)
            if not recursive and os.path.isdir(file_path):
                continue
            patch_rename(file_path, rename_fuc, recursive)
    else:
        print("not a file or dir")
        exit(0)


def _replace(old: str, new: str, is_reg_exp=False):
    if is_reg_exp:
        reg_exp = re.compile(old, re.MULTILINE)

    def _replace_imp(file_name):
        if is_reg_exp:
            new_file_name = reg_exp.sub(new, file_name)
        else:
            new_file_name = file_name.replace(old, new)

        return new_file_name
    return _replace_imp


def _format(format_str: str, args: [str]):

    def _format_imp(file_name):
        args_value = []
        for arg_exp in args:
            m = re.search(arg_exp, file_name)
            if m is None:
                print("input error!")
                exit(0)
            args_value.append(m.group(0))
        new_file_name = format_str.format(args_value)
        return new_file_name

    return _format_imp


def main():
    arg_parser = argparse.ArgumentParser()
    sub_parsers = arg_parser.add_subparsers(help="commands", dest='command')

    rpl_parser = sub_parsers.add_parser('rpl', help='replace old string with new string in file name.')
    rpl_parser.add_argument('file_or_dir', help='path to file or dir.')
    rpl_parser.add_argument('old')
    rpl_parser.add_argument('new')
    rpl_parser.add_argument('-E', action='store_true', help='enable regular expression.')
    rpl_parser.add_argument('-r', action='store_true', help='recursive process files.')

    fmt_parser = sub_parsers.add_parser('fmt', help='get new file name from format string.')
    fmt_parser.add_argument('file_or_dir', help="path to file or dir.")
    fmt_parser.add_argument('format', help='format string: placeholder is {}.')
    fmt_parser.add_argument('-a', dest='arguments', action='append', help="regular expression search in file name.")
    fmt_parser.add_argument('-r', action='store_true', help='recursive process files.')

    args = arg_parser.parse_args()
    print(args)
    if args.command == 'rpl':
        patch_rename(args.file_or_dir, _replace(args.old, args.new, args.E), args.r)
    elif args.command == 'fmt':
        patch_rename(args.file_or_dir, _format(args.format, args.arguments), args.r)


if __name__ == '__main__':
    main()