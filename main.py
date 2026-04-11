"""Program entry point for Fly_in."""

import sys
from parser import parse_file
from simulation import simulate
from formatter import print_result


def main() -> None:
    """Program entry point for Fly_in."""
    if len(sys.argv) != 2:
        print("Usage: python3 main.py map.txt")
        return

    filename: str = sys.argv[1]

    try:
        nb_drones, graph = parse_file(filename)
        result: list[str] = simulate(nb_drones, graph)

        #  clearer message for disconnected / unsolved maps
        if not result:
            print("No valid path from start to end.")

        # formatter now needs graph for colors
        print_result(result, graph)

    except ValueError as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
