"""Pruebas unitarias de board_factory: configuraciones, estrategias y fábrica."""
from __future__ import annotations

from dataclasses import FrozenInstanceError
import random
import unittest

from src.buscaminas.model import (
    DIFFICULTY_CONFIGS,
    BoardConfig,
    CellState,
    Difficulty,
    FixedMinePlacementStrategy,
    GameStatus,
    MinesweeperGame,
    MinesweeperGameFactory,
    RandomMinePlacementStrategy,
    get_board_config,
)


def _count_mines(game: MinesweeperGame) -> int:
    """Cuenta las minas descubriendo casillas hasta perder o ganar."""
    for row in range(game.rows):
        for column in range(game.columns):
            game.reveal(row, column)
            if game.status in (GameStatus.LOST, GameStatus.WON):
                break
        if game.status in (GameStatus.LOST, GameStatus.WON):
            break

    cells = [cell for row in game.snapshot().cells for cell in row]
    if game.status is GameStatus.LOST:
        return sum(1 for cell in cells if cell.is_mine)
    return sum(1 for cell in cells if cell.state is not CellState.REVEALED)


class RecordingStrategy:
    """Registra llamadas recibidas y devuelve posiciones fijas."""

    def __init__(self, positions: set[tuple[int, int]]) -> None:
        self._positions = positions
        self.calls: list[tuple[int, int, int]] = []

    def place_mines(self, rows: int, columns: int, mine_count: int) -> set[tuple[int, int]]:
        self.calls.append((rows, columns, mine_count))
        return set(self._positions)


class BoardFactoryTests(unittest.TestCase):
    def test_difficulty_labels(self) -> None:
        self.assertEqual(Difficulty.EASY.value, "Fácil")
        self.assertEqual(Difficulty.MEDIUM.value, "Medio")
        self.assertEqual(Difficulty.HARD.value, "Difícil")

    def test_classic_difficulties_and_density(self) -> None:
        expected = {
            Difficulty.EASY: BoardConfig(9, 9, 10),
            Difficulty.MEDIUM: BoardConfig(16, 16, 40),
            Difficulty.HARD: BoardConfig(16, 30, 99),
        }
        self.assertEqual(set(DIFFICULTY_CONFIGS), set(Difficulty))
        for difficulty, config in expected.items():
            with self.subTest(difficulty=difficulty):
                self.assertEqual(get_board_config(difficulty), config)

        densities = [
            get_board_config(d).mine_count / get_board_config(d).total_cells
            for d in (Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD)
        ]
        self.assertEqual(densities, sorted(densities))

    def test_board_config_boundaries_and_validation(self) -> None:
        self.assertEqual(BoardConfig(3, 3, 0).mine_count, 0)
        self.assertEqual(BoardConfig(5, 5, 24).mine_count, 24)
        with self.assertRaises(FrozenInstanceError):
            BoardConfig(9, 9, 10).rows = 5  # type: ignore[misc]

        for rows, columns, mines in ((0, 5, 1), (-1, 5, 1), (5, 5, -1), (5, 5, 25), (5, 5, 26)):
            with self.subTest(rows=rows, columns=columns, mines=mines):
                with self.assertRaises(ValueError):
                    BoardConfig(rows, columns, mines)

    def test_random_strategy_bounds_and_seed(self) -> None:
        first = RandomMinePlacementStrategy(random.Random(42)).place_mines(9, 9, 10)
        second = RandomMinePlacementStrategy(random.Random(42)).place_mines(9, 9, 10)
        different = RandomMinePlacementStrategy(random.Random(99)).place_mines(9, 9, 10)

        self.assertEqual(len(first), 10)
        self.assertTrue(all(0 <= r < 9 and 0 <= c < 9 for r, c in first))
        self.assertEqual(first, second)
        self.assertNotEqual(first, different)

    def test_fixed_strategy_validation_and_immutability(self) -> None:
        strategy = FixedMinePlacementStrategy([(0, 0), (1, 1)])
        self.assertIsInstance(strategy.positions, frozenset)
        self.assertEqual(strategy.place_mines(3, 3, 2), {(0, 0), (1, 1)})

        with self.assertRaises(ValueError):
            FixedMinePlacementStrategy([(0, 0), (0, 0)])
        with self.assertRaises(ValueError):
            strategy.place_mines(3, 3, 3)
        with self.assertRaises(ValueError):
            FixedMinePlacementStrategy([(3, 0)]).place_mines(3, 3, 1)

    def test_new_game_is_ready_and_covered(self) -> None:
        game = MinesweeperGameFactory().create_from_difficulty(Difficulty.EASY)
        self.assertEqual(game.status, GameStatus.READY)
        self.assertTrue(
            all(c.state is CellState.COVERED for row in game.snapshot().cells for c in row)
        )

    def test_fixed_strategy_builds_deterministic_board(self) -> None:
        factory = MinesweeperGameFactory(FixedMinePlacementStrategy([(0, 0)]))
        game = factory.create_from_config(BoardConfig(3, 3, 1))
        self.assertEqual(game.reveal(0, 0).status, GameStatus.LOST)

    def test_factory_passes_difficulty_config_to_strategy(self) -> None:
        spy = RecordingStrategy(RandomMinePlacementStrategy().place_mines(16, 30, 99))
        MinesweeperGameFactory().create_from_difficulty(Difficulty.HARD, strategy=spy)
        self.assertEqual(spy.calls, [(16, 30, 99)])

    def test_factory_rejects_out_of_bounds_mines_from_strategy(self) -> None:
        with self.assertRaises(ValueError):
            MinesweeperGameFactory().create_from_config(
                BoardConfig(3, 3, 1),
                strategy=RecordingStrategy({(5, 5)}),
            )

    def test_factory_uses_default_strategy_and_explicit_overrides_it(self) -> None:
    default = RecordingStrategy({(0, 0)})
    override = RecordingStrategy({(1, 1)})
    factory = MinesweeperGameFactory(default_strategy=default)

    factory.create_from_config(BoardConfig(3, 3, 1))
    self.assertEqual((len(default.calls), len(override.calls)), (1, 0))

    factory.create_from_config(BoardConfig(3, 3, 1), strategy=override)
    self.assertEqual((len(default.calls), len(override.calls)), (1, 1))

    def test_factory_returns_independent_games(self) -> None:
        factory = MinesweeperGameFactory(FixedMinePlacementStrategy([(0, 0)]))
        first = factory.create_from_config(BoardConfig(3, 3, 1))
        second = factory.create_from_config(BoardConfig(3, 3, 1))
        self.assertIsNot(first, second)
        first.reveal(2, 2)
        self.assertEqual(second.status, GameStatus.READY)

    def test_factory_rejects_wrong_mine_count_from_strategy(self) -> None:
        with self.assertRaises(ValueError):
            MinesweeperGameFactory().create_from_config(
                BoardConfig(3, 3, 1),
                strategy=RecordingStrategy({(0, 0), (1, 1)}),
            )

    def test_factory_creates_expected_mines_per_difficulty(self) -> None:
        factory = MinesweeperGameFactory(RandomMinePlacementStrategy(random.Random(7)))
        for diff, mines in (
            (Difficulty.EASY, 10),
            (Difficulty.MEDIUM, 40),
            (Difficulty.HARD, 99),
        ):
            with self.subTest(diff=diff):
                self.assertEqual(_count_mines(factory.create_from_difficulty(diff)), mines)


if __name__ == "__main__":
    unittest.main()