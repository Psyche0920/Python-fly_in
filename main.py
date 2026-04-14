"""Program entry point for Fly_in."""

import sys
from parser import parse_file
from simulation import simulate
from formatter import print_result
from ui import FlyUI
DEFAULT_MAP = "default.txt"


def main() -> None:
    """Program entry point for Fly_in."""
    if len(sys.argv) > 3:
        print("Usage: python3 main.py [map.txt] [--ui]")
        return

    filename = DEFAULT_MAP
    use_ui = False

    for arg in sys.argv[1:]:
        if arg == "--ui":
            use_ui = True
        else:
            filename = arg

    try:
        nb_drones, graph = parse_file(filename)
        result: list[str] = simulate(nb_drones, graph)

        if not result:  # dijkstra doesnt work or no path or no start/end
            print("No valid path from start to end.")
            return

        print_result(result, graph)

        if use_ui:
            ui_result = [line for line in result if line.startswith("D")]
            FlyUI(graph, ui_result)

    except ValueError as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
