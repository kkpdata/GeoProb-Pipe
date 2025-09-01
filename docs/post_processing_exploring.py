import os
import inflection
from bs4 import BeautifulSoup
from typing import Optional


def should_be_reformatted(value: Optional[str]) -> bool:
    if value is None:
        return False
    if "geoprob_pipe" not in value:
        return False
    if value.split(sep='.').__len__() <= 1:
        return False
    return True

def reformat(value: str):
    return inflection.humanize(value.split(sep='.')[-1])


def simplify_anchor_text_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    changed = False

    # Strings
    for a in soup.find_all('a'):
        if not should_be_reformatted(a.string):
            continue
        a.string = reformat(a.string)
        changed = True

    # For navigation items
    for nav in soup.find_all('div', {'role': 'navigation'}):
        for li in nav.find_all('li', class_='breadcrumb-item active'):
            if not should_be_reformatted(li.string):
                continue
            li.string = reformat(li.string)
            changed = True

    if changed:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(str(soup))


for root, _, files in os.walk(r"C:\Users\CP\git_clones\GeoProb-Pipe\GeoProb-PipeV2\GeoProb-Pipe\docs\_build\html"):
    for filename in files:
        if filename.endswith('.html'):
            file_path = os.path.join(root, filename)
            simplify_anchor_text_in_file(file_path)
