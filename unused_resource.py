
import os
from hashlib import md5
from source_code_process import filter_objc_source_file, StateType
from io import StringIO

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
        hash_md5 = md5()
        with open(file, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        md5_hex = hash_md5.hexdigest()

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


def find_unused_resource_file(project_root_path, resource_exts=default_resource_exts, code_exts=default_code_exts):
    if os.path.isfile(project_root_path):
        print('You should attach a dir, not a file.')
        exit(1)

    resource_files, code_files = find_resource_and_code(project_root_path, resource_exts, code_exts)
    resource_file_names = set([os.path.split(x)[-1] for x in resource_files])

    for code_file in code_files:
        last_string = None
        with open(code_file, 'r') as cf:
            string_file = StringIO()
            filter_objc_source_file(cf, string_file, StateType.STRING)
            for line in string_file:
                if last_string is not None:
                    if (line.startswith('.') and line in resource_exts) or ('.' not in line and ('.' + line) in resource_exts):
                        file_full_name = last_string + line
                        if '.' not in line:
                            file_full_name = last_string + '.' + line

                        if file_full_name in resource_file_names:
                            resource_file_names.remove(file_full_name)
                    elif (last_string + default_resource_ext) in resource_file_names:
                        resource_file_names.remove(last_string + default_resource_ext)

                    last_string = None
                else:
                    possible_file_name = os.path.split(line)[-1]
                    if possible_file_name in resource_file_names:
                        resource_file_names.remove(possible_file_name)
                    else:
                        last_string = line

            string_file.close()

    left_files = [x for x in resource_files if os.path.split(x)[-1] in resource_file_names]

    return left_files


def main():
    # test_path = 'D:/test_scripts'
    # rfs, cfs = find_resource_and_code(test_path)
    # # print(rfs)
    # print(check_same_resource(rfs))
    str_file = StringIO("""
    UIImage *image = [UIImage imageNamed:@"1.png"];
    NSString *fileURL = [NSBundle mainBundle] pathForResource:@"2.png" withType:@""];
    NSString *fileURL = [NSBundle mainBundle] pathForResource:@"2" 
    withType:@"png"];
    NSString *fileURL = [NSBundle mainBundle] pathForResource:@"2"
     withType:@"png"
     customType:123];
    """)
    out_file = StringIO()
    filter_objc_source_file(str_file, out_file, StateType.STRING)
    out_file.seek(0)
    print(out_file.read())
    str_file.close()
    out_file.close()


if __name__ == '__main__':
    main()