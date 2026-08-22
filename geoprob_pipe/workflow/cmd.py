from geoprob_pipe.workflow import steps, State
import typer


state = State(file_path=r"C:\Users\CP\Downloads\false_fix\tmp.gpkg")

app = typer.Typer(help="GeoProb-Pipe - CLI applicatie voor probabilistische piping berekeningen.", add_completion=False)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """ Default entry point for `geoprob-pipe`. Runs when no subcommand is specified. """
    if ctx.invoked_subcommand is None:
        for obj in steps:
            step = obj(state=state)
            print(f"{step.label}: {step.should_run=} {step.completed=}")
            if step.should_run and not step.completed:
                step.execute()


if __name__ == "__main__":
    app()
