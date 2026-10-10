"""Эксперименты Монте-Карло над игрой с монеткой."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .game import Session, play_games, play_session


@dataclass
class CapitalStats:
    """Статистика сессий для одного начального капитала."""

    start: float
    win_rate: float          # доля сессий, закончившихся выходом в плюс
    win_rate_err: float      # стандартная ошибка доли (биномиальная)
    mean_profit: float       # средний итог сессии, руб.
    median_games: float      # медианная длина сессии, игр
    profits: np.ndarray      # итог каждой сессии


def capital_stats(
    start: float, cost: float, n_sessions: int, rng: np.random.Generator
) -> CapitalStats:
    """Сыграть ``n_sessions`` сессий с капиталом ``start`` и собрать статистику."""
    sessions = [play_session(start, cost, rng) for _ in range(n_sessions)]
    won = np.array([s.won for s in sessions])
    p = won.mean()
    return CapitalStats(
        start=start,
        win_rate=float(p),
        win_rate_err=float(np.sqrt(p * (1 - p) / n_sessions)),
        mean_profit=float(np.mean([s.profit for s in sessions])),
        median_games=float(np.median([s.games for s in sessions])),
        profits=np.array([s.profit for s in sessions]),
    )


def sample_sessions(start: float, cost: float, n: int, rng: np.random.Generator) -> list[Session]:
    """Несколько сессий с полной историей баланса — для графиков траекторий."""
    return [play_session(start, cost, rng, keep_history=True) for _ in range(n)]


def running_mean_win(n_games: int, rng: np.random.Generator) -> np.ndarray:
    """Средний выигрыш за игру после первых 1, 2, …, ``n_games`` игр.

    Для петербургской игры он не сходится к константе, а медленно растёт —
    примерно как ``log2(N) / 2``: чем больше сыграно, тем крупнее самый
    большой выигрыш, который успел выпасть.
    """
    wins = play_games(n_games, rng)
    return np.cumsum(wins) / np.arange(1, n_games + 1)
