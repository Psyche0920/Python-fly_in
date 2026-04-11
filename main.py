"""Program entry point for Fly_in."""

import sys
from parser import parse_file
from simulation import simulate
from formatter import print_result
from ui import FlyUI


def main() -> None:
    """Program entry point for Fly_in."""
    if len(sys.argv) not in {2, 3}:
        print("Usage: python3 main.py map.txt [--ui]")
        return

    filename: str = sys.argv[1]
    use_ui = len(sys.argv) == 3 and sys.argv[2] == "--ui"

    try:
        nb_drones, graph = parse_file(filename)
        result: list[str] = simulate(nb_drones, graph)

        if not result:  # bfs doesnt work or no path or no start/end
            print("No valid path from start to end.")
            return

        # formatter now needs graph for colors
        print_result(result, graph)

        # UI
        if use_ui:

            FlyUI(graph, result)

    except ValueError as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
