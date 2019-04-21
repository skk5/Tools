#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
import shutil


def patch_rename(file_or_dir: str, rename_fuc, temp_path, operation_records, recursive=False):
    file_or_dir_name = os.path.split(file_or_dir)[-1]
    if file_or_dir_name.startswith('.'):
        return

    if os.path.isfile(file_or_dir):
        file_path, file_name = os.path.split(file_or_dir)
        new_file_name = rename_fuc(file_name)

        temp_file_path = os.path.join(temp_path, new_file_name)
        shutil.copy2(file_or_dir, temp_file_path)
        operation_records.append((file_or_dir, temp_file_path))
    elif os.path.isdir(file_or_dir):
        files_under_path = os.listdir(file_or_dir)
        for file in files_under_path:
            file_path = os.path.join(file_or_dir, file)
            if not recursive and os.path.isdir(file_path):
                continue
            patch_rename(file_path, rename_fuc, temp_path, operation_records, recursive)
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
        arg_idx = 0
        for arg_exp in args:
            arg_idx += 1
            m = re.search(arg_exp, file_name)
            if m is None:
                print("argument({}) error!".format(arg_idx))
                exit(0)
            args_value.append(m.group(0))
        new_file_name = format_str.format(*args_value)
        return new_file_name

    return _format_imp


def _by_order():
    inner_counter = 0

    def _by_order_imp(file_name):
        ext = os.path.splitext(file_name)
        new_name = "{}.{}".format(inner_counter, ext)
        inner_counter++
        return new_name
    return _by_order_imp


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

    order_parser = sub_parsers.add_parser("order", help="rename file by order.")


    args = arg_parser.parse_args()
    operation_records = []

    if os.path.isfile(args.file_or_dir):
        temp_dir = os.path.join(os.path.split(args.file_or_dir)[0], '.rename_tmp')
    elif os.path.isdir(args.file_or_dir):
        temp_dir = os.path.join(args.file_or_dir, '.rename_tmp')
    else:
        print("Please attach a file or dir.")
        exit(0)

    is_create_by_self = False
    if not os.path.exists(temp_dir):
        is_create_by_self = True
        os.mkdir(temp_dir)
    
    if args.command == 'rpl':
        patch_rename(args.file_or_dir, _replace(args.old, args.new, args.E), temp_dir, operation_records, args.r)
    elif args.command == 'fmt':
        patch_rename(args.file_or_dir, _format(args.format, args.arguments), temp_dir, operation_records, args.r)
    elif args.command == 'order':
        patch_rename(args.file_or_dir, _by_order(), temp_dir, operation_records, args.r)

    if len(operation_records) == 0:
        print("Can't find any file to rename.")
        exit(0)
    
    old_file, new_file = operation_records[0]
    confirm = input("Rename Example:\n\t{} -> {}\nIs that you want? (If not, will rollback all operations.) y/n? : ".format(os.path.split(old_file)[-1], os.path.split(new_file)[-1]))
    while confirm.lower() not in ['n', 'y', 'yes', 'no']:
        confirm = input("Invalid input, please input again. y/n? : ")

    if confirm.lower() in ['n', 'no']:
            shutil.rmtree(temp_dir, ignore_errors=True)
    else:
        for old, tmp in operation_records:
            shutil.move(tmp, os.path.split(old)[0])
            if os.path.exists(old):
                os.remove(old)
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
