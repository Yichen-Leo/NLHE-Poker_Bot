# Experiment Log

This document records the main experiments and lessons from developing `MyBot_v4_2`.

It is intentionally separate from `v4_2_implemented_strategy.md`.

- `v4_2_implemented_strategy.md` explains what the final bot does.
- This file explains what we tried, what failed, and what we learned.

---

## 1. Development Philosophy

The most important rule during development was:

> Do not trust a change just because it fixes one bad seed.

Many candidate strategies looked better on a specific failure case, but became worse across fresh seeds or different opponent pools.

The project gradually became less about adding more logic and more about protecting a strong baseline from overfitting.

---

## 2. Version Timeline

### v1 — Basic Rule Bot

The first bot was a simple rule-based player:

- play strong preflop hands
- call cheaply with medium hands
- fold weak hands against pressure
- use very basic postflop made-hand checks

This version was useful for learning the engine, but it was too shallow because it did not estimate actual equity.

### v2 — Monte Carlo Postflop

v2 introduced `eval7` Monte Carlo simulation.

The bot began estimating expected pot share instead of only checking labels like pair or high card.

This became the foundation of all later versions.

### v3.x — Risk Controls and Evaluation Tools

The v3 series added:

- stronger preflop ranges
- stack-risk gates
- multiway pressure controls
- board texture checks
- early opponent-style profiling
- more testing scripts

The key learning was that postflop calls needed more than pot odds. They also needed context: stack risk, pressure, board danger, and opponent behavior.

### v4.2 — Final Baseline

v4.2 became the final baseline because it had the best balance of:

- chip accumulation
- stability
- risk control
- robustness across fresh seeds
- resistance to overfitting

Most later experiments tried to replace or harden v4.2, but did not clearly improve it.

---

## 3. Defensive Guard Experiments

Several experiments tried to reduce large losses and busts.

Ideas included:

- broad river guards
- broad wet-board guards
- vulnerable-hand guards
- turn pressure guards
- near-all-in floors
- tighter player-style penalties

These ideas were strategically reasonable. Many large losses came from marginal made hands paying too much on dangerous boards.

However, the broad guards often failed because they blocked profitable paths too:

- value raises with strong hands
- profitable river calls
- bluff-catching against aggressive opponents
- high-EV continuation lines that looked dangerous locally

Lesson:

> Reducing a visible bad loss is not enough. A guard must improve the full distribution.

---

## 4. v4.3 Series

The v4.3 family was the main attempt to make v4.2 cleaner and more logically organized.

### 4.1 v4.3a — Cleaner Call Formula

The idea was to replace v4.2's overlapping margins with a cleaner formula:

```text
required_equity =
    pot_odds
  + risk_margin
  + hand_pressure
  + player_style_action
  + opponent_commitment
  + street_margin
  + stack_preservation
```

This was easier to explain, but it shifted the empirical decision boundary too much.

It saved some bad calls, but also folded spots that v4.2 turned into profit.

Lesson:

> Cleaner logic is not automatically better policy.

### 4.2 v4.3b — Wet Board and Vulnerable Hand Guard

This candidate targeted spots like:

```text
wet board + vulnerable made hand + later street + pressure
```

It reduced some dangerous calls, but hurt overall performance by blocking too many profitable river and turn paths.

Lesson:

> The idea was valid, but the implementation was too blunt.

### 4.3 soft1 / soft2

We then softened the v4.3 ideas:

- smaller penalties
- narrower river-only guards
- less punishment for strong hands
- reduced pressure from player-style margins

These versions recovered some flexibility, but still did not clearly beat v4.2.

Final v4.3 lesson:

> v4.2 was messy, but its messy margins preserved a useful balance.

---

## 5. Value Sizing Experiments

We tested larger raises with very strong hands, especially on turn and river.

The hypothesis:

> If we have a very strong hand, larger sizing should extract more value.

The problem:

- larger raises increased variance
- some opponents folded earlier
- some spots overcommitted the stack
- the improved value paths were not consistent enough

Final decision:

Keep v4.2's original sizing behavior.

---

## 6. River Raise Profiling

River losses looked scary because many large pots are decided there.

But profiling showed that river aggression was also one of v4.2's main profit engines.

Broad river guards were therefore rejected.

Lesson:

> A street with many losses can also be the street with the largest profits.

---

## 7. Monte Carlo Count Experiments

Near the end, we tested whether more simulations would improve decisions.

Candidates included:

- fixed MC300
- fixed MC350
- fixed MC400
- adaptive MC for close call/fold spots

The adaptive idea was:

```text
Default: MC250
If abs(equity - required_equity) <= 0.03:
    recompute with more simulations
```

Latency was not the main issue. The variants stayed comfortably below the action time limit in local testing.

The real issue was strategic stability. More simulations changed marginal decisions, and those changes were not consistently profitable.

Lesson:

> More precise equity estimation is not automatically a better policy.

Final decision:

Keep `MONTE_CARLO_SIMS = 250`.

---

## 8. True Position Candidate

We investigated whether the preflop position heuristic should be replaced.

v4.2 uses a simple seat-based position score:

```text
seat_to_act / (number_of_players - 1)
```

This is not a true button / cutoff / blind position calculation.

A true-position candidate was built to infer blinds and dealer more carefully. It was logically cleaner, but did not consistently beat v4.2.

Important engine detail:

- seats are rebuilt from alive players at the start of each hand
- dealer rotates by hand
- the score stays in the `0..1` range
- the heuristic is imperfect, but not catastrophic

Final decision:

Keep the v4.2 position heuristic.

---

## 9. Mixed-Pool Evaluation

We expanded testing beyond the original reference bots.

The evaluation pool eventually included:

- reference bots
- strong value bots
- pressure bots
- tight bots
- calling-station style bots
- nit bots
- trapper bots
- small-ball bots
- draw chasers
- randomized regulars
- MC-style sparring bots

The goal was to avoid building a bot that only beats the visible reference opponents.

The final all-profile mixed-pool stress test supported keeping v4.2:

- positive cumulative result across tested seeds
- no local timeouts or errors
- strong rank performance in a larger mixed field

The exact numbers are less important than the lesson:

> v4.2 remained stable when the opponent pool became more diverse.

---

## 10. Final Decision

The final decision was to submit:

```text
MyBot_v4_2
MONTE_CARLO_SIMS = 250
```

Rejected or not adopted:

- fixed higher-MC candidates
- adaptive MC
- true-position candidate
- broad wet-board guards
- broad river guards
- v4.3 margin rewrite
- larger turn/river value sizing
- overly defensive anti-bust logic

Main lesson:

> The final strategy should not be the one that explains the last bad hand best. It should be the one that survives the widest set of tests.
