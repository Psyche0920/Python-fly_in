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


def zone_capacity(graph: Graph, zone_name: str) -> int:
    if zone_name == graph.start or zone_name == graph.end:
        return 10**9  # ???
    return graph.zones[zone_name].max_drones


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
    if not path:
        return []  # BFS 可能找不到路

    for drone in drones:
        drone.path = path[1:]

    results: list[str] = []

    while True:
        moves: list[str] = []
        # finished: int = 0
        # 当前各 zone 有多少 drone
        current_occupancy: dict[str, int] = {}
        for drone in drones:
            if drone.delivered:  # ??? why jump if delivered? delivered=finished at the destination? why not count at the destination hub
                continue
            if drone.in_transit:  # means not in any pos? so no counting?
                continue
            current_occupancy[drone.pos] = current_occupancy.get(drone.pos,
                                                                 0) + 1

        # 本回合预约进入 zone 的数量
        incoming: dict[str, int] = {}

        # 本回合使用 connection 的数量
        link_usage: dict[frozenset[str], int] = {}  # ??? what is this

        moved_this_turn = 0
        # 这个变量专门用来防止死循环。
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
                if target is None:  # what does this mean. already finish transit? why after reaiming_turns -=1
                    continue

                # 到达 restricted zone
                drone.pos = target
                drone.in_transit = False
                drone.transit_target = None
                drone.transit_from = None

                incoming[target] = incoming.get(target, 0) + 1
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
            if not drone.path:
                if drones.pos == graph.end:
                    drone.delivered = True
                continue
            next_zone: str = drone.path[0]

            if not drone.path:
                # 已经到终点路径为空
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
                continue  # means wait until next round? but why >?

            # 检查目标 zone 容量
            cap = zone_capacity(graph, next_zone)
            now_inside = current_occupancy.get(next_zone, 0)
            already_reserved = incoming.get(next_zone, 0)

            if now_inside + already_reserved >= cap:
                continue

            # # restricted: 进入需要两回合
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

# v2:“改动清单”
# graph.py

# 新增：

# self.links

# add_connection(..., capacity=1)

# 重复 connection 检查

# get_link_capacity()

# parser.py

# 修改：

# connection 段读取 max_link_capacity

# simulation.py

# 新增：

# delivered

# zone_capacity()

# current_occupancy

# incoming

# link_usage

# moved_this_turn

# zone / edge capacity 检查

# waiting 逻辑


# [Questions]
# 1.

# current_occupancy.get(..., 0) + 1 不是永远 1，而是在原有数量上加 1。

# 2.

# continue = 跳过这次，去下一个
# break = 整个循环结束
# exit/quit = 程序结束

# 3.

# if now_inside + already_reserved >= cap: continue
# 表示目标 zone 满了，这个 drone 这回合不能进去，只能等。
# 即使里面的人会走，你现在这个简化写法也还是先保守检查
# a. now_inside+already reserved
# 你现在这套逻辑是比较保守的规则层：
# 先看当前占用
# 再看本轮已预约进入
# 满了就不让进
# 这能保证不会超容量。
# b. continue:
# 结束它在这一轮的处理，马上去处理下一个 drone。
# 等 for drone in drones 全部跑完，这一轮就结束了。
# 然后外层 while True 开始下一轮，这个 drone 才会再次被处理。
# 所以不是“永远不处理了”，而是：
# 这一轮不动，下一轮再试

# 4.
# if drone.pos == graph.end and not drone.path
# 表示“已经到终点，而且后面没有剩余路径”，才算真正送达。
# 对于你当前阶段：
# 只写 if drone.pos == graph.end: 也能跑
# 忘了 pop，短期内也可能看不出坏结果
# 但是：
# 这属于“被掩盖的 bug”
# 以后一旦你依赖 path，就会出问题
# 所以最好保持状态一致


# 5.
# 会卡死是因为 while True 还在跑，但没有任何 drone 能移动，状态永远不变。
# BFS 一般会尽量避开 blocked zone。原始 bfs 里已经有 blocked 检查。
# 但如果别的逻辑有问题，或者路径根本无效，drone 可能永远过不去。
