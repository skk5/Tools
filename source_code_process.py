#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum, unique
from os import path
from sys import argv
import argparse


@unique
class StateType(Enum):
    CODE = 0
    STRING = 1
    COMMENT = 2
    ESCAPE = 3


class StateMapNote(object):
    """state-map-note.
    :param snt: type of this state note.
    :param ways: out ways of this note.
    :param name: name of note
    :param include_end: when out of this state, should include the transfer symbol
    """
    def __init__(self, snt, ways, name, include_end=False):
        self.name = name
        self.type = snt
        self.transfer_ways = ways  # k: symbols, v: StateNoteName
        self.include_end = include_end

        self.char_buffer = []

    def eat(self, c):
        if len(self.char_buffer) > 0:
            self.char_buffer.append(c)
            new_str = "".join(self.char_buffer)

            t = self._find_next_state(new_str)
            if t is not None:
                self.char_buffer.clear()
                return new_str, t
            elif self._is_likes_transfer_symbols(new_str):
                return None
            else:
                self.char_buffer.clear()
                return new_str, self.name

        t = self._find_next_state(c)
        if t is not None:
            return c, t
        elif self._is_likes_transfer_symbols(c):
            self.char_buffer.append(c)
            return None
        else:
            return c, self.name

    def _find_next_state(self, s):
        for k, v in self.transfer_ways.items():
            if k == "" or k == s:
                return v

        return None

    def _is_likes_transfer_symbols(self, s):
        for k, v in self.transfer_ways.items():
            if k.startswith(s):
                return True
        return False


class CodeFilter(object):
    def __init__(self):
        self.cur_state = None
        self.state_map = {}

    def _find_cur_state_note(self):
        if self.cur_state in self.state_map:
            return self.state_map[self.cur_state]
        return None

    def _self_check(self):
        all_state_notes = set([x for _, y in self.state_map.items() for _, x in y.transfer_ways.items()])
        if set(self.state_map.keys()) == all_state_notes:
            return True
        return False

    def filter(self, in_file, out_file, out_type):
        if not self._self_check():
            print("self check error")
            return

        for line in in_file:
            for c in line:
                n = self._find_cur_state_note()
                if n is None:
                    print("error")
                    exit()

                ret = n.eat(c)
                if ret is not None:
                    self.cur_state = ret[1]
                    csn = self._find_cur_state_note()

                    if out_type == StateType.CODE:
                        if ret[0] is not None and ((csn == n and n.type != StateType.COMMENT) or (csn != n and ((n.include_end and n.type != StateType.COMMENT) or (not n.include_end and csn.type != StateType.COMMENT)))):
                            out_file.write(ret[0])
                    elif out_type == StateType.STRING:
                        if ret[0] is not None and ((n.include_end and n.type == StateType.STRING or n.type == StateType.ESCAPE) or (not n.include_end and csn.type == StateType.STRING or csn.type == StateType.ESCAPE)):
                            out_file.write(ret[0].replace('\n', ''))
                            if (n.type == StateType.STRING or n.type == StateType.ESCAPE) and not (csn.type == StateType.STRING or csn.type == StateType.ESCAPE):
                                out_file.write('\n')
                    elif out_type == StateType.COMMENT:
                        if ret[0] is not None and ((n.include_end and n.type == StateType.COMMENT) or (not n.include_end and n.type == StateType.COMMENT)):
                            out_file.write(ret[0])

    def load_from_str(self, map_desc):
        pass


def filter_objc_source_file(in_file, out_file, out_type=StateType.CODE):
    _filter = CodeFilter()
    _filter.state_map = {
        'starter': StateMapNote(StateType.CODE, {
            '@"': "oc_string",
            "//": "single_comment",
            '"': "c_string",
            "/*": "multi_comment",
        }, "starter"),
        'oc_string': StateMapNote(StateType.STRING, {
            '"': "starter",
            '\\': "oc_escaper",
        }, "oc_string", True),
        'c_string': StateMapNote(StateType.STRING, {
            '"': "starter",
            '\\': "c_escaper",
        }, "c_string", True),
        'single_comment': StateMapNote(StateType.COMMENT, {
            "\n": "starter",
        }, "single_comment"),
        'multi_comment': StateMapNote(StateType.COMMENT, {
            "*/": "starter",
        }, "multi_comment", True),
        'oc_escaper': StateMapNote(StateType.ESCAPE, {
            "": "oc_string"
        }, "oc_escaper"),
        'c_escaper': StateMapNote(StateType.ESCAPE, {
            "": "c_string"
        }, "c_escaper")
    }

    _filter.cur_state = "starter"

    _filter.filter(in_file, out_file, out_type)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("source_code_file")
    arg_parser.add_argument('-o', "--out_file_path", help="out file path;if not specified, will write to {source_code_file_path_and_name}_trimmed{source_code_file_ext}")
    arg_parser.add_argument('-t', '--out_type', type=int, choices=[0, 1, 2], help="type what you want: 0 means code, 1 means only string, 2 means comment. defaults 0", default=0)

    args = arg_parser.parse_args()

    in_file_path = path.expanduser(args.source_code_file)

    if args.out_file_path is not None:
        out_file_path = path.expanduser(args.out_file_path)
    else:
        in_path_split = path.splitext(args.source_code_file)
        out_file_path = in_path_split[0] + "_trimmed" + in_path_split[1]

    ot = StateType.STRING
    if args.out_type:
        ot = StateType(args.out_type)

    with open(in_file_path, 'r', errors='ignore') as f:
        with open(out_file_path, 'w+') as o:
            filter_objc_source_file(f, o, ot)


if __name__ == "__main__":
    main()
