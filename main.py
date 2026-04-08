import sys
from parser import parse_file
from simulation import simulate
from formatter import print_result


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 main.py map.txt")
        return

    filename: str = sys.argv[1]
    nb_drones, graph = parse_file(filename)
    result: list[str] = simulate(nb_drones, graph)
    print_result(result)


if __name__ == "__main__":
    main()
