from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import random
from types import MappingProxyType
from typing import Iterable, Mapping, Protocol

from .game import MinesweeperGame, Position


class Difficulty(Enum):
    EASY = "Fácil"
    MEDIUM = "Medio"
    HARD = "Difícil"


@dataclass(frozen=True, slots=True)
class BoardConfig:
    rows: int
    columns: int
    mine_count: int

    def __post_init__(self) -> None:
        if (
            isinstance(self.rows, bool)
            or isinstance(self.columns, bool)
            or isinstance(self.mine_count, bool)
        ):
            raise ValueError("Los valores de configuración del tablero deben ser enteros.")
        if (
            not isinstance(self.rows, int)
            or not isinstance(self.columns, int)
            or not isinstance(self.mine_count, int)
        ):
            raise ValueError("Los valores de configuración del tablero deben ser enteros.")
        if self.rows <= 0 or self.columns <= 0:
            raise ValueError("Las dimensiones del tablero deben ser enteros positivos.")
        if self.mine_count < 0:
            raise ValueError("La cantidad de minas no puede ser negativa.")
        if self.mine_count >= self.rows * self.columns:
            raise ValueError("La cantidad de minas debe ser menor al total de casillas.")

    @property
    def total_cells(self) -> int:
        return self.rows * self.columns

DIFFICULTY_CONFIGS: Mapping[Difficulty, BoardConfig] = MappingProxyType(
    {
        Difficulty.EASY: BoardConfig(rows=9, columns=9, mine_count=10),
        Difficulty.MEDIUM: BoardConfig(rows=16, columns=16, mine_count=40),
        Difficulty.HARD: BoardConfig(rows=16, columns=30, mine_count=99),
    }
)


def get_board_config(difficulty: Difficulty) -> BoardConfig:
    if not isinstance(difficulty, Difficulty):
        raise TypeError("Se esperaba un miembro del enum Difficulty.")
    return DIFFICULTY_CONFIGS[difficulty]


class MinePlacementStrategy(Protocol):
    """Interfaz de estrategia para generar coordenadas únicas de minas."""

    def place_mines(
        self,
        rows: int,
        columns: int,
        mine_count: int,
    ) -> set[Position]:
        ...


class RandomMinePlacementStrategy:
    """Coloca minas de forma aleatoria sin duplicados en el tablero."""

    def __init__(self, rng: random.Random | None = None) -> None:
        self._rng = rng if rng is not None else random.Random()

    def place_mines(
        self,
        rows: int,
        columns: int,
        mine_count: int,
    ) -> set[Position]:
        config = BoardConfig(rows=rows, columns=columns, mine_count=mine_count)
        all_positions = [
            (r, c)
            for r in range(config.rows)
            for c in range(config.columns)
        ]
        selected = self._rng.sample(all_positions, config.mine_count)
        return set(selected)


class FixedMinePlacementStrategy:
    """Usa coordenadas de minas predefinidas."""

    def __init__(self, positions: Iterable[Position]) -> None:
        normalized: set[Position] = set()
        for pos in positions:
            if (
                not isinstance(pos, tuple)
                or len(pos) != 2
                or any(isinstance(v, bool) or not isinstance(v, int) for v in pos)
            ):
                raise ValueError("Cada posición de mina debe ser una tupla de enteros (fila, columna).")
            if pos in normalized:
                raise ValueError(f"No se permite la posición de mina duplicada {pos}.")
            normalized.add(pos)
        self._positions = frozenset(normalized)

    @property
    def positions(self) -> frozenset[Position]:
        return self._positions

    def place_mines(
        self,
        rows: int,
        columns: int,
        mine_count: int,
    ) -> set[Position]:
        config = BoardConfig(rows=rows, columns=columns, mine_count=mine_count)
        if len(self._positions) != config.mine_count:
            raise ValueError(
                f"La estrategia fija tiene {len(self._positions)} minas, "
                f"se esperaban {config.mine_count}."
            )
        for r, c in self._positions:
            if not (0 <= r < config.rows and 0 <= c < config.columns):
                raise ValueError(
                    f"La posición de mina {(r, c)} está fuera del tablero {config.rows}x{config.columns}."
                )
        return set(self._positions)


class MinesweeperGameFactory:
    """Fábrica que construye instancias configuradas de MinesweeperGame."""

    def __init__(
        self,
        default_strategy: MinePlacementStrategy | None = None,
    ) -> None:
        self._default_strategy: MinePlacementStrategy = (
            default_strategy
            if default_strategy is not None
            else RandomMinePlacementStrategy()
        )

    def create_from_difficulty(
        self,
        difficulty: Difficulty,
        strategy: MinePlacementStrategy | None = None,
    ) -> MinesweeperGame:
        config = get_board_config(difficulty)
        return self.create_from_config(config, strategy=strategy)

    def create_from_config(
        self,
        config: BoardConfig,
        strategy: MinePlacementStrategy | None = None,
    ) -> MinesweeperGame:
        active_strategy = strategy if strategy is not None else self._default_strategy
        mine_positions = set(
            active_strategy.place_mines(
                rows=config.rows,
                columns=config.columns,
                mine_count=config.mine_count,
            )
        )
        # Una estrategia propia (el Protocol permite cualquiera) podría devolver
        # una cantidad distinta de minas; MinesweeperGame no lo detectaría.
        if len(mine_positions) != config.mine_count:
            raise ValueError(
                f"La estrategia devolvió {len(mine_positions)} minas, "
                f"se esperaban {config.mine_count}."
            )
        return MinesweeperGame(
            rows=config.rows,
            columns=config.columns,
            mine_positions=mine_positions,
        )
