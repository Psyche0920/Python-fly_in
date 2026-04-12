import heapq  # whats the use why use this, heap??? list???
from graph import Graph


class Drone:
    """Represents one drone moving through the graph."""
    def __init__(self, drone_id: int, start: str) -> None:
        self.id: int = drone_id
        self.pos: str = start
        self.path: list[str] = []
        self.delivered: bool = False

        # Transit state for restricted zones.
        self.in_transit: bool = False
        self.transit_target: str | None = None
        self.transit_from: str | None = None
        self.remaining_turns: int = 0


def zone_move_cost(graph: Graph, zone_name: str) -> int:
    """Return the cost to enter a zone."""
    zone = graph.zones[zone_name]
    if zone.zone_type == "restricted":
        return 2
    return 1


def zone_priority_rank(graph: Graph, zone_name: str) -> int:
    """Return tie-break rank for a zone."""
    zone = graph.zones[zone_name]
    if zone.zone_type == "priority":
        return 0
    return 1
# tie-break = 当两个选择一样好时，用一个规则决定选谁


def dijkstra(graph: Graph) -> list[str]:
    """
    Return the lowest-cost path from start to end.
    Rules:
        - blocked zones are skipped
        - restricted zones cost 2
        - normal and priority zones cost 1
        - priority zones win ties
    """
    if graph.start is None or graph.end is None:
        return []

    # priority queque: total cost, priority score, current zone, path
    heap: list[tuple[int, int, str, list[str]]] = []

    # push start into heap
    heapq.heappush(heap, (0, 0, graph.start, [graph.start]))

    # record the best-seen sate of each zone
    # key: zone name
    # value: (cost, priority_score)
    best_seen: dict[str, tuple[int, int]] = {
        graph.start: (0, 0)
    }

    # if heap not empty, continue searching
    while heap:

        # take out the best state
        # according to first minimum cost, second priority_score
        total_cost, priority_score, current_zone, path = heapq.heappop(heap)

        # if already the end, return the path
        # coz it's the best path under the current rule
        if current_zone == graph.end:
            return path

        recorded = best_seen.get(current_zone)
        if recorded is not None and (total_cost, priority_score) > recorded:
            continue

        for neighbor in graph.adj[current_zone]:
            zone = graph.zones[neighbor]
            if zone.zone_type == "blocked":
                continue
            new_cost = total_cost + zone_move_cost(graph, neighbor)
            new_priority = priority_score + zone_priority_rank(graph, neighbor)
            new_state = (new_cost, new_priority)
            previous_best = best_seen.get(neighbor)
            if previous_best is not None and new_state >= previous_best:
                continue
            best_seen[neighbor] = new_state
            heapq.heappush(
                heap,
                (new_cost, new_priority, neighbor, path + [neighbor])
            )
    # if all paths tried, still cannot reach end
    return []


def zone_capacity(graph: Graph, zone_name: str) -> int:
    """
    Return the effective capacity of a zone.

    Start and end are treated as practically unlimited
    in this simplified model.
    """
    if zone_name == graph.start or zone_name == graph.end:
        return 10**9  # set unlimited
    return graph.zones[zone_name].max_drones


