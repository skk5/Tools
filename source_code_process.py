#!/usr/bin/python3

from enum import Enum, unique
from os import path
from sys import argv


@unique
class StateType(Enum):
    CODE = 1,
    STRING = 2,
    ESCAPE = 3,
    COMMENT = 4,


class StateMapNote(object):
    def __init__(self, snt, ways, name="", include_end=False):
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


class CommentFilter(object):
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

    def filter(self, in_file, out_file):
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

                    if ret[0] is not None and ((csn == n and n.type != StateType.COMMENT) or (csn != n and ((n.include_end and n.type != StateType.COMMENT) or (not n.include_end and csn.type != StateType.COMMENT)))):
                        out_file.write(ret[0])

    def load_from_str(self, map_desc):
        pass


def filter_objc_source_file(in_file, out_file):
    _filter = CommentFilter()
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

    _filter.filter(in_file, out_file)


def main():
    if len(argv) < 2:
        print("Please attach code file.\nUsage: 'python3 source_code_process.py in_file_path [out_file_path]'")
        exit(1)

    code_file_path = path.expanduser(argv[1])
    # code_file_path = path.expanduser('~/Documents/TestMachO/TestMachO/AppDelegate.m')

    if len(argv) >= 3:
        out_file_path = path.expanduser(argv[2])
    else:
        in_path_split = path.splitext(code_file_path)
        out_file_path = in_path_split[0] + "_trimmed" + in_path_split[1]

    with open(code_file_path, 'r') as f:
        with open(out_file_path, 'w+') as o:
            filter_objc_source_file(f, o)


if __name__ == "__main__":
    main()
