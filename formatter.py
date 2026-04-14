"""Output formatting for Fly_in."""

from graph import Graph


def print_result(lines: list[str], graph: Graph) -> None:
    """Print simulation output line by line with operational colors."""
    for line in lines:
        print(line)