def simulate(nb_drones: int, graph: Graph) -> list[str]:
    """
        Simulate drone movements turn by turn.

        Notes:
            - All drones initially share the same Dijkstra path.
            - Zone capacity and connection capacity are enforced.
            - Restricted zones take two turns:
            1) enter transit
            2) arrive on the next turn(if transit)
        """
    if graph.start is None or graph.end is None:
        return []

    drones: list[Drone] = [Drone(i + 1, graph.start) for i in range(nb_drones)]

    path: list[str] = dijkstra(graph)
    if not path:
        return []

    # Remove the initial start zone so turn 1 does not print "start".
    for drone in drones:
        drone.path = path[1:]

    results: list[str] = []

    while True:
        moves: list[str] = []
        arrived_this_turn: set[int] = set()

        # How many drones in the current zones- Real Time
        current_occupancy: dict[str, int] = {}
        for drone in drones:
            if drone.delivered:
                continue
            if drone.in_transit:
                continue
            current_occupancy[drone.pos] = current_occupancy.get(drone.pos,
                                                                 0) + 1

        # How many drones have already used a connection [this turn.
        link_usage: dict[frozenset[str], int] = {}

        # if no move, to break the while true deadlock
        moved_this_turn = 0

        # ----------------------------
        #  Phase 1: finish transit for drones that were already flying.
        # ----------------------------
        for drone in drones:
            if drone.delivered:
                continue

            if not drone.in_transit:
                continue

            drone.remaining_turns -= 1

            if drone.remaining_turns == 0:
                target_zone = drone.transit_target
                if target_zone is None:  # defensive, should not normally
                    continue

                # arrived restricted zone
                drone.pos = target_zone
                drone.in_transit = False
                drone.transit_target = None
                drone.transit_from = None

                # CHANGED: drone has alre arved, so update real occupancy only
                current_occupancy[target_zone] = (
                    current_occupancy.get(target_zone, 0) + 1
                )
                arrived_this_turn.add(drone.id)
                moves.append(f"D{drone.id}-{target_zone}")
                moved_this_turn += 1

                if drone.pos == graph.end and not drone.path:
                    drone.delivered = True

        # ----------------------------
        # Phase 2: process normal drones that can act this turn.
        # ----------------------------
        for drone in drones:
            if drone.delivered:
                continue

            if drone.in_transit:
                continue

            # A drone (just landed/transited) this turn cannot move again imme.
            if drone.id in arrived_this_turn:
                continue

            if not drone.path:
                if drone.pos == graph.end:
                    drone.delivered = True
                continue

            target_zone = drone.path[0]
            next_zone_obj = graph.zones[target_zone]

            # blocked zone cannot be entered
            if next_zone_obj.zone_type == "blocked":
                continue

            # check connection capacity
            link_key = frozenset({drone.pos, target_zone})
            used = link_usage.get(link_key, 0)
            capacity = graph.get_link_capacity(drone.pos, target_zone)
            if used >= capacity:
                continue  # defensive

            # check zone capacity
            cap = zone_capacity(graph, target_zone)
            now_inside = current_occupancy.get(target_zone, 0)
            if now_inside >= cap:
                continue

            # restricted: need to hold for two turns
            if next_zone_obj.zone_type == "restricted":
                old_pos = drone.pos
                drone.path.pop(0)

                # left old zone
                current_occupancy[old_pos] -= 1

                # enter transit mode
                drone.in_transit = True
                drone.transit_from = old_pos
                drone.transit_target = target_zone
                drone.remaining_turns = 1

                link_usage[link_key] = used + 1
                moves.append(f"D{drone.id}-{old_pos}-{target_zone}")
                moved_this_turn += 1
                continue

            # normal / priority: this turn enter directly
            old_pos = drone.pos
            drone.path.pop(0)
            # left old zone
            current_occupancy[old_pos] -= 1

            # enter target zone
            drone.pos = target_zone
            current_occupancy[target_zone] = (
                current_occupancy.get(target_zone, 0) + 1
            )
            link_usage[link_key] = used + 1
            moves.append(f"D{drone.id}-{target_zone}")
            moved_this_turn += 1

            if drone.pos == graph.end and not drone.path:
                drone.delivered = True

        if moves:
            results.append(" ".join(moves))

        # all arrived
        if all(drone.delivered for drone in drones):
            break

        # no move deadlock-break
        if moved_this_turn == 0:
            break

    return results

# [v5]
# a. dijkstra
# 这个函数使用 Dijkstra 算法在图中寻找从 start 到 end 的最低总代价路径。
# 我用一个最小堆来维护候选状态，每个状态包含当前总代价、priority 的辅助分数、当前节点和整条路径。
# 每次我都会先取出总代价最小的状态进行扩展。
# 如果遇到 blocked zone，我会直接跳过。
# 如果进入 restricted zone，路径代价会加 2；进入 normal 或 priority zone，代价加 1。
# 当两条路径总代价一样时，我再用 priority score 作为第二比较标准，让经过 priority zone 的路径更优先。
# best_seen 用来记录到每个节点目前看到的最佳状态，避免重复扩展更差的状态。
# 当我第一次从堆里取出 end 时，就可以返回当前路径，因为它已经是当前规则下的最佳路径。
# 最容易被问到的 4 个点
# 1. 为什么 priority 是 0？
# 不是说它 cost 是 0。
# 而是说它在 tie-break 里更优。
# movement cost 还是 1。
# 这个要分清。

# 2. 为什么 path + [neighbor] 不直接 append？
# 因为 append 会修改原列表。
# 这里需要每条候选路径都是独立副本，所以用 + 创建新列表更安全。

# 3. 为什么要有 best_seen？
# 为了避免同一个点反复用更差状态扩展，减少重复计算。

# 4. 为什么 if current_zone == graph.end: return path 可以直接返回？
# 因为堆保证当前弹出来的是按 (cost, priority_score) 排序最优的状态。
# 所以第一次弹出终点时，这条路径就是当前规则下最佳的。

# b. 导入 Python 自带的堆模块。

# 这个模块提供的主要功能就是：

# heappush
# heappop

# 让你把一个普通 list 当成 最小堆 min-heap 来用。

# [v4]
# Problem: 当前代码的状态其实是不对称的
# a. restricted 落地时, occupancy +1, incoming +1
# b. normal 直接进入时, occupancy 不加incoming +1

# 这就导致：

# restricted 落地更容易“双算”
# normal 进入更依赖 incoming 来挡住同回合冲突

# 所以整体建模有点不统一。
# solution1: occupany or incoming, choose one
#
# 方法 1：实时状态法
# current_occupancy 实时更新
# 不需要 incoming
# 方法 2：预约表法
# current_occupancy 只表示回合开始快照
# 本回合新增进入全记到 incoming

# 两种都能成立，但不能混着用。

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
