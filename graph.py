"""Graph data structures for the Fly_in project."""


class Zone:
    """A zone (node) in the drone network."""

    def __init__(self, name, x, y, zone_type="normal", max_drones=1) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.max_drones: int = max_drones

    def cost(self) -> float:
        """Return the movement cost to enter this zone."""
        if self.zone_type == "restricted":
            return 2.0
        if self.zone_type == "blocked":
            return float("inf")  # unlimited big
        return 1.0


class Connection:
    """An undirected connection between two zones."""

    def __init__(self, z1: str, z2: str, capacity: int = 1) -> None:
        self.z1: str = z1
        self.z2: str = z2
        self.capacity: int = capacity


class Graph:
    """Graph storing zones, adjacency lists, and connection capacities."""

    def __init__(self) -> None:
        self.zones: dict[str, Zone] = {}
        self.adj: dict[str, list[str]] = {}
        self.start: str | None = None
        self.end: str | None = None
        self.links: dict[frozenset[str], int] = {}
        # key=frozenset({"a", "b"}) => a-b = b-a

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph."""
        self.zones[zone.name] = zone
        self.adj[zone.name] = []

    def add_connection(self, name1: str, name2: str,
                       capacity: int = 1) -> None:
        """Add an undirected??? connection between two existing zones."""
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
        """Return the maximum number of drones allowed on a connection."""
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

# float("inf") 用在 Zone.cost() 里，是“无穷大”的意思。
# 它表示 blocked zone 的进入代价大到不可选，所以返回类型写 float 更合适。2 和 1 也会自动兼容成 float。
# 为什么要“无限大”？
# 因为这是一个通用设计（为最短路径算法准备）：
# normal → cost = 1
# restricted → cost = 2
# blocked → cost = ∞（永远不选）
# 👉 这样如果以后你用：
# Dijkstra
# A*
# 就可以自然跳过 blocked。
