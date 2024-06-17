__version__ = "0.0.1"

from functools import wraps


from pydantic_config.parse import parse_argv
from pydantic import BaseModel as PydanticBaseModel, ValidationError
from pydantic import validate_call as pydantic_validate_call
from pydantic import ConfigDict

from rich import print as rich_print
from rich.panel import Panel
from rich import box


class BaseConfig(PydanticBaseModel):
    model_config = ConfigDict(extra="forbid")


def _recreate_cli_arg(loc: list[str]) -> str:
    cli_cmd = "--" + ".".join(loc)
    cli_cmd = cli_cmd.replace("_", "-")
    return cli_cmd


def _get_error_panel(error: str, n_errors: int) -> Panel:
    # inspired from cyclopts https://github.com/BrianPugh/cyclopts/blob/a6489e6f6e7e1b555c614f2fa93a13191718d44b/cyclopts/exceptions.py#L318
    return Panel(
        error,
        title=f"{n_errors} errors",
        box=box.ROUNDED,
        expand=True,
        title_align="left",
        style="red",
    )


@wraps(pydantic_validate_call)
def validate_call(*args, **kwargs):
    inner_wrapper = pydantic_validate_call(*args, **kwargs)

    def wrapper(*args, **kwargs):
        try:
            return inner_wrapper(*args, **kwargs)
        except ValidationError as e:
            msg = ""
            n_errors = len(e.errors())
            for error in e.errors():
                if msg != "":
                    msg += "\n"
                msg += f"[white][bold]{_recreate_cli_arg(error['loc'])}[/bold] is not a valid cli argument[/white]"

            panel = _get_error_panel(msg, n_errors)

            rich_print(panel)
            exit(code=1)

    return wrapper


__all__ = ["parse_argv", "BaseConfig", "validate_call"]
