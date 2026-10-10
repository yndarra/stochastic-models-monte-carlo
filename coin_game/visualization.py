"""Графики для игры с монеткой."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

from .experiments import CapitalStats
from .game import Session

WIN_COLOR = "#2e8b57"
LOSS_COLOR = "#d1495b"


def rubles(x: float, _pos=None) -> str:
    """Подпись оси в рублях: 1.5M, 20K, 300."""
    sign = "−" if x < 0 else ""
    x = abs(x)
    if x >= 1e6:
        return f"{sign}{x / 1e6:.3g}M"
    if x >= 1e3:
        return f"{sign}{x / 1e3:.3g}K"
    return f"{sign}{x:.3g}"


def plot_sessions(groups: dict[float, list[Session]], path: Path) -> None:
    """Траектории баланса: по панели на каждый начальный капитал."""
    fig, axes = plt.subplots(1, len(groups), figsize=(6 * len(groups), 4.5), squeeze=False)
    for ax, (start, sessions) in zip(axes[0], groups.items(), strict=True):
        for s in sessions:
            ax.plot(s.history, color=WIN_COLOR if s.won else LOSS_COLOR, lw=0.9, alpha=0.75)
        ax.axhline(start, color="k", ls="--", lw=1)
        wins = sum(s.won for s in sessions)
        ax.set(title=f"Start {rubles(start)} ₽: {wins} of {len(sessions)} sessions won",
               xlabel="Game", ylabel="Balance, ₽")
        ax.yaxis.set_major_formatter(FuncFormatter(rubles))
        ax.grid(alpha=0.3)
    handles = [
        Line2D([], [], color=WIN_COLOR, label="Ended in profit"),
        Line2D([], [], color=LOSS_COLOR, label="Went broke"),
        Line2D([], [], color="k", ls="--", label="Starting capital"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    _save(fig, path)


def plot_capital_sweep(stats: list[CapitalStats], path: Path) -> None:
    """Вероятность выйти в плюс и длина сессии в зависимости от капитала."""
    s0 = np.array([s.start for s in stats])
    fig, (ax_p, ax_m) = plt.subplots(1, 2, figsize=(13, 4.5))

    ax_p.errorbar(s0, [s.win_rate * 100 for s in stats],
                  yerr=[2 * s.win_rate_err * 100 for s in stats],
                  fmt="o-", color=WIN_COLOR, capsize=3)
    ax_p.set(xscale="log", xlabel="Starting capital, ₽", ylabel="Sessions ending in profit, %",
             title="Chance to get ahead before going broke", ylim=(0, None))

    # Средний итог здесь не показываем: из-за тяжёлого хвоста выигрышей он
    # определяется единичными сессиями и почти не стабилизируется. Зато
    # длина сессии ведёт себя очень регулярно.
    games = np.array([s.median_games for s in stats])
    ax_m.plot(s0, games, "o-", color="#3b6fb6", label="Simulation (median)")
    ax_m.plot(s0, games[-1] * s0 / s0[-1], "k--", lw=1, label="∝ capital")
    ax_m.set(xscale="log", yscale="log", xlabel="Starting capital, ₽",
             ylabel="Games per session", title="Session length")
    ax_m.legend()
    for ax in (ax_p, ax_m):
        ax.xaxis.set_major_formatter(FuncFormatter(rubles))
        ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    _save(fig, path)


def plot_profit_histogram(stats: CapitalStats, path: Path) -> None:
    """Распределение итогов сессий для одного капитала."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    profits = stats.profits
    bins = np.linspace(profits.min(), np.percentile(profits, 99.5), 60)
    ax.hist(profits[profits <= 0], bins=bins, color=LOSS_COLOR, alpha=0.8, label="Went broke")
    ax.hist(profits[profits > 0], bins=bins, color=WIN_COLOR, alpha=0.8, label="Ended in profit")
    ax.axvline(stats.mean_profit, color="k", ls="--",
               label=f"Mean {stats.mean_profit:+.0f} ₽")
    ax.set(xlabel="Session result, ₽", ylabel="Sessions", yscale="log",
           title=f"Session results, start {rubles(stats.start)} ₽ ({stats.profits.size} sessions)")
    ax.xaxis.set_major_formatter(FuncFormatter(rubles))
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    _save(fig, path)


def plot_running_mean(running: np.ndarray, cost: float, path: Path) -> None:
    """Средний выигрыш за игру растёт как log2(N)/2 — петербургский парадокс."""
    n = np.arange(1, running.size + 1)
    idx = np.unique(np.logspace(0, np.log10(running.size), 2000).astype(int)) - 1
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(n[idx], running[idx], color="#3b6fb6", label="Simulated mean win per game")
    ax.plot(n[idx], np.log2(n[idx]) / 2, "k--", lw=1, label=r"$\log_2(N)/2$")
    ax.axhline(cost, color=LOSS_COLOR, ls=":", label=f"Entry fee {cost:g} ₽")
    ax.set(xscale="log", xlabel="Games played N", ylabel="Mean win per game, ₽",
           title="The mean never settles: St. Petersburg paradox")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    _save(fig, path)


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close(fig)
