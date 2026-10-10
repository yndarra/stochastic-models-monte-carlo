"""Игра с монеткой — вариант петербургского парадокса.

Правила одной игры:

* игрок платит ``cost`` рублей за участие;
* монетку бросают до первой решки;
* если до этого выпало ``n ≥ 1`` орлов подряд, игрок получает ``2^n`` рублей,
  если решка выпала сразу — не получает ничего.

Число орлов до первой решки имеет геометрическое распределение:
``P(n) = 2^{−(n+1)}``. Математическое ожидание выигрыша бесконечно:

    E[выигрыш] = Σ_{n≥1} 2^n · 2^{−(n+1)} = 1/2 + 1/2 + 1/2 + … = ∞,

поэтому «справедливой» конечной цены за участие не существует. Это и есть
петербургский парадокс. При этом медианный выигрыш за игру равен нулю, а
каждый уровень выигрыша вносит в ожидание лишь 1/2 рубля, так что на
практике игра долго выглядит убыточной.

**Стратегия игрока (сессия):** начать с капитала ``S0`` и играть, пока
баланс впервые не превысит ``S0`` (выход в плюс) или пока денег не перестанет
хватать на следующую игру (разорение).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def play_games(n_games: int, rng: np.random.Generator) -> np.ndarray:
    """Сыграть ``n_games`` игр и вернуть выигрыши (без учёта цены участия).

    ``rng.geometric(0.5)`` — номер первого успеха (решки), начиная с 1,
    поэтому число орлов до неё на единицу меньше.
    """
    heads = rng.geometric(0.5, size=n_games) - 1
    return np.where(heads > 0, 2.0**heads, 0.0)


@dataclass
class Session:
    """Итог одной сессии."""

    start: float           # начальный капитал
    final: float           # итоговый баланс
    games: int             # сколько игр сыграно
    won: bool              # True — вышли в плюс, False — разорились
    history: np.ndarray | None = None  # баланс после каждой игры (если запрошен)

    @property
    def profit(self) -> float:
        return self.final - self.start


def play_session(
    start: float,
    cost: float,
    rng: np.random.Generator,
    keep_history: bool = False,
    chunk: int = 4096,
    max_games: int = 50_000_000,
) -> Session:
    """Играть до выхода в плюс или до разорения.

    Игры разыгрываются пачками по ``chunk`` штук и обрабатываются векторно:
    баланс после каждой игры — накопленная сумма ``выигрыш − cost``. Затем
    ищется первая игра, после которой сессия заканчивается. Так даже сессии
    из миллионов игр считаются за доли секунды.
    """
    if start < cost:
        return Session(start, start, 0, False, np.array([start]) if keep_history else None)

    balance = float(start)
    games = 0
    pieces = [np.array([balance])] if keep_history else None

    while games < max_games:
        net = play_games(chunk, rng) - cost
        path = balance + np.cumsum(net)
        # Сессия заканчивается после игры, в которой баланс стал > start
        # (выигрыш) или < cost (на следующую игру уже не хватает).
        stop = np.flatnonzero((path > start) | (path < cost))
        end = stop[0] + 1 if stop.size else chunk
        if keep_history:
            pieces.append(path[:end])
        balance = float(path[end - 1])
        games += end
        if stop.size:
            break
    else:
        raise RuntimeError("Сессия не завершилась за max_games игр")

    history = np.concatenate(pieces) if keep_history else None
    return Session(start, balance, games, balance > start, history)


def expected_win_truncated(max_heads: int) -> float:
    """Ожидание выигрыша, если число орлов ограничено ``max_heads``.

    Каждый уровень ``n = 1..max_heads`` вносит ровно 1/2 рубля, поэтому
    ожидание растёт лишь логарифмически от максимального выигрыша:
    ``max_heads / 2``.
    """
    return max_heads / 2
