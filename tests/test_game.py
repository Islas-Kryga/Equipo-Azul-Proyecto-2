import pytest

from src.buscaminas.model import CellState, GameStatus, MinesweeperGame


def test_reveals_safe_cell_and_reports_adjacent_mines() -> None:
    game = MinesweeperGame(3, 3, {(0, 0)})

    result = game.reveal(1, 1)

    assert result.changed
    assert result.first_reveal
    assert game.status is GameStatus.IN_PROGRESS
    assert game.snapshot().cells[1][1].adjacent_mines == 1
    assert game.snapshot().cells[1][1].state is CellState.REVEALED


def test_corner_cell_counts_only_three_diagonal_and_side_neighbors() -> None:
    game = MinesweeperGame(3, 3, {(0, 1), (1, 0), (1, 1)})

    game.reveal(0, 0)

    assert game.snapshot().cells[0][0].adjacent_mines == 3


def test_first_reveal_can_hit_mine_and_reveals_all_mines() -> None:
    game = MinesweeperGame(2, 3, {(0, 0), (1, 2)})

    result = game.reveal(0, 0)
    snapshot = game.snapshot()

    assert result.changed
    assert result.first_reveal
    assert result.status is GameStatus.LOST
    assert snapshot.cells[0][0].is_mine is True
    assert snapshot.cells[1][2].is_mine is True
    assert snapshot.cells[1][2].state is CellState.REVEALED


def test_revealing_empty_cell_expands_but_preserves_flagged_cells() -> None:
    game = MinesweeperGame(4, 4, {(3, 3)})
    game.toggle_flag(0, 0)

    result = game.reveal(0, 1)

    assert (0, 0) not in result.newly_revealed
    assert game.snapshot().cells[0][0].state is CellState.FLAGGED
    assert game.snapshot().cells[2][2].state is CellState.REVEALED
    assert game.snapshot().cells[3][3].state is CellState.COVERED
    assert game.status is GameStatus.IN_PROGRESS


def test_flag_can_be_toggled_and_prevents_reveal() -> None:
    game = MinesweeperGame(2, 2, {(1, 1)})

    placed = game.toggle_flag(0, 0)
    blocked = game.reveal(0, 0)
    removed = game.toggle_flag(0, 0)

    assert placed.changed
    assert not blocked.changed
    assert blocked.first_reveal is False
    assert removed.changed
    assert game.snapshot().cells[0][0].state is CellState.COVERED
    assert game.status is GameStatus.READY


def test_flagging_a_safe_cell_does_not_prevent_winning() -> None:
    game = MinesweeperGame(1, 2, {(0, 1)})
    game.toggle_flag(0, 0)
    game.toggle_flag(0, 0)

    result = game.reveal(0, 0)

    assert result.status is GameStatus.WON
    assert game.status is GameStatus.WON


def test_game_ends_after_all_safe_cells_are_revealed() -> None:
    game = MinesweeperGame(1, 2, {(0, 1)})

    game.reveal(0, 0)

    assert game.status is GameStatus.WON


def test_zero_mine_board_expands_and_wins() -> None:
    game = MinesweeperGame(3, 4, ())

    result = game.reveal(1, 2)

    assert len(result.newly_revealed) == 12
    assert result.status is GameStatus.WON


def test_winning_does_not_expose_mines() -> None:
    game = MinesweeperGame(1, 2, {(0, 1)})

    game.reveal(0, 0)

    assert game.snapshot().cells[0][1].is_mine is None


def test_cannot_flag_a_revealed_cell() -> None:
    game = MinesweeperGame(1, 2, {(0, 1)})
    game.reveal(0, 0)

    result = game.toggle_flag(0, 0)

    assert not result.changed
    assert game.snapshot().cells[0][0].state is CellState.REVEALED


def test_actions_after_game_over_do_not_change_board() -> None:
    game = MinesweeperGame(1, 2, {(0, 1)})
    game.reveal(0, 0)
    before = game.snapshot()

    reveal_result = game.reveal(0, 1)
    flag_result = game.toggle_flag(0, 0)

    assert not reveal_result.changed
    assert not flag_result.changed
    assert game.snapshot() == before


def test_snapshot_does_not_expose_unrevealed_mines() -> None:
    game = MinesweeperGame(2, 2, {(1, 1)})

    snapshot = game.snapshot()

    assert snapshot.cells[1][1].is_mine is None


def test_observers_receive_snapshots_when_board_changes() -> None:
    game = MinesweeperGame(2, 2, {(1, 1)})
    received = []
    unsubscribe = game.subscribe(received.append)

    game.toggle_flag(0, 0)
    game.reveal(1, 0)
    unsubscribe()
    game.toggle_flag(0, 1)

    assert len(received) == 2
    assert received[0].cells[0][0].state is CellState.FLAGGED
    assert received[1].cells[1][0].state is CellState.REVEALED


@pytest.mark.parametrize(
    ("rows", "columns", "mines"),
    [
        (0, 2, set()),
        (2, -1, set()),
        (1, 1, {(0, 0)}),
        (2, 2, {(2, 0)}),
        (2, 2, ((0, 0), (0, 0))),
    ],
)
def test_rejects_invalid_board_configuration(rows, columns, mines) -> None:
    with pytest.raises(ValueError):
        MinesweeperGame(rows, columns, mines)


@pytest.mark.parametrize("position", [(-1, 0), (0, 2), (2, 0)])
def test_rejects_out_of_bounds_moves(position) -> None:
    game = MinesweeperGame(2, 2, {(1, 1)})

    with pytest.raises(IndexError):
        game.reveal(*position)
