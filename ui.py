import tkinter as tk
from typing import Any

from graph import Graph

State = tuple[str, ...]
Point = tuple[float, float]


class FlyUI:
    """Simple and clear Tkinter UI for Fly-in."""

    BG = "#526055"
    TEXT = "#FDFFFD"
    EDGE_BG = "#1e293b"
    EDGE = "#475569"
    FALLBACK = "#1E1E1F"
    START = "#22c55e"
    END = "#f59e0b"
    BALL_COLORS = (
        "#ff4d4d",
        "#ff9f1c",
        "#ffe66d",
        "#2ec4b6",
        "#3a86ff",
        "#8338ec",
    )

    def __init__(self, graph: Graph, results: list[str]) -> None:
        self.graph = graph
        self.results = results
        self.turn = 0
        self.margin = 70
        self.zone_radius = 28
        self.animation_ms = 700
        self.zone_pos: dict[str, Point] = {}
        self.current_pos: dict[int, Point] = {}
        self.animation_id = 0
        self.drone_ids = self._collect_drone_ids()

        self.root = tk.Tk()
        self.root.title("Fly-in")
        self.root.configure(bg=self.BG)
        self.root.geometry("1200x820")

        self.canvas = tk.Canvas(
            self.root,
            bg=self.BG,
            # highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.info = tk.Label(
            self.root,
            bg="#111827",
            fg=self.TEXT,
            font=("Arial", 12, "bold"),
            pady=8,
        )
        self.info.pack(fill="x")

        self.canvas.bind(
            "<Configure>",
            lambda _event: self._show_turn(self.turn, animate=False),
        )
        self._bind_keys()

        self.root.update_idletasks()
        self.root.update()
        self._show_turn(0, animate=False)
        self.root.mainloop()

    def _bind_keys(self) -> None:
        keys = {
            "<Left>": self.prev_turn,
            "<Right>": self.next_turn,
            "<space>": self.next_turn,
            "<r>": self.restart,
            "<R>": self.restart,
            "<q>": self.quit_ui,
            "<Q>": self.quit_ui,
            "<Escape>": self.quit_ui,
        }
        for key, action in keys.items():
            self.root.bind(key, action)

    def _collect_drone_ids(self) -> list[int]:
        ids: set[int] = set()
        for line in self.results:
            for token in line.split():
                left = token.split("-")[0]
                if left.startswith("D") and left[1:].isdigit():
                    ids.add(int(left[1:]))
        return sorted(ids)

    def _canvas_size(self) -> tuple[int, int]:
        width = max(self.canvas.winfo_width(), 700)
        height = max(self.canvas.winfo_height(), 500)
        return width, height

    def _safe_color(self, color: str | None) -> str:
        if not color or color.lower() == "rainbow":
            return self.FALLBACK
        try:
            self.root.winfo_rgb(color)
            return color
        except tk.TclError:
            return self.FALLBACK

    def _compute_layout(self) -> None:
        if not self.graph.zones:
            self.zone_pos = {}
            return

        width, height = self._canvas_size()
        xs = [zone.x for zone in self.graph.zones.values()]
        ys = [zone.y for zone in self.graph.zones.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(1, max_x - min_x)
        span_y = max(1, max_y - min_y)
        count = len(self.graph.zones)

        scale = min(
            (width - 2 * self.margin) / span_x,
            (height - 2 * self.margin) / span_y,
        )
        caps = [(8, 280.0), (15, 230.0), (28, 180.0)]
        max_scale = 145.0
        for limit, cap in caps:
            if count <= limit:
                max_scale = cap
                break
        scale = max(28.0, min(scale, max_scale))

        extra = 12 if count <= 10 else 0
        radius = scale * 0.22 + extra
        self.zone_radius = int(max(22, min(50, radius)))

        offset_x = (width - span_x * scale) / 2 - min_x * scale
        offset_y = (height - span_y * scale) / 2 - min_y * scale
        self.zone_pos = {}
        for name, zone in self.graph.zones.items():
            self.zone_pos[name] = (
                zone.x * scale + offset_x,
                zone.y * scale + offset_y,
            )

    def _parse_token(self, token: str) -> tuple[int, State | None]:
        parts = token.split("-")
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
        return drone_id, None

    def _build_state(self, turn: int) -> dict[int, State]:
        state: dict[int, State] = {}
        if self.graph.start is not None:
            for drone_id in self.drone_ids:
                state[drone_id] = ("zone", self.graph.start)

        for line in self.results[:turn]:
            for token in line.split():
                drone_id, item = self._parse_token(token)
                if drone_id >= 0 and item is not None:
                    state[drone_id] = item
        return state

    def _build_positions(self, state: dict[int, State]) -> dict[int, Point]:
        pos: dict[int, Point] = {}
        edge_count: dict[tuple[str, str], int] = {}

        for drone_id, item in sorted(state.items()):
            if item[0] == "zone":
                zone_name = item[1]
                if zone_name in self.zone_pos:
                    pos[drone_id] = self.zone_pos[zone_name]
                continue

            a, b = item[1], item[2]
            if a not in self.zone_pos or b not in self.zone_pos:
                continue
            x1, y1 = self.zone_pos[a]
            x2, y2 = self.zone_pos[b]
            key = (a, b) if a <= b else (b, a)
            index = edge_count.get(key, 0)
            edge_count[key] = index + 1

            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            vec_x = x2 - x1
            vec_y = y2 - y1
            length = max((vec_x * vec_x + vec_y * vec_y) ** 0.5, 1.0)
            side_x = -vec_y / length
            side_y = vec_x / length
            shift = ((index + 1) // 2) * 10
            if index % 2 == 0:
                shift *= -1
            pos[drone_id] = (
                mid_x + side_x * shift,
                mid_y + side_y * shift,
            )
        return pos

    def _draw_text_box(
        self,
        x: float,
        y: float,
        text: str,
        size: int,
        fill: str,
    ) -> None:
        text_id = self.canvas.create_text(
            x,
            y,
            text=text,
            fill=fill,
            font=("Arial", size, "bold"),
        )
        box = self.canvas.bbox(text_id)
        if box is None:
            return
        x1, y1, x2, y2 = box
        bg_id = self.canvas.create_rectangle(
            x1 - 6,
            y1 - 3,
            x2 + 6,
            y2 + 3,
            fill="#0b1220",
            outline="#334155",
        )
        self.canvas.tag_lower(bg_id, text_id)

    def _draw_rainbow_zone(self, x: float, y: float) -> None:
        start = 0
        for color in self.BALL_COLORS:
            self.canvas.create_arc(
                x - self.zone_radius,
                y - self.zone_radius,
                x + self.zone_radius,
                y + self.zone_radius,
                start=start,
                extent=61,
                style=tk.PIESLICE,
                outline="",
                fill=color,
            )
            start += 60

    def _draw_graph(self) -> None:
        self.canvas.delete("all")
        self._compute_layout()

        for link in getattr(self.graph, "links", []):
            a, b = tuple(link)
            if a not in self.zone_pos or b not in self.zone_pos:
                continue
            x1, y1 = self.zone_pos[a]
            x2, y2 = self.zone_pos[b]
            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=self.EDGE_BG,
                width=8,
                capstyle=tk.ROUND,
            )
            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=self.EDGE,
                width=3,
                capstyle=tk.ROUND,
            )

        for name, zone in self.graph.zones.items():
            x, y = self.zone_pos[name]
            if name == self.graph.start:
                border_width = 5
                border_color = self.START
            elif name == self.graph.end:
                border_width = 5
                border_color = self.END
            else:
                border_width = 2
                border_color = "#cbd5e1"

            self.canvas.create_oval(
                x - self.zone_radius - 4,
                y - self.zone_radius - 4,
                x + self.zone_radius + 4,
                y + self.zone_radius + 4,
                outline="#020617",
                width=5,
            )

            zone_color = getattr(zone, "color", "")
            if isinstance(zone_color, str) and zone_color.lower() == "rainbow":
                self._draw_rainbow_zone(x, y)
            else:
                self.canvas.create_oval(
                    x - self.zone_radius,
                    y - self.zone_radius,
                    x + self.zone_radius,
                    y + self.zone_radius,
                    fill=self._safe_color(zone_color),
                    outline="",
                )

            self.canvas.create_oval(
                x - self.zone_radius,
                y - self.zone_radius,
                x + self.zone_radius,
                y + self.zone_radius,
                outline=border_color,
                width=border_width,
            )
            self._draw_text_box(
                x,
                y - self.zone_radius - 16,
                name,
                max(11, self.zone_radius // 3),
                "#f8fafc",
            )
            self._draw_text_box(
                x,
                y + self.zone_radius + 16,
                f"({zone.x}, {zone.y})",
                max(9, self.zone_radius // 4),
                "#cbd5e1",
            )

    def _ball_color(self, drone_id: int) -> str:
        index = (drone_id - 1) % len(self.BALL_COLORS)
        return self.BALL_COLORS[index]

    def _draw_drones(self, pos: dict[int, Point]) -> None:
        radius = max(9, min(13, self.zone_radius // 3))
        for drone_id, (x, y) in sorted(pos.items()):
            self.canvas.create_oval(
                x - radius - 2,
                y - radius - 2,
                x + radius + 2,
                y + radius + 2,
                outline="#ffffff",
                width=1,
            )
            self.canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=self._ball_color(drone_id),
                outline="#0b1020",
                width=2,
            )

    def _update_info(self, state: dict[int, State]) -> None:
        end_zone = getattr(self.graph, "end", None)
        arrived = sum(
            1
            for item in state.values()
            if item == ("zone", end_zone)
        )
        move_line = "No moves yet"
        if 0 < self.turn <= len(self.results):
            move_line = self.results[self.turn - 1]
        text = (
            f"Left/Right: move    R: restart    Esc: quit    "
            f"Turn {self.turn}/{len(self.results)}    "
            f"Arrived {arrived}/{len(self.drone_ids)}    {move_line}"
        )
        self.info.config(text=text)

    def _render(self, pos: dict[int, Point], state: dict[int, State]) -> None:
        self._draw_graph()
        self._draw_drones(pos)
        self._update_info(state)

    def _animate(
        self,
        target: dict[int, Point],
        state: dict[int, State],
    ) -> None:
        self.animation_id += 1
        this_id = self.animation_id
        start = self.current_pos or target
        drone_ids = sorted(set(start) | set(target))

        def ease(value: float) -> float:
            return value * value * (3 - 2 * value)

        def step(frame: int, total: int = 26) -> None:
            if this_id != self.animation_id:
                return
            value = ease(frame / total)
            pos: dict[int, Point] = {}
            for drone_id in drone_ids:
                from_x, from_y = start.get(drone_id, target[drone_id])
                to_x, to_y = target.get(drone_id, start[drone_id])
                pos[drone_id] = (
                    from_x + (to_x - from_x) * value,
                    from_y + (to_y - from_y) * value,
                )
            self.current_pos = pos
            self._render(pos, state)
            if frame < total:
                delay = max(1, self.animation_ms // total)
                self.root.after(delay, lambda: step(frame + 1, total))

        step(0)

    def _show_turn(self, turn: int, animate: bool = True) -> None:
        self.turn = max(0, min(turn, len(self.results)))
        state = self._build_state(self.turn)
        target = self._build_positions(state)
        if animate and self.current_pos:
            self._animate(target, state)
        else:
            self.current_pos = target
            self._render(target, state)

    def next_turn(self, _event: Any = None) -> None:
        self._show_turn(self.turn + 1)

    def prev_turn(self, _event: Any = None) -> None:
        self._show_turn(self.turn - 1)

    def restart(self, _event: Any = None) -> None:
        self._show_turn(0)

    def quit_ui(self, _event: Any = None) -> None:
        self.root.destroy()
