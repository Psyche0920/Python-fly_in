import tkinter as tk
from typing import Any
from graph import Graph

State = tuple[str, ...]
# flexible tuple structure, all strs: zone or edge
# ("zone", zone_name)
# ("edge", a, b)
Point = tuple[float, float]  # canvas coordinates


class FlyUI:
    """Simple visualizer for Fly-in results."""

    BG = "#526055"
    TEXT = "#e2e8f0"
    EDGE_BG = "#1e293b"
    FALLBACK = "#64748b"
    START = "#22c55e"
    BALL_COLOR = (
        "#ff4d4d",
        "#ff9f1c",
        "#ffe66d",
        "#2ec4b6",
        "#3a86ff",
        "#8338ec",
    )

    def __init__(self, graph: Graph, results: list[str]) -> None:
        """Initialize the UI, create widgets, bind keys, and show turn 0."""
        self.graph = graph
        self.results = results
        self.turn = 0
        self.margin = 70
        self.zone_radius = 24
        self.zone_pos: dict[str, Point] = {}  # {"start": (120.0, 380.0)}
        # needs to transfer logic coordinates into tkinter coordinates
        # drone-id: drone position
        self.drone_ids = self._collect_drone_ids()  # find ids of all drones

        self.root = tk.Tk()  # create TK window
        self.root.title("Fly-in")
        self.root.geometry("1100x760")

        # initial window size,may change afterwards
        self.canvas = tk.Canvas(
            self.root,  # Canvas in the main window
            bg=self.BG,
            highlightthickness=0  # remove the highlighted frame of Canvas
        )
        self.canvas.pack(fill="both", expand=True)
        # put canvas in the window, allow it extend automatically
        # both vertically and horizontally
        # as window grows, canvas grows also

        self.info = tk.Label(
            self.root,
            bg="#111827",
            fg=self.TEXT,  # foreground
            font=("Arial", 11, "bold"),
            pady=8  # padding y
        )
        self.info.pack(fill="x")

        self.canvas.bind(
            "<Configure>",
            lambda _event: self._show_turn(self.turn)
        )
        # "<Configure>": an event, size changes, relayout
        # bind()-> event listener
        # pull window
        #   ↓
        # Canvas size change
        #   ↓
        # trigger <Configure>
        #   ↓
        # execute _show_turn()
        #   ↓
        # redraw, auto update ui
        self._bind_keys()

        self.root.update_idletasks()
        self.root.update()
        self._show_turn(0)
        self.root.mainloop()
        # while True:
        # wait for printing
        # updates
        # instead of execute once and exit quickly

    def _bind_keys(self) -> None:
        """Set keys shortcut. """
        keys = {
            "<Left>": self.prev_turn,
            "<Right>": self.next_turn,
            "<space>": self.next_turn,
            "<r>": self.restart,
            "<R>": self.restart,
            "<Escape>": self.quit_ui
        }

        for key, action in keys.items():
            self.root.bind(key, action)

    def _collect_drone_ids(self) -> list[int]:
        """Collect all drone ids that appear in the simulation results."""
        ids: set[int] = set()
        for line in self.results:
            for token in line.split():
                left = token.split("-")[0]
                if left.startswith("D") and left[1:].isdigit():
                    ids.add(int(left[1:]))
        return sorted(ids)

    def _safe_color(self, color: str | None) -> str:
        """Return a valid Tkinter color or a fallback color if invalid."""
        if not color or color.lower() == "rainbow":
            return self.FALLBACK
        try:
            self.root.winfo_rgb(color)
            # built-in function
            # check color validity and transfer into RGB value
            return color
        except tk.TclError:
            return self.FALLBACK

    def _layout(self) -> None:
        """
        Convert [zone] coordinates into canvas cooridnates.
        - compute the map (original coordinates boundaries)
        - decide scale based on the map
        - move the scaled maps into the screen middle
        """
        if not self.graph.zones:
            self.zone_pos = {}
            return

        # access the current canvas size
        # set min fallback value to void failed initialization
        width = max(self.canvas.winfo_width(), 700)
        height = max(self.canvas.winfo_height(), 500)

        # get the map span
        xs = [zone.x for zone in self.graph.zones.values()]
        ys = [zone.y for zone in self.graph.zones.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(1, max_x - min_x)
        span_y = max(1, max_y - min_y)

        # compute the scale
        scale = min(
            (width - 2 * self.margin) / span_x,
            (height - 2 * self.margin) / span_y
        )
        scale = max(35.0, min(scale, 180.0))
        # scaled map too big, ugly, max 180.0
        # too small, cannot see, at least 35

        if len(self.graph.zones) <= 10:
            self.zone_radius = 34
        elif len(self.graph.zones) <= 20:
            self.zone_radius = 28
        else:
            self.zone_radius = 22

        # put the scaled map in the middle
        offset_x = (width - span_x * scale) / 2 - min_x * scale
        offset_y = (height - span_y * scale) / 2 - min_y * scale
        # in case not start from (0,0)

        # 屏幕坐标 = 原始坐标 * 缩放 + 偏移
        self.zone_pos = {}
        for name, zone in self.graph.zones.items():
            self.zone_pos[name] = (
                zone.x * scale + offset_x,
                zone.y * scale + offset_y
            )

    def _parse_token(self, token: str) -> tuple[int, State | None]:
        """Parse one output token into a drone id and a state tuple"""
        parts = token.split("-")
        # "D1-A"     → (1, ("zone", "A"))
        # "D2-A-B"   → (2, ("edge", "A", "B"))

        if len(parts) < 2:
            return -1, None

        head = parts[0]
        if not head.startswith("D") or not head[1:].isdigit():
            return -1, None

        drone_id = int(head[1:])

        if len(parts) == 2:
            return drone_id, ("zone", parts[1])

        if len(parts) == 3:
            return drone_id, ("edge", parts[1], parts[2])
        return -1, None

    def _state_for_turn(self, turn: int) -> dict[int, State]:
        """
        Rebuild the updated drone state for the [given] turn.
        Return:
        {
            1: ("zone", "A"),
            2: ("edge", "A", "B"),
            3: ("zone", "C"),
        }
        """
        state: dict[int, State] = {}
        if self.graph.start is not None:
            for drone_id in self.drone_ids:
                state[drone_id] = ("zone", self.graph.start)
                # state = {
                # 1: ("zone", "A"),
                # 2: ("zone", "A"),
                # 3: ("zone", "A"),
                # }
        for line in self.results[:turn]:
            for token in line.split():
                drone_id, item = self._parse_token(token)
                if drone_id >= 0 and item is not None:
                    state[drone_id] = item
        return state

    def _positions(self, state: dict[int, State]) -> dict[int, Point]:
        """Convert logical [drone] states into canvas positions."""
        positions: dict[int, Point] = {}
        zone_count: dict[str, int] = {}
        edge_count: dict[tuple[str, str], int] = {}

        for drone_id, item in sorted(state.items()):
            if item[0] == "zone":
                zone_name = item[1]
                if zone_name not in self.zone_pos:
                    continue  # defensive
                x, y = self.zone_pos[zone_name]
                index = zone_count.get(zone_name, 0)
                zone_count[zone_name] = index + 1
                dx = (index % 4 - 1.5) * 10
                dy = (index // 4 - 0.5) * 10
                positions[drone_id] = (x + dx, y + dy)

            # item[0] == "edge"
            else:
                a, b = item[1], item[2]
                if a not in self.zone_pos or b not in self.zone_pos:
                    continue
                x1, y1 = self.zone_pos[a]
                x2, y2 = self.zone_pos[b]
                key = (a, b) if a <= b else (b, a)
                index = edge_count.get(key, 0)
                edge_count[key] = index + 1
                mx = (x1 + x2) / 2
                my = (y1 + y2) / 2
                shift = (index - 0.5) * 10
                positions[drone_id] = (mx + shift, my)
        return positions

    def _draw_graph(self) -> None:
        """Draw all links/edges and zones on the canvas"""
        self.canvas.delete("all")
        self._layout()
        for link in self.graph.links:  # only the key is listed through
            a, b = tuple(link)
            if a not in self.zone_pos or b not in self.zone_pos:
                continue

            # take two zones
            x1, y1 = self.zone_pos[a]
            x2, y2 = self.zone_pos[b]
            # draw the edge
            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=self.EDGE_BG,
                width=3
            )
            # draw the zones
        for name, zone in self.graph.zones.items():
            x, y = self.zone_pos[name]
            color = getattr(zone, "color", None)
            fill = self._safe_color(color)
            # draw the circle
            self.canvas.create_oval(
                x - self.zone_radius,
                y - self.zone_radius,
                x + self.zone_radius,
                y + self.zone_radius,
                fill=fill,
                outline="#f6fafa",
                width=2
            )
            # draw zone name
            self.canvas.create_text(
                x,
                y - self.zone_radius - 14,
                text=name,
                fill=self.TEXT,
                font=("Arial", 11, "bold")
            )

            # draw coordinates
            self.canvas.create_text(
                x,
                y + self.zone_radius + 14,
                text=f"({zone.x}, {zone.y})",
                fill=self.TEXT,
                font=("Arial", 9)
            )

    def _draw_drones(self, positions: dict[int, Point]) -> None:
        """Draw all drones at their current canvas positions."""
        radius = max(7, self.zone_radius // 3)
        colors = (
            "#ff4d4d",
            "#ff9f1c",
            "#ffe66d",
            "#2ec4b6",
            "#3a86ff",
            "#8338ec"
        )
        for drone_id, (x, y) in sorted(positions.items()):
            color = colors[(drone_id - 1) % len(colors)]
            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=color,
                outline="#0f172a",
                width=2
            )

    def _show_turn(self, turn: int) -> None:
        """Display one simulation turn on the screen"""
        self.turn = max(0, min(turn, len(self.results)))
        state: dict[int, State] = self._state_for_turn(self.turn)
        positions = self._positions(state)

        self._draw_graph()

        self._draw_drones(positions)

        arrived = 0
        if self.graph.end is not None:
            arrived = sum(
                1 for item in state.values()
                if item == ("zone", self.graph.end)
            )
        text = (
            f"Left/Right: move    R: restart    "
            f"Turn {self.turn}/{len(self.results)}    "
            f"Arrived {arrived}/{len(self.drone_ids)}"
        )
        # update label info
        self.info.config(text=text)

    def next_turn(self, _event: Any = None) -> None:
        self._show_turn(self.turn + 1)

    def prev_turn(self, _event: Any = None) -> None:
        self._show_turn(self.turn - 1)

    def restart(self, _event: Any = None) -> None:
        self._show_turn(0)

    def quit_ui(self, _event: Any = None) -> None:
        self.root.destroy()

# dx = (index % 4 - 1.5) * 10
# dy = (index // 4 - 0.5) * 10
# | index | %4 | //4 |
# | ----- | -- | --- |
# | 0     | 0  | 0   |
# | 1     | 1  | 0   |
# | 2     | 2  | 0   |
# | 3     | 3  | 0   |
# | 4     | 0  | 1   |
# | 5     | 1  | 1   |
# (0,0) (1,0) (2,0) (3,0)
# (0,1) (1,1) (2,1) (3,1)
# dx
# | index | index%4 | -1.5 后 |
# | ----- | ------- | ------ |
# | 0     | 0       | -1.5   |
# | 1     | 1       | -0.5   |
# | 2     | 2       | 0.5    |
# | 3     | 3       | 1.5    |
# L ←   -1.5  -0.5   0.5   1.5   → R
#        -15    -5    +5    +15
# dy
# ●   ●   ●   ●
# ●   ●   ●   ●

# mx = (x1 + x2) / 2
# xy = (y1 + y2) / 2
# positions[drone_id] = (mx + shift, my)
# Suppose A —— B：
# A ----------- B
#       ●
# multiple drones：
# A ----------- B
#    ●   ●   ●
