import os
from geoprob_pipe.utils.other import repository_root_path
from typing import Tuple
from pandas import DataFrame


def get_todo_contents(line: str) -> Tuple[bool, str, str, str, str]:
    line = line[line.find("# TODO")+7:]
    items = line.split(sep=':')
    description = items[1]
    print(f"{items[0]=}")
    items = items[0].split(sep=' ')
    if items.__len__() >= 4:
        print(f"length issue")
        return False, "", "", "", ""
    if items[0].lower() not in ['nu', 'later']:
        print(f"nu later issue")
        return False, "", "", "", ""
    if items[1].lower() not in ['must', 'should', 'could', 'nice']:
        print(f"prio issue")
        return False, "", "", "", ""
    if items[2].lower() not in ['groot', 'middel', 'klein']:
        print(f"size issue")
        return False, "", "", "", ""
    return True, items[0].lower(), items[1].lower(), items[2].lower(), description


def find_todos_in_file(filepath):
    todos = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
        for lineno, line in enumerate(file, start=1):
            if '# TODO ' not in line:
                continue
            valid, when, priority, size, description = get_todo_contents(line=line)
            if not valid:
                continue
            todos.append({
                'bestand': filepath,
                'regel': lineno,
                'line': line,
                'when': when,
                'priority': priority,
                'size': size,
                'description': description
            })
    return todos


def collect_all_todos():
    todos = []
    repo_root = repository_root_path()
    for subdir, _, files in os.walk(repo_root):
        for file in files:
            if not file.endswith(".py"):
                continue
            path = os.path.join(subdir, file)
            print(f"Now exploring file: {path}")
            todos.extend(find_todos_in_file(path))

    df_todos = DataFrame(todos)
    df_todos = df_todos.sort_values(by=['when', 'priority', 'size'], ascending=[False, True, True])

    return df_todos


collection = collect_all_todos()
