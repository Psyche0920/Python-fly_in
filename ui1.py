# 读取图（zones 和 connections）
# 读取每一回合的结果 results
# 把 zone 和 connection 画出来
# 把 drones 画出来
# 支持 turn 切换和动画

import tkinter as tk
from typing import Any
from graph import Graph

State = tuple[str, ...]
# unfixed data structure, all strs: zone or edge
# ("zone", zone_name)
# ("edge", a, b)
Point = tuple[float, float]  # coordinates


class FlyUI:
    """Simple and clear Tkinter UI for Fly-in"""

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
    self.graph = graph
    self.results = results
    self.turn = 0
    self.margin = 70
    self.zone_radius = 28
    self.animation_ms = 700
    self.zone_pos: dict[str, Point] = {}  # {"start": (120.0, 380.0)}
    # needs to transfer logic coordinates into tkinter coordinates
    self.current_pos: dict[int, Point]  # {1: (200.0, 300.0)}
    # drone-id: drone position
    self.animation_id = 0
    # avoid new-old animation conflict
    self.drone_ids = self._collect_drone_ids()  # find ids of all drones
    self.root = tk.TK()  # create TK window
    self.root.title("Fly-in")
    self.root.configure(bg=self.BG)
    self.root.geometry("1200x820")  # initial window size,may change afterwards
    self.canvas = tk.Canvas(
        self.root,  # Canvas in the main window
        bg=self.BG,
        highlightthickness=0  # remove the highlighted frame of Canvas
    )
    self.canvas.pack(fill="both", expand=True)
    # put canvas in the window, allow it extend automatically
    # both vertically and horizontally
    # as window grows, canvas grows also
    self. info = tk.Label(
        self.root,
        bg="#111827",
        fg=self.TEXT,  # foreground
        font=("Arial", 12, "bold"),
        pady=8  # padding y
    )
    self.info.pack(fill="x")
    self.canvas.bind(
        "<Configure>",
        lambda _event: self._show_turn(self.turn, animate=False)
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
    self._show_turn(0, animate=False)
    self.root.mainloop()
    # while True:
    # wait for printing
    # updates
    # instead of execute once and exit quickly


def _bind_keys(self) -> None:
    keys = {
        "<Left>": self.prev_turn,
        "<Right>": self.next_turn,
        "<Space>": self.next_turn,
        "<r>": self.restart,
        "<R": self.restart,
        "q": self.quit_ui,
        "Q": self.quit_ui,
        "<Escape>": self.quit_ui
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


# 输入 results
#       ↓
# 预处理（collect drone ids）
#       ↓
# 构建 state
#       ↓
# 计算位置
#       ↓
# 绘制 UI







