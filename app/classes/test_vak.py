
def test_vak_collection():

    ##
    from app.classes.vak import VakCollection
    from pandas import read_excel
    from app.classes.workspace import Workspace
    from app.helper_functions.utils import repository_root_path
    import os

    assert 1+1 == 2

    repo_root = repository_root_path()
    workspace_path = os.path.join(repo_root, "workspaces", "example_new_calculations")
    workspace = Workspace(workspace_path)
    df_overview_parameters = read_excel(
        workspace.input.folderpath / "input.xlsx", sheet_name="Overzicht_parameters", index_col=0, header=0).rename(
        columns=lambda x: x.strip())
    df_vakken = read_excel(workspace.input.folderpath / "input.xlsx", sheet_name="Vakken").rename(
        columns=lambda x: x.strip())
    # noinspection PyUnusedLocal
    vak_collection = VakCollection(df_vakken, df_overview_parameters)

    ##
