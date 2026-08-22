from geoprob_pipe.workflow import State
from geoprob_pipe.workflow import steps





def test_workflow(tmp_path):
    state = State(file_dir=tmp_path)
    for obj in steps:
        step = obj(state=state)
        print(f"{step.__name__}: {step.should_run=} {step.completed=}")
        if step.should_run and not step.completed:
            step.execute()
