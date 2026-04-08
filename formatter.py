"""Output formatting for Fly_in."""


def print_result(lines: list[str]) -> None:
    """Print simulation output line by line."""
    for line in lines:
        print(line)


# print_result([
#     "D1-a D2-a",
#     "D1-b D2-b",
#     "D1-end D2-end"
# ])
