"""Output formatting for Fly_in."""

from graph import Graph

COLOR_MAP: dict[str, str] = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "gray": "\033[90m",
    "grey": "\033[90m",
    "cyan": "\033[96m",
    "magenta": "\033[95m",
    "white": "\033[97m",
}

RESET = "\033[0m"


def colorize(token: str, graph: Graph) -> str:
    """
    Color one movement token according to its destination zone color.

    Examples:
        D1-a
        D2-start-r1
    """

    parts = token.split("-")
    if len(parts) < 2:
        return token

    zone_name = parts[-1]
    if zone_name not in graph.zones:
        return token

    zone = graph.zones[zone_name]
    if zone.color is None:
        return token

    ansi = COLOR_MAP.get(zone.color.lower())
    if ansi is None:
        return token

    return f"{ansi}{token}{RESET}"


def print_result(lines: list[str], graph: Graph) -> None:
    """Print simulation output line by line with operational colors."""
    for line in lines:
        tokens = line.split()
        colored_tokens = [colorize(token, graph) for token in tokens]
        print(" ".join(colored_tokens))

# 1. [Reset]
# e.g. "\033[91mD1-r1\033[0m"
# 终端看到这个字符串时，会把 D1-r1 显示成红色，然后恢复默认颜色
# 2. [token] = 被“切出来的一块语法单位”
# 每一块都可以独立分析
# 一个 token = 一个 drone 的一次移动描述
# 3. [each line output]
# 如果：
# tokens = ["D1-r1", "D2-start-r1"]
# 假设 r1 是 red，
# 那么 colored_tokens 可能变成：
# [
#     "\033[91mD1-r1\033[0m",
#     "\033[91mD2-start-r1\033[0m"
# ]
