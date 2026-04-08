from collections import deque
from graph import Graph


class Drone:
    def __init__(self, drone_id: int, start: str) -> None:
        self.id: int = drone_id
        self.pos: str = start
        self.path: list[str] = []
        self.delivered: bool = False

        # restricted zone 用到的飞行状态
        self.in_transit: bool = False
        self.transit_target: str | None = None
        self.transit_from: str | None = None
        self.remaining_turns: int = 0


def bfs(graph: Graph) -> list[str]:
    if graph.start is None or graph.end is None:
        return []

    queue: deque[tuple[str, list[str]]] = deque([(graph.start, [])])
    visited: set[str] = set()

    while queue:
        node, path = queue.popleft()
        # from queue out start, [] //a, [start]//a1, start+a//end, start+a+a1

        if node == graph.end:
            return path + [node]  # start+a+a1+end

        if node in visited:
            # if visited, continue to the next queue element avoid intertwining
            continue

        visited.add(node)

        for nxt in graph.adj[node]:  # from adj to queue
            zone = graph.zones[nxt]
            if zone.zone_type != "blocked":
                queue.append((nxt, path + [node]))
                # a, start//a1, start+a//end, start+a+a1
    return []


def zone_capacity(graph: Graph, zone_name: str) -> int:
    if zone_name == graph.start or zone_name == graph.end:
        return 10**9  # set unlimited
    return graph.zones[zone_name].max_drones


def simulate(nb_drones: int, graph: Graph) -> list[str]:
    """
    Input: nb_drones：无人机数量, graph：地图
    Output: list[str]：每一回合的输出行
    """
    if graph.start is None or graph.end is None:
        return []

    # 一次性创建所有 drone 对象, 开始都在 graph.start
    drones: list[Drone] = [Drone(i + 1, graph.start) for i in range(nb_drones)]

    # 先找出一条从 start 到 end 的路径
    # 如果找不到，直接返回空结果
    # 然后把同一条路径分给每架 drone
    # path[1:] 是为了去掉开头的 start
    path: list[str] = bfs(graph)
    if not path:
        return []  # BFS 可能找不到路
    for drone in drones:
        drone.path = path[1:]

    results: list[str] = []

    while True:
        moves: list[str] = []
        arrived_this_turn: set[int] = set()

        # 当前各 zone 有多少 drone
        current_occupancy: dict[str, int] = {}
        for drone in drones:
            if drone.delivered:
                continue
            if drone.in_transit:
                continue
            current_occupancy[drone.pos] = current_occupancy.get(drone.pos,
                                                                 0) + 1

        # 本回合预约进入 zone 的数量
        incoming: dict[str, int] = {}

        # 本回合使用 connection 的数量
        link_usage: dict[frozenset[str], int] = {}
        #         因为 connection 是双向的。
        # frozenset({"a", "b"}) 和 frozenset({"b", "a"}) 是一样的，所以很适合表示一条无向边。

        # 这个变量专门用来防止死循环
        moved_this_turn = 0
        # 如果这一回合没有任何 drone 成功移动，那说明程序卡住了。
        # 如果不 break，就可能一直 while 下去

        # ----------------------------
        # 阶段 1：先处理正在 transit 的 drone
        # ----------------------------
        for drone in drones:
            if drone.delivered:  # 因为已经到终点的 drone 不应该继续参与调度。
                continue

            if not drone.in_transit:
                continue

            drone.remaining_turns -= 1

            if drone.remaining_turns == 0:
                target = drone.transit_target
                if target is None:  # defensive, should not normally
                    continue

                # 到达 restricted zone
                drone.pos = target
                drone.in_transit = False
                drone.transit_target = None
                drone.transit_from = None

                # 本回合各 zone 已预约进入多少架
                incoming[target] = incoming.get(target, 0) + 1
                current_occupancy[target] = (
                    current_occupancy.get(target, 0) + 1
                )
                arrived_this_turn.add(drone.id)
                moves.append(f"D{drone.id}-{target}")
                moved_this_turn += 1

                if drone.pos == graph.end and not drone.path:
                    drone.delivered = True

        # ----------------------------
        # 阶段 2：处理普通可行动 drone
        # ----------------------------
        for drone in drones:
            if drone.delivered:
                continue

            if drone.in_transit:
                continue

            # 本回合刚落地的 drone，不允许同回合再移动
            if drone.id in arrived_this_turn:
                continue

            if not drone.path:
                if drone.pos == graph.end:
                    drone.delivered = True
                continue

            next_zone: str = drone.path[0]
            next_zone_obj = graph.zones[next_zone]

            # blocked zone 不能进
            if next_zone_obj.zone_type == "blocked":
                continue

            # 检查 connection capacity
            link_key = frozenset({drone.pos, next_zone})
            used = link_usage.get(link_key, 0)
            capacity = graph.get_link_capacity(drone.pos, next_zone)
            if used >= capacity:
                continue  # defensive

            # 检查目标 zone 容量
            cap = zone_capacity(graph, next_zone)
            now_inside = current_occupancy.get(next_zone, 0)
            already_reserved = incoming.get(next_zone, 0)

            if now_inside + already_reserved >= cap:
                continue

            # restricted: 进入需要两回合
            if next_zone_obj.zone_type == "restricted":
                drone.path.pop(0)

                # 离开当前 zone
                current_occupancy[drone.pos] -= 1

                drone.in_transit = True
                drone.transit_from = drone.pos
                drone.transit_target = next_zone
                drone.remaining_turns = 1

                link_usage[link_key] = used + 1
                moves.append(f"D{drone.id}-{drone.pos}-{next_zone}")
                moved_this_turn += 1
                continue

            # normal / priority: 本回合直接进入
            drone.path.pop(0)
            current_occupancy[drone.pos] -= 1
            drone.pos = next_zone

            incoming[next_zone] = incoming.get(next_zone, 0) + 1
            link_usage[link_key] = used + 1

            moves.append(f"D{drone.id}-{next_zone}")
            moved_this_turn += 1

            if drone.pos == graph.end and not drone.path:
                drone.delivered = True

        if moves:
            results.append(" ".join(moves))

        # 全部送达
        if all(drone.delivered for drone in drones):
            break

        # 没人能动，避免死循环
        if moved_this_turn == 0:
            break

    return results


