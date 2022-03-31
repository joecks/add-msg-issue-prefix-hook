#!/usr/bin/env python3

import argparse
import sys
import re
import subprocess

def FileCheck(fn):
    try:
      open(fn, "r+")
      return True
    except IOError:
      return False

class ArgumentException(Exception):
    pass

def get_ticket_id_from_branch_name(branch):
    matches = re.findall('[a-zA-Z]{1,10}-[0-9]{1,5}', branch)
    if len(matches) > 0:
        return matches[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("commit_msg_filepath")
    parser.add_argument(
        '-t', '--template', default="[{}]",
        help='Template to render ticket id into',
    )
    args = parser.parse_args()
    commit_msg_filepath = args.commit_msg_filepath
    template = args.template

    branch = ""
    try:
        branch = subprocess.check_output(["git","symbolic-ref", "--short", "HEAD"], universal_newlines=True).strip()
    except Exception as e:
        print(e)

    result = get_ticket_id_from_branch_name(branch)
    issue_number = ""

    if result:
        issue_number = result.upper()

    file_path_gitgui = commit_msg_filepath.replace("COMMIT_EDITMSG", "GITGUI_MSG")
    file_path = ""
    if FileCheck(commit_msg_filepath):
        file_path = commit_msg_filepath
    elif FileCheck(file_path_gitgui):
        file_path = file_path_gitgui
    else :
        raise ArgumentException(f"Can not open {commit_msg_filepath} and {file_path_gitgui}")

    with open(file_path, "r+") as f:
        content = f.read()
        content_subject = content.split("\n", maxsplit=1)[0].strip()
        f.seek(0, 0)
        if issue_number and issue_number not in content_subject:
            prefix = template.format(issue_number)
            f.write("{} {}".format(prefix, content))
        else:
            f.write(content)


if __name__ == "__main__":
    exit(main())


