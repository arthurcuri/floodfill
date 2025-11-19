from __future__ import annotations

import random
import tkinter as tk
from collections import deque
from tkinter import ttk
from typing import Iterable, Iterator, List, Sequence, Tuple

Grid = List[List[int]]
Coord = Tuple[int, int]

FREE_COLOR = "#f3f4f6"
OBSTACLE_COLOR = "#111827"
OUTLINE_COLOR = "#d1d5db"
START_OUTLINE = "#f97316"
PALETTE = [
    "#f97316",
    "#06d6a0",
    "#118ab2",
    "#ef476f",
    "#ffd166",
    "#4c1d95",
    "#0ead69",
]


def neighbors(x: int, y: int, n_rows: int, n_cols: int) -> Iterable[Coord]:
    if x > 0:
        yield x - 1, y
    if x + 1 < n_rows:
        yield x + 1, y
    if y > 0:
        yield x, y - 1
    if y + 1 < n_cols:
        yield x, y + 1


def reserve_color(used_colors: set[int], candidate: int) -> Tuple[int, int]:
    color = max(candidate, 2)
    while color in used_colors:
        color += 1
    used_colors.add(color)
    return color, color + 1


def flood_fill_steps(grid: Grid, start: Coord) -> Iterator[Tuple[str, int, int, int]]:
    used_colors = {value for row in grid for value in row if value >= 2}
    next_candidate = 2
    rows, cols = len(grid), len(grid[0])

    def fill_region(coord: Coord) -> Iterator[Tuple[str, int, int, int]]:
        nonlocal next_candidate
        x, y = coord
        if grid[x][y] != 0:
            return
        color, next_candidate = reserve_color(used_colors, next_candidate)
        queue: deque[Coord] = deque([coord])
        grid[x][y] = color
        painted = 1
        yield ("color", color, 0, 0)
        yield ("cell", x, y, color)
        while queue:
            cx, cy = queue.popleft()
            for nx, ny in neighbors(cx, cy, rows, cols):
                if grid[nx][ny] == 0:
                    grid[nx][ny] = color
                    painted += 1
                    queue.append((nx, ny))
                    yield ("cell", nx, ny, color)
        return painted

    regions = 0
    painted = yield from fill_region(start)
    if painted:
        regions += 1
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 0:
                painted = yield from fill_region((i, j))
                if painted:
                    regions += 1
    yield ("done", regions, 0, 0)


def generate_random_grid(rows: int, cols: int, obstacle_ratio: float) -> Grid:
    grid: Grid = []
    free_cells: List[Coord] = []
    for r in range(rows):
        row: List[int] = []
        for c in range(cols):
            value = 1 if random.random() < obstacle_ratio else 0
            row.append(value)
            if value == 0:
                free_cells.append((r, c))
        grid.append(row)
    if not free_cells:
        r = random.randrange(rows)
        c = random.randrange(cols)
        grid[r][c] = 0
    return grid


def color_for_value(value: int) -> str:
    if value == 0:
        return FREE_COLOR
    if value == 1:
        return OBSTACLE_COLOR
    palette_index = (value - 2) % len(PALETTE)
    return PALETTE[palette_index]


class FloodFillApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Flood Fill Visualizer")
        self.rows_var = tk.IntVar(value=10)
        self.cols_var = tk.IntVar(value=10)
        self.obstacle_var = tk.DoubleVar(value=30.0)
        self.speed_var = tk.IntVar(value=60)
        self.status_var = tk.StringVar(value="Pronto")
        self.start_var = tk.StringVar(value="Start: -")
        self.grid: Grid | None = None
        self.rects: List[List[int]] = []
        self.start: Coord | None = None
        self.animation = None
        self.animation_running = False
        self.step_iter: Iterator[Tuple[str, int, int, int]] | None = None
        self.cell_size = 32
        self.colors_used: List[int] = []
        self.color_placeholder: tk.Widget | None = None
        self.build_ui()
        self.generate_new_grid()

    def build_ui(self) -> None:
        controls = ttk.Frame(self.root, padding=10)
        controls.pack(fill="x")

        ttk.Label(controls, text="Linhas (máx. 10)").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(controls, from_=3, to=10, textvariable=self.rows_var, width=5).grid(row=1, column=0, padx=(0, 10))

        ttk.Label(controls, text="Colunas (máx. 10)").grid(row=0, column=1, sticky="w")
        ttk.Spinbox(controls, from_=3, to=10, textvariable=self.cols_var, width=5).grid(row=1, column=1, padx=(0, 10))

        self.obstacle_label = ttk.Label(controls, text="Obstáculos: 30%")
        self.obstacle_label.grid(row=0, column=2, sticky="w")
        ttk.Scale(controls, from_=5, to=80, orient="horizontal", variable=self.obstacle_var, command=self.update_obstacle_label).grid(row=1, column=2, padx=(0, 10), sticky="ew")

        ttk.Label(controls, text="Velocidade (ms)").grid(row=0, column=3, sticky="w")
        ttk.Scale(controls, from_=20, to=200, orient="horizontal", variable=self.speed_var).grid(row=1, column=3, padx=(0, 10), sticky="ew")

        ttk.Button(controls, text="Novo grid", command=self.generate_new_grid).grid(row=0, column=4, rowspan=2, padx=(0, 10))
        ttk.Button(controls, text="Iniciar preenchimento", command=self.start_animation).grid(row=0, column=5, rowspan=2)

        controls.columnconfigure(2, weight=1)
        controls.columnconfigure(3, weight=1)

        info_frame = ttk.Frame(self.root, padding=(10, 0, 10, 5))
        info_frame.pack(fill="x")
        ttk.Label(info_frame, textvariable=self.start_var).pack(side="left")
        ttk.Label(info_frame, textvariable=self.status_var).pack(side="right")

        self.canvas = tk.Canvas(self.root, width=600, height=400, bg="white", highlightthickness=0)
        self.canvas.pack(padx=10, pady=(0, 10))
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        legend_frame = ttk.LabelFrame(self.root, text="Cores utilizadas", padding=(10, 5))
        legend_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.color_container = ttk.Frame(legend_frame)
        self.color_container.pack(fill="x")
        self.reset_color_feedback()

    def update_obstacle_label(self, _event: str | None = None) -> None:
        value = int(self.obstacle_var.get())
        self.obstacle_label.config(text=f"Obstáculos: {value}%")

    def generate_new_grid(self) -> None:
        if self.animation_running:
            return
        rows = self.rows_var.get()
        cols = self.cols_var.get()
        ratio = self.obstacle_var.get() / 100
        self.grid = generate_random_grid(rows, cols, ratio)
        self.start = self.pick_random_start()
        self.status_var.set("Pronto")
        self.step_iter = None
        self.animation = None
        self.animation_running = False
        self.draw_grid()
        self.update_start_label()
        self.reset_color_feedback()

    def pick_random_start(self) -> Coord | None:
        assert self.grid is not None
        free_cells = [(r, c) for r, row in enumerate(self.grid) for c, value in enumerate(row) if value == 0]
        return random.choice(free_cells) if free_cells else None

    def draw_grid(self) -> None:
        assert self.grid is not None
        self.canvas.delete("all")
        self.rects = []
        rows, cols = len(self.grid), len(self.grid[0])
        width = cols * self.cell_size
        height = rows * self.cell_size
        self.canvas.config(width=width, height=height)
        for r, row in enumerate(self.grid):
            rect_row: List[int] = []
            for c, value in enumerate(row):
                x0 = c * self.cell_size
                y0 = r * self.cell_size
                rect = self.canvas.create_rectangle(
                    x0,
                    y0,
                    x0 + self.cell_size,
                    y0 + self.cell_size,
                    fill=color_for_value(value),
                    outline=START_OUTLINE if self.start == (r, c) else OUTLINE_COLOR,
                    width=2 if self.start == (r, c) else 1,
                )
                rect_row.append(rect)
            self.rects.append(rect_row)

    def on_canvas_click(self, event: tk.Event) -> None:
        if self.grid is None or self.animation_running:
            return
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if row < 0 or col < 0:
            return
        rows, cols = len(self.grid), len(self.grid[0])
        if row >= rows or col >= cols:
            return
        if self.grid[row][col] != 0:
            return
        self.start = (row, col)
        self.update_start_label()
        self.update_cell_outline()

    def update_cell_outline(self) -> None:
        if self.grid is None:
            return
        for r, row in enumerate(self.grid):
            for c, value in enumerate(row):
                outline = START_OUTLINE if self.start == (r, c) else OUTLINE_COLOR
                width = 2 if self.start == (r, c) else 1
                self.canvas.itemconfigure(self.rects[r][c], outline=outline, width=width)

    def update_start_label(self) -> None:
        if self.start is None:
            self.start_var.set("Start: -")
        else:
            r, c = self.start
            self.start_var.set(f"Start: ({r}, {c})")
        self.update_cell_outline()

    def start_animation(self) -> None:
        if self.grid is None or self.start is None or self.animation_running:
            return
        self.step_iter = flood_fill_steps([row[:] for row in self.grid], self.start)
        self.animation_running = True
        self.status_var.set("Executando flood fill...")
        self.advance_animation()

    def advance_animation(self) -> None:
        if self.step_iter is None:
            self.animation_running = False
            return
        try:
            event = next(self.step_iter)
        except StopIteration:
            self.animation_running = False
            self.status_var.set("Concluído")
            return
        kind, row, col, value = event
        delay = 0
        if kind == "cell":
            self.grid[row][col] = value
            self.canvas.itemconfigure(self.rects[row][col], fill=color_for_value(value))
            delay = self.speed_var.get()
        elif kind == "color":
            self.register_color(row)
        elif kind == "done":
            regions = row
            self.status_var.set(f"Regiões preenchidas: {regions}")
            self.animation_running = False
            return
        if self.animation_running:
            self.root.after(delay, self.advance_animation)

    def reset_color_feedback(self) -> None:
        for child in self.color_container.winfo_children():
            child.destroy()
        self.colors_used.clear()
        self.color_placeholder = ttk.Label(self.color_container, text="Nenhuma cor aplicada")
        self.color_placeholder.pack(anchor="w", pady=2)

    def register_color(self, color_value: int) -> None:
        if color_value in self.colors_used:
            return
        self.colors_used.append(color_value)
        if self.color_placeholder is not None:
            self.color_placeholder.destroy()
            self.color_placeholder = None
        entry = ttk.Frame(self.color_container)
        entry.pack(side="left", padx=4, pady=2)
        swatch = tk.Canvas(entry, width=26, height=26, highlightthickness=1, highlightbackground=OUTLINE_COLOR)
        swatch.pack()
        swatch.create_rectangle(0, 0, 26, 26, fill=color_for_value(color_value), outline="")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    FloodFillApp().run()


if __name__ == "__main__":
    main()
