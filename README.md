# MyBot_v4_2 — Fullhouse Poker Bot

`MyBot_v4_2` is a No-Limit Texas Hold'em bot built for the Fullhouse poker bot hackathon, ranked **46/400+** in Qualifier-I.

The bot combines:

- rule-based preflop ranges
- Monte Carlo postflop equity estimation
- pot-odds based call/fold decisions
- stack-risk controls
- opponent-style and board-texture adjustments
- local evaluation against multiple opponent styles

Final bot:

- `bots/mybot/bot.py`

---

## Strategy Summary

The strategy is split into two parts.

```text
Preflop:
    hand ranges + position heuristic + stack-risk gates

Postflop:
    Monte Carlo equity + pot odds + risk margins
```

### Preflop

Preflop decisions are range-based. The bot groups hole cards into categories such as:

- premium pairs
- strong broadways
- medium hands
- speculative suited hands
- late-position extras

It then adjusts by:

- position heuristic
- active opponent count
- multiway risk
- table aggression
- amount owed relative to stack

The goal is to enter good pots while avoiding dominated hands that can lose large stacks.

### Postflop

Postflop decisions use `eval7` Monte Carlo simulation.

The bot estimates expected pot share by sampling unknown opponent cards and future community cards. Ties receive fractional credit, so the estimate is closer to expected pot fraction than simple win probability.

The bot then compares:

```text
estimated_equity
```

against:

```text
required_equity = pot_odds + risk/context margins
```

If equity is high enough, the bot calls. If equity is much stronger, it may raise for value.

---

## Main Features

- **Monte Carlo equity**: estimates postflop hand strength from simulated futures.
- **Pot odds discipline**: avoids calling unless the price is justified.
- **Stack-risk margins**: requires more equity for larger stack commitments.
- **Multiway caution**: tightens decisions when more opponents remain active.
- **Opponent profiling**: uses recent actions to identify styles such as aggressive, tight, passive, or calling-station.
- **Board texture checks**: adds caution on wet boards when holding vulnerable made hands.
- **Evaluation tools**: includes local scripts for matches, Swiss-style simulations, candidate comparison, and mixed-pool stress tests.

---

## Project Files

- `bots/mybot/bot.py` — final bot source
- `v4_2_implemented_strategy.md` — detailed final strategy notes
- `experiment_log.md` — experiments and lessons learned
- `docs/preflop_strategy_v4_2.md` — focused preflop strategy notes
- `scripts/qualifier_sim.py` — Swiss-style local simulation
- `scripts/compare_candidate_swiss.py` — candidate-vs-baseline comparison
- `scripts/compare_mixed_pool_swiss.py` — mixed opponent-pool stress tests
- `scripts/measure_decision_latency.py` — lightweight decision latency check

Note: the evaluation scripts show the testing framework, but some private sparring bot implementations and raw experiment outputs are intentionally omitted from this public-facing repo.

---

## What I Learned

The hardest part was not adding more logic. It was deciding which ideas to reject.

Several reasonable-sounding changes did not survive testing:

- broader river guards
- broader wet-board guards
- cleaner but more conservative margin rewrites
- larger value sizing
- higher fixed Monte Carlo counts
- adaptive Monte Carlo for close spots

The final version keeps the strategy that was most robust in local evaluation rather than the one that looked most elegant on paper.
