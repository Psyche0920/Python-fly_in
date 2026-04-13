import tkinter as tk
from tkinter import ttk
from typing import Any

from graph import Graph

State = tuple[str, ...]
Pos = tuple[float, float]


class FlyUI:
    """Compact, cleaner Tkinter UI for Fly-in."""

    BG = "#0f172a"
    PANEL = "#111827"
    CARD = "#1f2937"
    LINE = "#334155"
    TEXT = "#e5e7eb"
    MUTED = "#94a3b8"
    DRONE = "#f8fafc"
    DRONE_OUTLINE = "#0f172a"
    START = "#22c55e"
    END = "#f59e0b"
    FALLBACK_ZONE = "#475569"

    def __init__(self, graph: Graph, results: list[str]) -> None:
        self.graph = graph
        self.results = results
        self.turn = 0
        self.margin = 90
        self.zone_radius = 24
        self.zone_pos: dict[str, Pos] = {}
        self.drone_ids = self._collect_drone_ids()

        self.root = tk.Tk()
        self.root.title("Fly-in")
        self.root.configure(bg=self.BG)
        self.root.geometry("1360x860")
        self.root.minsize(980, 680)

        self._build_ui()
        self._bind_keys()
        self._redraw()
        self.root.mainloop()

    def _build_ui(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Root.TFrame", background=self.BG)
        style.configure("Panel.TFrame", background=self.PANEL)
        style.configure("Card.TFrame", background=self.CARD)
        style.configure("Title.TLabel", background=self.PANEL,
                        foreground=self.TEXT, font=("Arial", 18, "bold"))
        style.configure("Body.TLabel", background=self.PANEL,
                        foreground=self.MUTED, font=("Arial", 11))
        style.configure("Card.TLabel", background=self.CARD,
                        foreground=self.TEXT, font=("Arial", 11))
        style.configure("Big.TLabel", background=self.CARD,
                        foreground=self.TEXT, font=("Arial", 22, "bold"))
        style.configure("TButton", font=("Arial", 11, "bold"))

        root = ttk.Frame(self.root, style="Root.TFrame", padding=14)
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=0)
        root.rowconfigure(0, weight=1)

        left = ttk.Frame(root, style="Panel.TFrame", padding=10)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        ttk.Label(left, text="Fly-in visualizer",
                  style="Title.TLabel").grid(row=0, column=0, sticky="w")

        self.canvas = tk.Canvas(left, bg=self.BG, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        self.canvas.bind("<Configure>", lambda _e: self._redraw())

        right = ttk.Frame(root, style="Panel.TFrame", padding=12)
        right.grid(row=0, column=1, sticky="ns")
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="Controls",
                  style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            right,
            text="← prev   → next   Space next\nR restart   Esc quit",
            style="Body.TLabel",
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(2, 12))

        card1 = ttk.Frame(right, style="Card.TFrame", padding=12)
        card1.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(card1, text="Turn", style="Card.TLabel").pack(anchor="w")
        self.turn_value = ttk.Label(card1, text="0 / 0", style="Big.TLabel")
        self.turn_value.pack(anchor="w", pady=(4, 6))
        self.progress = ttk.Label(card1, text="No moves yet",
                                  style="Card.TLabel", wraplength=260,
                                  justify="left")
        self.progress.pack(anchor="w")

        card2 = ttk.Frame(right, style="Card.TFrame", padding=12)
        card2.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(card2, text="Summary", style="Card.TLabel").pack(anchor="w")
        self.stats = ttk.Label(card2, text="",
                               style="Card.TLabel", justify="left")
        self.stats.pack(anchor="w", pady=(6, 0))

        btns = ttk.Frame(right, style="Panel.TFrame")
        btns.grid(row=4, column=0, sticky="ew", pady=(4, 10))
        for i in range(3):
            btns.columnconfigure(i, weight=1)
        ttk.Button(
            btns, text="Prev",
            command=self.prev_turn).grid(row=0, column=0, sticky="ew",
                                         padx=(0, 4))
        ttk.Button(btns, text="Next",
                   command=self.next_turn).grid(row=0, column=1,
                                                sticky="ew", padx=4)
        ttk.Button(btns, text="Restart",
                   command=self.restart).grid(row=0, column=2,
                                              sticky="ew", padx=(4, 0))

        card3 = ttk.Frame(right, style="Card.TFrame", padding=12)
        card3.grid(row=5, column=0, sticky="nsew")
        ttk.Label(card3, text="Legend", style="Card.TLabel").pack(anchor="w")
        legend = (
            "• Large green ring: start\n"
            "• Large amber ring: end\n"
            "• Small white dots: drones\n"
            "• Dot on edge: moving through restricted turn\n"
            "• Zone color uses map metadata when valid"
        )
        ttk.Label(card3, text=legend, style="Card.TLabel",
                  justify="left", wraplength=260).pack(anchor="w", pady=(6, 0))

    def _bind_keys(self) -> None:
        self.root.bind("<Left>", self.prev_turn)
        self.root.bind("<Right>", self.next_turn)
        self.root.bind("<space>", self.next_turn)
        self.root.bind("<r>", self.restart)
        self.root.bind("<R>", self.restart)
        self.root.bind("<Escape>", self.quit_ui)
        self.root.bind("<q>", self.quit_ui)
        self.root.bind("<Q>", self.quit_ui)

    def _collect_drone_ids(self) -> list[int]:
        ids: set[int] = set()
        for line in self.results:
            for token in line.split():
                if token.startswith("D"):
                    try:
                        ids.add(int(token.split("-")[0][1:]))
                    except ValueError:
                        pass
        return sorted(ids)

    def _safe_color(self, color: str | None, fallback: str) -> str:
        if not color:
            return fallback
        try:
            self.root.winfo_rgb(color)
            return color
        except tk.TclError:
            return fallback

    def _canvas_size(self) -> tuple[int, int]:
        width = max(self.canvas.winfo_width(), 600)
        height = max(self.canvas.winfo_height(), 500)
        return width, height

    def _layout(self) -> None:
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
        scale = min((width - 2 * self.margin) / span_x,
                    (height - 2 * self.margin) / span_y)
        scale = max(28.0, min(scale, 160.0))

        graph_w = span_x * scale
        graph_h = span_y * scale
        offset_x = (width - graph_w) / 2 - min_x * scale
        offset_y = (height - graph_h) / 2 - min_y * scale

        self.zone_pos = {
            name: (zone.x * scale + offset_x, zone.y * scale + offset_y)
            for name, zone in self.graph.zones.items()
        }

    def _parse_token(self, token: str) -> tuple[int, State | None]:
        parts = token.split("-")
        if not parts or not parts[0].startswith("D"):
            return -1, None
        try:
            drone_id = int(parts[0][1:])
        except ValueError:
            return -1, None
        if len(parts) == 2:
            return drone_id, ("zone", parts[1])
        if len(parts) == 3:
            return drone_id, ("edge", parts[1], parts[2])
        return drone_id, None

    def _state_at(self, turn: int) -> dict[int, State]:
        state: dict[int, State] = {}
        if self.graph.start is not None:
            for drone_id in self.drone_ids:
                state[drone_id] = ("zone", self.graph.start)
        for line in self.results[:turn]:
            for token in line.split():
                drone_id, value = self._parse_token(token)
                if drone_id >= 0 and value is not None:
                    state[drone_id] = value
        return state

    def _positions(self, state: dict[int, State]) -> dict[int, Pos]:
        positions: dict[int, Pos] = {}
        zone_slots: dict[str, int] = {}
        edge_slots: dict[tuple[str, str], int] = {}

        for drone_id, info in sorted(state.items()):
            if info[0] == "zone":
                name = info[1]
                if name not in self.zone_pos:
                    continue
                x, y = self.zone_pos[name]
                idx = zone_slots.get(name, 0)
                zone_slots[name] = idx + 1
                cols = 4
                gap = 13
                row, col = divmod(idx, cols)
                dx = (col - (cols - 1) / 2) * gap
                dy = 32 + row * gap
                positions[drone_id] = (x + dx, y + dy)
            else:
                a, b = info[1], info[2]
                if a not in self.zone_pos or b not in self.zone_pos:
                    continue
                x1, y1 = self.zone_pos[a]
                x2, y2 = self.zone_pos[b]
                first, second = sorted((a, b))
                key: tuple[str, str] = (first, second)
                idx = edge_slots.get(key, 0)
                edge_slots[key] = idx + 1
                mx = (x1 + x2) / 2
                my = (y1 + y2) / 2
                vx, vy = x2 - x1, y2 - y1
                length = max((vx * vx + vy * vy) ** 0.5, 1.0)
                px, py = -vy / length, vx / length
                offset = (idx - 0.5) * 12
                positions[drone_id] = (mx + px * offset, my + py * offset)
        return positions

    def _draw_graph(self) -> None:
        self.canvas.delete("all")
        self._layout()

        for raw_link in getattr(self.graph, "links", []):
            a, b = tuple(raw_link)
            if a not in self.zone_pos or b not in self.zone_pos:
                continue
            x1, y1 = self.zone_pos[a]
            x2, y2 = self.zone_pos[b]
            self.canvas.create_line(x1, y1, x2, y2, fill=self.LINE, width=3)

        for name, zone in self.graph.zones.items():
            x, y = self.zone_pos[name]
            fill = self._safe_color(getattr(zone, "color", None),
                                    self.FALLBACK_ZONE)
            outline = "#e2e8f0"
            width = 2
            if name == getattr(self.graph, "start", None):
                outline = self.START
                width = 4
            elif name == getattr(self.graph, "end", None):
                outline = self.END
                width = 4

            self.canvas.create_oval(
                x - self.zone_radius,
                y - self.zone_radius,
                x + self.zone_radius,
                y + self.zone_radius,
                fill=fill,
                outline=outline,
                width=width,
            )
            self.canvas.create_text(x, y - 2, text=name,
                                    fill=self.TEXT, font=("Arial", 10, "bold"))
            self.canvas.create_text(x, y + 14, text=f"({zone.x}, {zone.y})",
                                    fill=self.MUTED, font=("Arial", 8))

    def _draw_drones(self, positions: dict[int, Pos]) -> None:
        for drone_id, (x, y) in sorted(positions.items()):
            self.canvas.create_oval(
                x - 8,
                y - 8,
                x + 8,
                y + 8,
                fill=self.DRONE,
                outline=self.DRONE_OUTLINE,
                width=1,
            )
            self.canvas.create_text(x, y - 14, text=f"D{drone_id}",
                                    fill=self.TEXT, font=("Arial", 8, "bold"))

    def _update_side_panel(self, state: dict[int, State]) -> None:
        total = len(self.results)
        arrived = sum(
            1 for item in state.values()
            if item == ("zone", getattr(self.graph, "end", None)))
        moving = sum(
            1 for item in state.values()
            if item and item[0] == "edge")
        waiting = max(len(self.drone_ids) - arrived - moving, 0)
        self.turn_value.config(text=f"{self.turn} / {total}")

        line = self.results[self.turn - 1] if 0 < self.turn <= total else ""
        self.progress.config(text=line if line else "No moves this turn")
        self.stats.config(
            text=(
                f"Drones: {len(self.drone_ids)}\n"
                f"Arrived: {arrived}\n"
                f"Moving: {moving}\n"
                f"Waiting: {waiting}"
            )
        )

    def _redraw(self) -> None:
        self._draw_graph()
        state = self._state_at(self.turn)
        self._draw_drones(self._positions(state))
        self._update_side_panel(state)

    def _draw_turn(self, turn: int) -> None:
        self.turn = max(0, min(turn, len(self.results)))
        self._redraw()

    def next_turn(self, _event: Any = None) -> None:
        self._draw_turn(self.turn + 1)

    def prev_turn(self, _event: Any = None) -> None:
        self._draw_turn(self.turn - 1)

    def restart(self, _event: Any = None) -> None:
        self._draw_turn(0)

    def quit_ui(self, _event: Any = None) -> None:
        self.root.destroy()
