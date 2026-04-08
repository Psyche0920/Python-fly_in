class Zone:
    def __init__(self, name, x, y, zone_type="normal", max_drones=1) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.max_drones: int = max_drones

    def cost(self) -> float:  # not int or float?
        if self.zone_type == "restricted":
            return 2
        if self.zone_type == "blocked":
            return float("inf")  # ???
        return 1


class Connection:
    def __init__(self, z1, z2, capacity=1) -> None:
        self.z1: str = z1
        self.z2: str = z2
        self.capacity: int = capacity


class Graph:
    def __init__(self) -> None:
        self.zones: dict[str, Zone] = {}
        self.adj: dict[str, list[str]] = {}
        self.start: str | None = None
        self.end: str | None = None
        self.links: dict[frozenset[str], int] = {}
        # ✅ 新增：保存每条 connection 的容量
        # key 用 frozenset({"a", "b"})，因为 a-b 和 b-a 是同一条无向边

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone
        self.adj[zone.name] = []

    def add_connection(self, name1: str, name2: str,
                       capacity: int = 1) -> None:
        if name1 not in self.adj:
            raise ValueError(f"Unknown zone in connection: {name1}")
        if name2 not in self.adj:
            raise ValueError(f"Unknown zone in connection: {name2}")

        key = frozenset({name1, name2})
        if key in self.links:
            raise ValueError(f"Duplicate connection: {name1}-{name2}")

        self.adj[name1].append(name2)
        self.adj[name2].append(name1)
        self.links[key] = capacity

    def get_link_capacity(self, name1: str, name2: str) -> int:
        return self.links[frozenset({name1, name2})]


# [v1]
# 1️⃣ Zone = 一个点
# 包含：
# 名字
# 坐标
# 类型
# 容量

# 2️⃣ cost() = 进入代价
# normal → 1
# restricted → 2
# blocked → ∞

# 3️⃣ Graph.zones
# 👉 "名字" → Zone对象

# 4️⃣ Graph.adj
# 👉 "名字" → [邻居列表]

# [testmain]
# from graph import Graph, Zone

# g = Graph()

# g.add_zone(Zone("start", 0, 0))
# g.add_zone(Zone("a", 1, 0))
# g.add_zone(Zone("end", 2, 0))

# g.add_connection("start", "a")
# g.add_connection("a", "end")

# g.adj


# [v2]
# graph.zones["a"].max_drones 管的是 点（zone）

# graph.links[...] 管的是 边（connection）
