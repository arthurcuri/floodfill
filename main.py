from __future__ import annotations

from collections import deque
from typing import Iterable, List, Sequence, Tuple

Grid = List[List[int]]
Coord = Tuple[int, int]


def read_ints(stream: Iterable[str]) -> List[int]:

	for raw in stream:
		line = raw.strip()
		if not line or line.startswith("#"):
			continue
		try:
			return [int(value) for value in line.split()]
		except ValueError as exc:
			raise ValueError(f"Linha inválida: '{line}'") from exc
	raise ValueError("Entrada insuficiente - esperava mais valores.")


def parse_problem(stream: Iterable[str]) -> Tuple[Grid, Coord]:
	dims = read_ints(stream)
	if len(dims) != 2:
		raise ValueError("Primeira linha deve conter dois inteiros: n m")
	n_rows, n_cols = dims
	if n_rows <= 0 or n_cols <= 0:
		raise ValueError("Dimensões do grid devem ser positivas.")

	grid: Grid = []
	for row_idx in range(n_rows):
		row = read_ints(stream)
		if len(row) != n_cols:
			raise ValueError(
				f"Linha {row_idx + 1} do grid deve conter {n_cols} inteiros, "
				f"mas recebeu {len(row)}."
			)
		grid.append(row)

	coord = read_ints(stream)
	if len(coord) != 2:
		raise ValueError("Coordenadas finais devem conter dois inteiros: x y")
	x, y = coord
	if not (0 <= x < n_rows and 0 <= y < n_cols):
		raise ValueError(
			f"Coordenadas ({x}, {y}) fora dos limites 0<=x<{n_rows}, 0<=y<{n_cols}."
		)

	return grid, (x, y)


def neighbors(x: int, y: int, n_rows: int, n_cols: int) -> Iterable[Coord]:
	if x > 0:
		yield x - 1, y
	if x + 1 < n_rows:
		yield x + 1, y
	if y > 0:
		yield x, y - 1
	if y + 1 < n_cols:
		yield x, y + 1


def paint_region(grid: Grid, start: Coord, color: int) -> int:

	x, y = start
	if grid[x][y] != 0:
		return 0

	queue: deque[Coord] = deque([(x, y)])
	grid[x][y] = color
	painted = 1
	n_rows, n_cols = len(grid), len(grid[0])

	while queue:
		cx, cy = queue.popleft()
		for nx, ny in neighbors(cx, cy, n_rows, n_cols):
			if grid[nx][ny] == 0:
				grid[nx][ny] = color
				painted += 1
				queue.append((nx, ny))
	return painted


def reserve_color(used_colors: set[int], candidate: int) -> Tuple[int, int]:

	color = max(candidate, 2)
	while color in used_colors:
		color += 1
	used_colors.add(color)
	return color, color + 1


def flood_fill_all(grid: Grid, start: Coord) -> Tuple[Grid, int]:
	used_colors = {value for row in grid for value in row if value >= 2}
	next_candidate = 2
	regions_colored = 0

	def fill_and_count(coord: Coord) -> None:
		nonlocal next_candidate, regions_colored
		if grid[coord[0]][coord[1]] != 0:
			return
		color, next_candidate = reserve_color(used_colors, next_candidate)
		if paint_region(grid, coord, color):
			regions_colored += 1

	fill_and_count(start)

	for row_idx, row in enumerate(grid):
		for col_idx, value in enumerate(row):
			if value == 0:
				fill_and_count((row_idx, col_idx))

	return grid, regions_colored


def format_grid(grid: Sequence[Sequence[int]]) -> str:
	return "\n".join(" ".join(str(value) for value in row) for row in grid)


def main() -> None:
	import sys

	try:
		grid, start = parse_problem(sys.stdin)
	except ValueError as exc:
		print(f"Erro na entrada: {exc}", file=sys.stderr)
		sys.exit(1)

	updated, regions = flood_fill_all(grid, start)
	print(format_grid(updated))
	print(f"#regioes={regions}", file=sys.stderr)


if __name__ == "__main__":
	main()