# [v3 change-list]
# [1. 给 Drone 加了 4 个字段]
# self.in_transit: bool = False
# self.transit_target: str | None = None
# self.transit_from: str | None = None
# self.remaining_turns: int = 0
# [作用：]
# in_transit：这架 drone 现在是不是在飞行中
# transit_target：飞向哪个 restricted zone
# transit_from：从哪里起飞
# remaining_turns：还要几回合才能落地

# 2. 把每回合拆成两阶段
# [阶段 1]
# 先处理“上一回合已经进入 restricted 通道”的 drone。
# 它们这回合会：
# remaining_turns -= 1
# 如果变成 0，就正式到达目标 zone
# 输出：
# D1-r1
# [阶段 2]
# 再处理普通 drone：
# normal / priority：直接进入
# restricted：不直接落地，而是进入 transit 状态，输出 connection 形式
# [例如：]
# D1-start-r1
# 下一回合才会输出：
# D1-r1


# Q1: restricted = drone 在 connection 上“飞 2 回合”，期间一直占用这条边
# towards restricted zone： two turns
# 回合 1
# 进入 transit
# remaining_turns = 1
# 输出连接
# 回合 2
# remaining_turns -= 1
# 变成 0
# 正式到达 restricted zone
# 输出 zone 名

# Q2: BFS 的“先后顺序”来源于：
# parser.py 读取 connection 的顺序
# graph.add_connection() 往 adj 列表里 append 的顺序
# BFS 按这个顺序遍历邻居

# Q3: incoming[target] = incoming.get(target, 0) + 1 到底是什么意思？
# incoming 表示：
# 本回合已经被安排进入这个 zone 的 drone 数量
