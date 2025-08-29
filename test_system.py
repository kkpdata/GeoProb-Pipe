

def test_system():

    ##

    from repo_utils.utils import repository_root_path
    from geoprob_pipe import GeoProbPipe
    import os
    repo_root = repository_root_path()
    workspace_path = os.path.join(repo_root, "workspaces", "traject_224")
    project = GeoProbPipe(workspace_path)
    project.export_archive()

    ##
