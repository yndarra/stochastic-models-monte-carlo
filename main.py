"""Точка входа: эксперименты Монте-Карло с игрой в монетку.

Примеры::

    python main.py               # все эксперименты
    python main.py paths         # траектории баланса для 1K, 100K и 1M ₽
    python main.py capital       # вероятность выигрыша от начального капитала
    python main.py paradox       # средний выигрыш за игру от числа игр
    python main.py capital --sessions 5000 --seed 7
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

from coin_game import experiments as exp
from coin_game import visualization as vis

COST = 20.0  # цена участия в одной игре, ₽


def run_paths(out: Path, rng: np.random.Generator, sessions: int) -> None:
    """По 20 сессий для трёх капиталов из задания: 1 000, 100 000 и 1 000 000 ₽."""
    groups = {}
    for start in (1_000, 100_000, 1_000_000):
        groups[start] = exp.sample_sessions(start, COST, 20, rng)
    vis.plot_sessions(groups, out / "sessions.png")

    for start in (1_000, 100_000, 1_000_000):
        stats = exp.capital_stats(start, COST, sessions, rng)
        print(f"  {vis.rubles(start):>5} ₽: выход в плюс {stats.win_rate:6.1%}, "
              f"средний итог {stats.mean_profit:+12,.0f} ₽, "
              f"медиана {stats.median_games:>9,.0f} игр".replace(",", " "))
        if start == 1_000:
            vis.plot_profit_histogram(stats, out / "profit_histogram.png")


def run_capital(out: Path, rng: np.random.Generator, sessions: int) -> None:
    """Как вероятность выйти в плюс зависит от начального капитала."""
    starts = np.round(np.logspace(2, 7, 11), -1)
    stats = []
    for start in starts:
        stats.append(exp.capital_stats(start, COST, sessions, rng))
        s = stats[-1]
        print(f"  S0 = {vis.rubles(start):>6} ₽: "
              f"P(плюс) = {s.win_rate:5.1%} ± {2 * s.win_rate_err:.1%}, "
              f"средний итог {s.mean_profit / start:+6.1%} капитала")
    vis.plot_capital_sweep(stats, out / "capital_sweep.png")


def run_paradox(out: Path, rng: np.random.Generator, _sessions: int) -> None:
    """Средний выигрыш за 10⁷ игр — не сходится, а растёт как log2(N)/2."""
    running = exp.running_mean_win(10_000_000, rng)
    print(f"  средний выигрыш после 10³ игр: {running[999]:.2f} ₽, "
          f"после 10⁷: {running[-1]:.2f} ₽ (log2(N)/2 = {np.log2(1e7) / 2:.2f})")
    vis.plot_running_mean(running, COST, out / "paradox.png")


def main() -> None:
    parser = argparse.ArgumentParser(description="Monte Carlo simulation of a coin-flip game")
    parser.add_argument("experiment", nargs="?", default="all",
                        choices=["all", "paths", "capital", "paradox"])
    parser.add_argument("--sessions", type=int, default=2000, help="сессий на точку")
    parser.add_argument("--seed", type=int, default=42, help="seed генератора случайных чисел")
    parser.add_argument("--out", type=Path, default=Path("images"), help="папка для картинок")
    args = parser.parse_args()

    print(f"Цена игры {COST:g} ₽, выигрыш 2^n ₽ за n орлов подряд до первой решки.")
    tasks = {
        "paths": ("Траектории сессий", run_paths),
        "capital": ("Зависимость от капитала", run_capital),
        "paradox": ("Петербургский парадокс", run_paradox),
    }
    rng = np.random.default_rng(args.seed)
    selected = tasks if args.experiment == "all" else {args.experiment: tasks[args.experiment]}
    for title, task in selected.values():
        started = time.perf_counter()
        print(f"{title}...")
        task(args.out, rng, args.sessions)
        print(f"  готово за {time.perf_counter() - started:.1f} с")
    print(f"Картинки сохранены в {args.out.resolve()}")


if __name__ == "__main__":
    main()
