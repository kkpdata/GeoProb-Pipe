from typing import Tuple
from pandas import DataFrame
import os
from git import Repo, InvalidGitRepositoryError
from typing import Optional


def repository_root_path() -> Optional[str]:

    # Bold guess, it is the execution path
    base_dir = os.getcwd()
    try:
        repo_root = Repo(base_dir, search_parent_directories=False).working_tree_dir
        return repo_root
    except InvalidGitRepositoryError:
        pass

    # Otherwise, search subdirectories
    for subdir, dirs, files in os.walk(os.getcwd()):
        for directory in dirs:
            try:
                repo = Repo(os.path.join(subdir, directory), search_parent_directories=False)
                return repo.working_tree_dir
            except InvalidGitRepositoryError:
                continue
        return None
    return None


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
    markdown = "| Belang | Formaat | Beschrijving | Bestand | Regel |\n"
    markdown += "| -- | -- | -- | -- | -- |\n"
    for _, row in df.iterrows():
        markdown += (f"| {row['belang']} | {row['formaat']} | {str(row['description']).strip()} "
                     f"| {row['bestand']} | {row['regel']} | \n")
    return markdown


def update_readme_with_table(wanneer: str = "nu"):
    start_marker = f"<!-- START_TODO_TABLE_{wanneer.upper()} -->"
    end_marker = f"<!-- END_TODO_TABLE_{wanneer.upper()} --> "

    readme_path = os.path.join(repository_root_path(), "README.md")

    # Construct Markdown table
    df_todos = collect_all_todos()
    df_todos = df_todos[df_todos['wanneer'] == wanneer]
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


update_readme_with_table(wanneer='nu')
update_readme_with_table(wanneer='later')
print(f"Finished updating README.")
