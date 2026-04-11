import tkinter as tk
from graph import Graph


class FlyUI:
    """Simple turn-based UI for Fly-in."""

    def __init__(self, graph: Graph, results: list[str]) -> None:
        self.graph = graph
        self.results = results
        self.turn = 0
        self.animating = False

        self.scale = 150
        self.offset = 100
        self.zone_radius = 22
        self.steps = 18
        self.delay_ms = 30

        self.zone_pos: dict[str, tuple[float, float]] = {}
        self.drone_ids = self.collect_drone_ids()
        self.current_pos: dict[int, tuple[float, float]] = {}

        self.root = tk.Tk()
        self.root.title("Fly-in Simulation")

        self.canvas = tk.Canvas(self.root, width=900, height=650, bg="white")
        self.canvas.pack()

        self.info_label = tk.Label(
            self.root,
            text="→ / Space: next   ←: prev   R: restart   Q / Esc: quit",
            font=("Arial", 12),
        )
        self.info_label.pack(pady=8)

        self.turn_label = tk.Label(
            self.root,
            text="Turn 0",
            font=("Arial", 14, "bold"),
        )
        self.turn_label.pack(pady=4)

        self.bind_keys()
        self.draw_graph()
        self.draw_turn(0)

        self.root.mainloop()

    def collect_drone_ids(self) -> list[int]:
        """Collect all drone IDs from simulation results."""
        ids: set[int] = set()

        for line in self.results:
            for token in line.split():
                drone_id = int(token.split("-")[0][1:])
                ids.add(drone_id)

        return sorted(ids)

    def to_canvas(self, x: int, y: int) -> tuple[float, float]:
        """Convert graph coordinates to canvas coordinates."""
        return x * self.scale + self.offset, y * self.scale + self.offset

    def bind_keys(self) -> None:
        """Bind keyboard controls."""
        self.root.bind("<Right>", self.next_turn)
        self.root.bind("<space>", self.next_turn)
        self.root.bind("<Left>", self.prev_turn)
        self.root.bind("<r>", self.restart)
        self.root.bind("<R>", self.restart)
        self.root.bind("<q>", self.quit_ui)
        self.root.bind("<Q>", self.quit_ui)
        self.root.bind("<Escape>", self.quit_ui)

    def next_turn(self, event=None) -> None:
        """Animate to next turn."""
        if not self.animating and self.turn < len(self.results):
            self.animate_to(self.turn + 1)

    def prev_turn(self, event=None) -> None:
        """Animate to previous turn."""
        if not self.animating and self.turn > 0:
            self.animate_to(self.turn - 1)

    def restart(self, event=None) -> None:
        """Restart from turn 0."""
        if not self.animating:
            self.animate_to(0)

    def quit_ui(self, event=None) -> None:
        """Close the UI."""
        self.root.destroy()

    def draw_graph(self) -> None:
        """Draw static graph: connections first, then zones."""
        for link in self.graph.links:
            a, b = list(link)
            x1, y1 = self.to_canvas(self.graph.zones[a].x, self.graph.zones[a].y)
            x2, y2 = self.to_canvas(self.graph.zones[b].x, self.graph.zones[b].y)
            self.canvas.create_line(x1, y1, x2, y2, width=2, fill="black")

        for name, zone in self.graph.zones.items():
            x, y = self.to_canvas(zone.x, zone.y)
            self.zone_pos[name] = (x, y)

            color = zone.color if zone.color else "lightgray"

            self.canvas.create_oval(
                x - self.zone_radius,
                y - self.zone_radius,
                x + self.zone_radius,
                y + self.zone_radius,
                fill=color,
                outline="black",
                width=2,
            )

            self.canvas.create_text(
                x,
                y,
                text=name,
                font=("Arial", 10, "bold"),
            )

    def parse_token(self, token: str):
        """
        Parse one simulation token.

        D1-a -> ("zone", "a")
        D2-start-r1 -> ("edge", "start", "r1")
        """
        parts = token.split("-")
        drone_id = int(parts[0][1:])

        if len(parts) == 2:
            return drone_id, ("zone", parts[1])

        if len(parts) == 3:
            return drone_id, ("edge", parts[1], parts[2])

        return drone_id, None

    def build_state(self, turn: int) -> dict[int, tuple]:
        """Build logical drone state after replaying turns [0, turn)."""
        state: dict[int, tuple] = {}

        if self.graph.start is not None:
            for drone_id in self.drone_ids:
                state[drone_id] = ("zone", self.graph.start)

        for line in self.results[:turn]:
            for token in line.split():
                drone_id, info = self.parse_token(token)
                if info is not None:
                    state[drone_id] = info

        return state

    def build_positions(self, state: dict[int, tuple]) -> dict[int, tuple[float, float]]:
        """Convert logical state to drawable positions."""
        positions: dict[int, tuple[float, float]] = {}
        zone_count: dict[str, int] = {}
        edge_count: dict[tuple[str, str], int] = {}

        for drone_id, info in sorted(state.items()):
            if info[0] == "zone":
                zone_name = info[1]
                x, y = self.zone_pos[zone_name]

                i = zone_count.get(zone_name, 0)
                zone_count[zone_name] = i + 1

                dx = (i % 3) * 12 - 12
                dy = (i // 3) * 12 + 30
                positions[drone_id] = (x + dx, y + dy)

            elif info[0] == "edge":
                a, b = info[1], info[2]
                x1, y1 = self.zone_pos[a]
                x2, y2 = self.zone_pos[b]

                i = edge_count.get((a, b), 0)
                edge_count[(a, b)] = i + 1

                x = (x1 + x2) / 2 + i * 10
                y = (y1 + y2) / 2 + 15
                positions[drone_id] = (x, y)

        return positions

    def draw_drones(self, positions: dict[int, tuple[float, float]]) -> None:
        """Draw drones."""
        self.canvas.delete("drone")

        for drone_id, (x, y) in sorted(positions.items()):
            self.canvas.create_oval(
                x - 7,
                y - 7,
                x + 7,
                y + 7,
                fill="black",
                outline="white",
                width=1,
                tags="drone",
            )
            self.canvas.create_text(
                x,
                y - 12,
                text=f"D{drone_id}",
                font=("Arial", 9),
                tags="drone",
            )

    def draw_turn(self, turn: int) -> None:
        """Draw one turn directly."""
        state = self.build_state(turn)
        positions = self.build_positions(state)
        self.current_pos = positions
        self.turn = turn
        self.turn_label.config(text=f"Turn {self.turn}")
        self.draw_drones(positions)

    def animate_to(self, target_turn: int) -> None:
        """Animate from current turn to target turn."""
        start_state = self.build_state(self.turn)
        end_state = self.build_state(target_turn)

        start_pos = self.build_positions(start_state)
        end_pos = self.build_positions(end_state)

        all_ids = set(start_pos) | set(end_pos)
        for drone_id in all_ids:
            if drone_id not in start_pos:
                start_pos[drone_id] = end_pos[drone_id]
            if drone_id not in end_pos:
                end_pos[drone_id] = start_pos[drone_id]

        self.animating = True
        self.animate_frame(start_pos, end_pos, 0, target_turn)

    def animate_frame(
        self,
        start_pos: dict[int, tuple[float, float]],
        end_pos: dict[int, tuple[float, float]],
        step: int,
        target_turn: int,
    ) -> None:
        """Draw one animation frame."""
        t = step / self.steps
        current: dict[int, tuple[float, float]] = {}

        for drone_id in start_pos:
            x1, y1 = start_pos[drone_id]
            x2, y2 = end_pos[drone_id]
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            current[drone_id] = (x, y)

        self.draw_drones(current)
        self.turn_label.config(text=f"Turn {target_turn}")

        if step < self.steps:
            self.root.after(
                self.delay_ms,
                lambda: self.animate_frame(start_pos, end_pos, step + 1, target_turn),
            )
        else:
            self.animating = False
            self.draw_turn(target_turn)
