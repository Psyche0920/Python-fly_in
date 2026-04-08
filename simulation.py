from collections import deque
from graph import Graph


class Drone:
    def __init__(self, drone_id: int, start: str) -> None:
        self.id: int = drone_id
        self.pos: str = start
        self.path: list[str] = []


def bfs(graph: Graph) -> list[str]:
    if graph.start is None or graph.end is None:
        return []

    queue: deque[tuple[str, list[str]]] = deque([(graph.start, [])])
    visited: set[str] = set()

    while queue:
        node, path = queue.popleft()  # from queue out

        if node == graph.end:
            return path + [node]

        if node in visited:
            # if visited, continue to the next queue element avoid intertwining
            continue

        visited.add(node)

        for nxt in graph.adj[node]:  # from adj to queue
            zone = graph.zones[nxt]
            if zone.zone_type != "blocked":
                queue.append((nxt, path + [node]))
    return []


def simulate(nb_drones: int, graph: Graph) -> list[str]:
    """
    Input: nb_drones：无人机数量, graph：地图
    Output: list[str]：每一回合的输出行
    """
    if graph.start is None:
        return []

    # 一次性创建所有 drone 对象。
    drones: list[Drone] = [Drone(i + 1, graph.start) for i in range(nb_drones)]
    # nb_drones input is zero?

    path: list[str] = bfs(graph)

    for drone in drones:
        drone.path = path[1:]

    results: list[str] = []

    while True:
        moves: list[str] = []
        finished: int = 0

        for drone in drones:
            if not drone.path:
                finished += 1
                continue

            next_zone: str = drone.path.pop(0)
            moves.append(f"D{drone.id}-{next_zone}")
            drone.pos = next_zone

        if moves:
            results.append(" ".join(moves))

        if finished == nb_drones:
            break

    return results
