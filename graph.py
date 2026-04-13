"""Graph data structures for the Fly_in project."""


class Zone:
    """A zone (node) in the drone network."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        max_drones: int = 1,
        color: str | None = None,
    ) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.max_drones: int = max_drones
        self.color = color

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
        # frozenset({"a", "b"}) == frozenset({"b", "a"})
        # frozenset: 不可修改的集合（immutable set）
        # e.g. connection: start-a [max_link_capacity=2]
        # self.links[frozenset({"start", "a"})] = 2

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
