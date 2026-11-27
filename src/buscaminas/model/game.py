from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable


Position = tuple[int, int]
GameObserver = Callable[["GameSnapshot"], None]


class CellState(Enum):
    COVERED = "covered"
    REVEALED = "revealed"
    FLAGGED = "flagged"


class GameStatus(Enum):
    READY = "ready"
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


@dataclass(frozen=True, slots=True)
class CellSnapshot:
    state: CellState
    adjacent_mines: int | None
    is_mine: bool | None


@dataclass(frozen=True, slots=True)
class GameSnapshot:
    rows: int
    columns: int
    status: GameStatus
    cells: tuple[tuple[CellSnapshot, ...], ...]


@dataclass(frozen=True, slots=True)
class MoveResult:
    changed: bool
    status: GameStatus
    newly_revealed: tuple[Position, ...] = ()
    first_reveal: bool = False


@dataclass(slots=True)
class _Cell:
    is_mine: bool = False
    adjacent_mines: int = 0
    state: CellState = CellState.COVERED


class MinesweeperGame:
    """UI-independent game rules for a single Minesweeper board."""

    def __init__(
        self,
        rows: int,
        columns: int,
        mine_positions: Iterable[Position],
    ) -> None:
        if isinstance(rows, bool) or isinstance(columns, bool):
            raise ValueError("Board dimensions must be positive integers.")
        if not isinstance(rows, int) or not isinstance(columns, int):
            raise ValueError("Board dimensions must be positive integers.")
        if rows <= 0 or columns <= 0:
            raise ValueError("Board dimensions must be positive integers.")

        positions = tuple(mine_positions)
        for position in positions:
            if (
                not isinstance(position, tuple)
                or len(position) != 2
                or any(isinstance(value, bool) or not isinstance(value, int) for value in position)
            ):
                raise ValueError("Each mine position must be a (row, column) integer pair.")
            if not self._in_bounds(position[0], position[1], rows, columns):
                raise ValueError(f"Mine position {position} is outside the board.")
        if len(set(positions)) != len(positions):
            raise ValueError("Mine positions must be unique.")
        if len(positions) >= rows * columns:
            raise ValueError("The board must contain at least one safe cell.")

        self._rows = rows
        self._columns = columns
        self._mine_count = len(positions)
        self._cells = [[_Cell() for _ in range(columns)] for _ in range(rows)]
        self._status = GameStatus.READY
        self._safe_revealed = 0
        self._observers: list[GameObserver] = []

        for row, column in positions:
            self._cells[row][column].is_mine = True
        self._calculate_adjacent_mines()

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def columns(self) -> int:
        return self._columns

    @property
    def status(self) -> GameStatus:
        return self._status

    @property
    def has_started(self) -> bool:
        return self._status is not GameStatus.READY

    def snapshot(self) -> GameSnapshot:
        cells = tuple(
            tuple(
                CellSnapshot(
                    state=cell.state,
                    adjacent_mines=(
                        cell.adjacent_mines
                        if cell.state is CellState.REVEALED
                        else None
                    ),
                    is_mine=(
                        cell.is_mine
                        if cell.state is CellState.REVEALED or self._status is GameStatus.LOST
                        else None
                    ),
                )
                for cell in row
            )
            for row in self._cells
        )
        return GameSnapshot(self._rows, self._columns, self._status, cells)

    def subscribe(self, observer: GameObserver) -> Callable[[], None]:
        """Register a callback and return a function that removes it."""
        if not callable(observer):
            raise TypeError("Observer must be callable.")
        self._observers.append(observer)

        def unsubscribe() -> None:
            if observer in self._observers:
                self._observers.remove(observer)

        return unsubscribe

    def reveal(self, row: int, column: int) -> MoveResult:
        self._validate_position(row, column)
        if self._status in (GameStatus.WON, GameStatus.LOST):
            return MoveResult(False, self._status)

        selected = self._cells[row][column]
        if selected.state is not CellState.COVERED:
            return MoveResult(False, self._status)

        first_reveal = self._status is GameStatus.READY
        self._status = GameStatus.IN_PROGRESS
        if selected.is_mine:
            newly_revealed = self._reveal_all_mines()
            self._status = GameStatus.LOST
            self._notify_observers()
            return MoveResult(
                True,
                self._status,
                newly_revealed,
                first_reveal,
            )

        newly_revealed = self._expand_reveal(row, column)
        if self._safe_revealed == self._rows * self._columns - self._mine_count:
            self._status = GameStatus.WON
        self._notify_observers()
        return MoveResult(True, self._status, newly_revealed, first_reveal)

    def toggle_flag(self, row: int, column: int) -> MoveResult:
        self._validate_position(row, column)
        if self._status in (GameStatus.WON, GameStatus.LOST):
            return MoveResult(False, self._status)

        cell = self._cells[row][column]
        if cell.state is CellState.COVERED:
            cell.state = CellState.FLAGGED
        elif cell.state is CellState.FLAGGED:
            cell.state = CellState.COVERED
        else:
            return MoveResult(False, self._status)

        self._notify_observers()
        return MoveResult(True, self._status)

    def _expand_reveal(self, row: int, column: int) -> tuple[Position, ...]:
        queue = deque([(row, column)])
        revealed: list[Position] = []
        queued = {(row, column)}

        while queue:
            current_row, current_column = queue.popleft()
            cell = self._cells[current_row][current_column]
            if cell.state is not CellState.COVERED or cell.is_mine:
                continue

            cell.state = CellState.REVEALED
            self._safe_revealed += 1
            revealed.append((current_row, current_column))

            if cell.adjacent_mines != 0:
                continue
            for neighbor in self._neighbors(current_row, current_column):
                neighbor_cell = self._cells[neighbor[0]][neighbor[1]]
                if (
                    neighbor not in queued
                    and neighbor_cell.state is CellState.COVERED
                    and not neighbor_cell.is_mine
                ):
                    queued.add(neighbor)
                    queue.append(neighbor)

        return tuple(revealed)

    def _reveal_all_mines(self) -> tuple[Position, ...]:
        newly_revealed: list[Position] = []
        for row in range(self._rows):
            for column in range(self._columns):
                cell = self._cells[row][column]
                if cell.is_mine and cell.state is not CellState.REVEALED:
                    cell.state = CellState.REVEALED
                    newly_revealed.append((row, column))
        return tuple(newly_revealed)

    def _calculate_adjacent_mines(self) -> None:
        for row in range(self._rows):
            for column in range(self._columns):
                self._cells[row][column].adjacent_mines = sum(
                    self._cells[neighbor_row][neighbor_column].is_mine
                    for neighbor_row, neighbor_column in self._neighbors(row, column)
                )

    def _neighbors(self, row: int, column: int) -> tuple[Position, ...]:
        return tuple(
            (neighbor_row, neighbor_column)
            for neighbor_row in range(max(0, row - 1), min(self._rows, row + 2))
            for neighbor_column in range(max(0, column - 1), min(self._columns, column + 2))
            if (neighbor_row, neighbor_column) != (row, column)
        )

    def _validate_position(self, row: int, column: int) -> None:
        if not self._in_bounds(row, column, self._rows, self._columns):
            raise IndexError(f"Position ({row}, {column}) is outside the board.")

    @staticmethod
    def _in_bounds(row: int, column: int, rows: int, columns: int) -> bool:
        return 0 <= row < rows and 0 <= column < columns

    def _notify_observers(self) -> None:
        snapshot = self.snapshot()
        for observer in tuple(self._observers):
            observer(snapshot)
