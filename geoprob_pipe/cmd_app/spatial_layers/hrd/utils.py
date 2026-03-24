
def hrd_file_path(hrd_dir: str) -> str:
    for file in os.listdir(hrd_dir):
        filename = os.fsdecode(file)
        if filename.endswith(".config.sqlite"):
            continue
        if filename.endswith("hlcd.sqlite"):
            continue
        return os.path.join(hrd_dir, filename)
    raise ValueError

