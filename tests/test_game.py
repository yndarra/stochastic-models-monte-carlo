"""Тесты игры с монеткой."""

import numpy as np
import pytest

from coin_game import play_games, play_session
from coin_game.experiments import running_mean_win


def test_win_distribution_matches_geometric_law():
    rng = np.random.default_rng(0)
    wins = play_games(400_000, rng)
    # P(выигрыш 0) = P(сразу решка) = 1/2, P(2) = 1/4, P(4) = 1/8.
    for value, prob in ((0, 0.5), (2, 0.25), (4, 0.125)):
        assert np.mean(wins == value) == pytest.approx(prob, abs=0.003)
    # Все выигрыши — 0 или степени двойки.
    nonzero = wins[wins > 0]
    assert np.all(np.log2(nonzero) == np.round(np.log2(nonzero)))


@pytest.mark.parametrize("start", [100, 1000, 50_000])
def test_session_ends_in_profit_or_ruin(start):
    rng = np.random.default_rng(1)
    for _ in range(200):
        s = play_session(start, 20, rng, keep_history=True)
        assert s.won == (s.final > start)
        if not s.won:
            assert s.final < 20
        # До последней игры баланс не выходил за границы остановки.
        assert np.all((s.history[:-1] <= start) & (s.history[:-1] >= 20))
        assert s.history.size == s.games + 1


def test_cannot_play_without_money():
    s = play_session(10, 20, np.random.default_rng(2))
    assert s.games == 0 and not s.won


def test_more_capital_more_chance_to_win():
    rng = np.random.default_rng(3)
    rates = [np.mean([play_session(s, 20, rng).won for _ in range(1500)]) for s in (100, 100_000)]
    assert rates[1] > rates[0] + 0.15


def test_running_mean_grows_like_log2():
    running = running_mean_win(2_000_000, np.random.default_rng(4))
    # Рост медленный и шумный, поэтому проверяем лишь порядок величины.
    assert 6 < running[-1] < 16
