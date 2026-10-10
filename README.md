# Monte Carlo: a Coin Game and the St. Petersburg Paradox

[![tests](https://github.com/yndarra/stochastic-models-monte-carlo/actions/workflows/tests.yml/badge.svg)](https://github.com/yndarra/stochastic-models-monte-carlo/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

**English** | [Русский](README.ru.md)

A Monte Carlo study of a gambling game with an **infinite expected payoff** that
still ruins most players. The program simulates millions of games to show why a
"profitable on average" game is a bad deal for anyone with finite capital.

![Balance trajectories](images/sessions.png)

> Coursework for the *Computer Modelling* university course.

## The game

* Each game costs **20 ₽** to enter.
* A coin is tossed until the first tails.
* If `n ≥ 1` heads came up before it, the player wins `2ⁿ ₽`; tails on the first
  toss wins nothing.

The probability of exactly `n` heads is `2^−(n+1)`, so the expected win is

```
E[win] = Σ 2ⁿ · 2^−(n+1) = ½ + ½ + ½ + … = ∞
```

so by expectation alone any finite entry fee looks worth paying. This is the
**St. Petersburg paradox**. Every payoff level adds only ½ ₽ to the expectation,
and the median win is zero.

**The player's strategy:** start with capital `S₀` and keep playing until the
balance first exceeds `S₀` (the player gets ahead and leaves) or until there is
not enough money for the next game (ruin).

## Implementation

The number of heads before the first tails follows a geometric distribution, so
`numpy.random.Generator.geometric` draws thousands of games in one call. A
session is simulated in vectorized chunks of games. The balance is a cumulative
sum, and the first index that crosses either stopping boundary ends the session.
Even sessions of hundreds of thousands of games take milliseconds, and the whole
study (≈ 28,000 sessions plus 10⁷ single games) runs in about a minute.

## Results

### Starting capital of 1K, 100K and 1M ₽

Each figure below comes from 2000 sessions per starting capital (seed 42).

| Starting capital | Sessions ending in profit | Mean result | Median session length |
|---|---|---|---|
| 1 000 ₽ | 18.0% | −329 ₽ | 58 games |
| 100 000 ₽ | 35.2% | −43 385 ₽ | 6 998 games |
| 1 000 000 ₽ | 45.1% | −70 031 ₽ | 76 844 games |

A typical session is a slow, steady loss of 20 ₽ per game, interrupted now and
then by a big win. Most sessions never see a win big enough to recover the
losses.

![Session results for 1K ₽](images/profit_histogram.png)

The outcome is strongly bimodal: either the player loses everything, or ends
slightly ahead. A handful of sessions win several times the starting capital,
and these rare outliers drive the mean. That is also why the mean result
fluctuates so much from run to run.

### Dependence on the starting capital

![Win probability and session length against capital](images/capital_sweep.png)

The more money the player has, the longer they can wait for a big win. The chance
of getting ahead grows roughly linearly with the *logarithm* of the capital,
from 9% at 100 ₽ to 53% at 10 M ₽. The session length grows almost in proportion to
the capital.

### The paradox in one picture

![Running mean of the win per game](images/paradox.png)

The sample mean of the win per game does not converge. It creeps up roughly like
`log₂(N)/2`, because the more games are played, the bigger the largest win that
has had time to happen. After 10⁷ games the average is only **11.06 ₽**,
against `log₂(10⁷)/2 ≈ 11.63`. To beat the 20 ₽ fee on average you would need
around `2⁴⁰ ≈ 10¹²` games.

## Getting started

```bash
git clone https://github.com/yndarra/stochastic-models-monte-carlo.git
cd stochastic-models-monte-carlo
python -m venv .venv
.venv/Scripts/activate        # Windows; on Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

python main.py                # every experiment (about 1 min), images go to images/
python main.py capital        # one experiment: paths | capital | paradox
python main.py capital --sessions 5000 --seed 7
```

To run the tests:

```bash
pip install -r requirements-dev.txt
pytest
```

## Project structure

```
coin_game/
├── game.py           # payoff distribution, vectorized session simulation
├── experiments.py    # capital statistics, sample paths, running mean
└── visualization.py  # plots
tests/                # distribution and stopping-rule tests
main.py               # command-line entry point
```

## References

* [St. Petersburg paradox](https://en.wikipedia.org/wiki/St._Petersburg_paradox) on Wikipedia.
* W. Feller. *An Introduction to Probability Theory and Its Applications*, Vol. 1, ch. X.4.

## License

[MIT](LICENSE)
