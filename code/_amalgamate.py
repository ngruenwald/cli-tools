#!/usr/bin/env python3

import glob
import regex

INPUT_PATH = "code/"

INPUT_FILES = [
   f"{INPUT_PATH}*.py"
]

GLOB_RECURSIVE = True

TEMPLATE_FILE = f"{INPUT_PATH}clitools.tpl.py"

OUTPUT_FILE = "clitools.py"

INPUT_DATA = {}

EXCLUDE = False

BLOCK_BEGIN = regex.compile("^\\s*#\\s*>>\\s*(.*)$")
BLOCK_END = regex.compile("^\\s*#\\s*<<\\s*(.*)$")

COMMENT_FILE = "# source: {}\n"
COMMENT_FILE_LINE = "# source: {}:{}\n"


def extract_data_from_file_include(input_file: str, data: dict) -> None:
    with open(input_file, "rt") as f:
        block_name: str = ""
        block_data: list[str] = []
        line_number: int = 0
        while True:
            line = f.readline()
            if not line:
                if block_name:
                    print(f"WARN: eol while in block '{block_name}'")
                break
            line_number += 1
            if block_name:
                # inside a block, check for blockend
                m = BLOCK_END.match(line)
                if m:
                    # TBD: should we verify the block name?
                    if block_name in data:
                        data[block_name].append("\n")
                        data[block_name].extend(block_data)
                    else:
                        data[block_name] = block_data
                    block_name = ""
                else:
                    block_data.append(line)
            else:
                # outside of block, check for block start
                m = BLOCK_BEGIN.match(line)
                if m:
                    block_name = m.group(1).strip()
                    block_data = [COMMENT_FILE_LINE.format(input_file, line_number)]


def extract_data_from_file_exclude(input_file: str, data: dict) -> None:
    with open(input_file, "rt") as f:
        block_data: list[str] = []
        line_number: int = 0
        include_line = True
        while True:
            line = f.readline()
            if not line:
                if not include_line:
                    print(f"WARN: eol while in block")
                break
            line_number += 1
            if include_line:
                # inside of block, check for block end
                m = BLOCK_END.match(line)
                if m:
                    include_line = False
            else:
                # outside a block, check for block start
                m = BLOCK_BEGIN.match(line)
                if m:
                    include_line = True
                else:
                    block_data.append(line)
        if block_data:
            data[""].append("\n")
            data[""].append(COMMENT_FILE.format(input_file))
            data[""].extend(block_data)


def extract_data_from_file(input_file: str, data: dict) -> None:
    print(f"processing '{input_file}'")
    if EXCLUDE:
        extract_data_from_file_exclude(input_file, data)
    else:
        extract_data_from_file_include(input_file, data)


def gather_input_data(input_files: list[str], data: dict) -> None:
    for input_file in input_files:
        files = glob.glob(input_file, recursive=GLOB_RECURSIVE)
        files.sort()
        for file in files:
            extract_data_from_file(file, data)


def create_output_file(output_file: str, template_file: str, data: dict) -> None:
    match_ins = regex.compile("^\\s*#\\s*\\$\\$\\s*(.*)$")
    output_data = []
    used_blocks = []
    with open(template_file, "rt") as f:
        while True:
            line = f.readline()
            if not line:
                break
            m = match_ins.match(line)
            if not m:
                output_data.append(line)
                continue
            block_name = m.group(1).strip()
            if not block_name in data:
                print(f"WARN: block '{block_name}' does not exist")
                continue
            output_data.extend(data[block_name])
            used_blocks.append(block_name)
    with open(output_file, "wt") as f:
        f.writelines(output_data)
    unused_blocks = set(data.keys()) - set(used_blocks)
    if unused_blocks:
        print(f"WARN: unused blocks: {unused_blocks}")


gather_input_data(INPUT_FILES, INPUT_DATA)
create_output_file(OUTPUT_FILE, TEMPLATE_FILE, INPUT_DATA)
