import os
from geoprob_pipe.utils.other import repository_root_path
from typing import Tuple
from pandas import DataFrame


def get_todo_contents(line: str) -> Tuple[bool, str, str, str, str]:
    line = line[line.find("# TODO")+7:]
    items = line.split(sep=':')
    description = items[1]
    items = items[0].split(sep=' ')
    if items.__len__() >= 4:
        return False, "", "", "", ""
    if items[0].lower() not in ['nu', 'later']:
        return False, "", "", "", ""
    if items[1].lower() not in ['must', 'should', 'could', 'nice']:
        return False, "", "", "", ""
    if items[2].lower() not in ['groot', 'middel', 'klein']:
        return False, "", "", "", ""
    return True, items[0].lower(), items[1].lower(), items[2].lower(), description


def find_todos_in_file(filepath: str, path_to_package: str):
    todos = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
        for lineno, line in enumerate(file, start=1):
            if '# TODO ' not in line:
                continue
            valid, wanneer, belang, formaat, description = get_todo_contents(line=line)
            if not valid:
                continue
            todos.append({
                'bestand': filepath.replace(path_to_package, ""),
                'regel': lineno,
                'line': line,
                'wanneer': wanneer,
                'belang': belang,
                'formaat': formaat,
                'description': description
            })
    return todos


def collect_all_todos():
    todos = []
    repo_root = repository_root_path()
    path_to_package = os.path.join(repo_root, "geoprob_pipe")
    for subdir, _, files in os.walk(path_to_package):
        for file in files:
            if not file.endswith(".py"):
                continue
            path = os.path.join(subdir, file)
            todos.extend(find_todos_in_file(filepath=path, path_to_package=path_to_package))

    df_todos = DataFrame(todos)
    df_todos = df_todos.sort_values(by=['wanneer', 'belang', 'formaat'], ascending=[False, True, True])

    return df_todos



def df_to_markdown(df: DataFrame):
    markdown = "| Wanneer | Belang | Formaat | Beschrijving | Bestand | Regel |\n"
    markdown += "| -- | -- | -- | -- | -- | -- |\n"
    for _, row in df.iterrows():
        markdown += (f"| {row['wanneer']} | {row['belang']} "
                     f"| {row['formaat']} | {str(row['description']).strip()} | {row['bestand']} | {row['regel']} | \n")
    return markdown


def update_readme_with_table():
    start_marker = "<!-- START_TODO_TABLE -->"
    end_marker = "<!-- END_TODO_TABLE --> "

    readme_path = os.path.join(repository_root_path(), "README.md")

    # Construct Markdown table
    df_todos = collect_all_todos()
    markdown = df_to_markdown(df_todos)

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if start_marker not in content or end_marker not in content:
        raise ValueError(f"Markers niet gevonden in het README.md-bestand.")

    new_content = \
        content.split(start_marker)[0] + \
        start_marker + '\n' + \
        markdown + '\n' + \
        end_marker + '\n' + \
        content.split(end_marker)[1]

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

# collection = collect_all_todos()
# df_to_markdown(collection)

update_readme_with_table()
print(f"Finished updating README.")
