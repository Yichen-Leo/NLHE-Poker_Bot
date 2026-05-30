# MyBot_v4_2 Implemented Strategy

This document explains the final strategy implemented in `MyBot_v4_2`.

Main bot file:

- `bots/mybot/bot.py`

Final configuration:

- `BOT_NAME = "MyBot_v4_2"`
- `MONTE_CARLO_SIMS = 250`

---

## 1. High-Level Structure

The bot uses two different decision systems:

```text
Preflop:
    rule-based hand ranges + position + stack-risk gates

Postflop:
    Monte Carlo expected pot share + pot odds + risk margins
```

The main decision flow is:

```text
If street == preflop:
    use preflop range strategy
Else:
    estimate equity with Monte Carlo
    consider value raise if equity is strong
    otherwise call or fold based on required equity
```

The bot is intentionally interpretable. Most decisions come from explicit hand groups, risk ratios, opponent count, table style, and estimated equity.

---

## 2. Preflop Strategy

Preflop is mostly rule-based. The bot converts the two hole cards into compact hand codes:

- `AA`
- `TT`
- `AKs`
- `AQo`
- `QJs`

Where:

- `s` means suited
- `o` means offsuit

### 2.1 Hand Groups

The main hand groups are:

- **Premium pairs**: `AA`, `KK`, `QQ`, `JJ`, `TT`
- **Strong broadways**: `AKs`, `AKo`, `AQs`, `AQo`, `AJs`, `KQs`
- **Medium hands**: hands like `ATs`, `KJs`, `QJs`, `JTs`, `99`, `88`, `77`, `66`
- **Speculative hands**: suited aces, suited broadways, and suited connectors
- **Late-position extras**: additional hands allowed when the preflop situation is cheaper or later

The purpose is not to play every technically playable hand. The bot tries to avoid dominated hands that can make second-best top pair and lose large pots.

### 2.2 Position Logic

The bot classifies preflop position into:

- `early`
- `middle`
- `late`

The current implementation uses a simple seat-based heuristic:

```text
position_score = seat_to_act / (number_of_players - 1)
```

Then:

- low score -> early
- middle score -> middle
- high score -> late

This is not a perfect poker button / cutoff / blind calculation. In this engine, however, seats are rebuilt from alive players each hand, and the dealer rotates by hand. In testing, this heuristic behaved acceptably and did not justify replacing the full strategy with a more complex true-position candidate.

### 2.3 Multiway Dominated-Offsuit Filter

In multiway pots, the bot removes some offsuit broadway hands:

```python
MULTIWAY_DOMINATED_OFFSUIT_HANDS = {"ATo", "KJo", "QJo", "KTo", "QTo"}
```

Reason:

These hands can look good when they hit top pair, but they are often dominated by stronger kickers in multiway pots.

Example:

- We hold `KJo`
- Opponent holds `AK` or `KQ`
- Board gives us top pair
- We may still lose a large pot

### 2.4 Preflop Stack-Risk Gates

The bot does not continue with strong-looking hands at any price.

It checks:

- `amount_owed / stack`
- whether the pot is multiway
- whether the table has been aggressive
- whether the hand is strong enough to defend against large pressure

The guiding idea:

> A hand can be good in absolute terms but still not good enough for the current price.

### 2.5 Preflop Raising

When raising preflop, the bot usually starts from a simple value raise target near:

```text
min_raise_to * PREFLOP_STRONG_RAISE_MULTIPLIER
```

The actual raise is capped by:

- stack exposure
- number of active opponents
- aggressive table conditions
- protected stack situations

So the bot can apply pressure with strong hands, but avoids turning too many preflop spots into uncontrolled stack-risk decisions.

---

## 3. Postflop Strategy

Postflop is the core of the bot.

After the flop, turn, and river, the bot estimates hand strength using Monte Carlo simulation with `eval7`.

### 3.1 Monte Carlo Equity

The bot samples many possible futures:

1. Keep our hole cards fixed.
2. Keep known community cards fixed.
3. Randomly complete unknown board cards.
4. Randomly assign opponent hole cards.
5. Evaluate final hands with `eval7`.
6. Estimate our expected share of the pot.

The result is:

```text
estimated_equity = simulated expected pot share
```

This is not exactly raw win probability.

The bot gives fractional credit for ties:

```text
win alone -> 1.0
tie       -> fractional credit
loss      -> 0.0
```

So the value is closer to an idealized expected fraction of the pot than a simple win/loss probability.

### 3.2 Pot Odds

Pot odds estimate the break-even equity required by the immediate call price:

```text
pot_odds = amount_owed / (pot + amount_owed)
```

If calling costs `200` and the final pot after calling would be `1000`, then:

```text
pot_odds = 0.20
```

The bot then adds risk margins on top of this baseline.

### 3.3 Required Equity

The central call/fold decision is:

```text
if estimated_equity >= required_equity:
    call
else:
    fold
```

The threshold is dynamic:

```text
required_equity =
    pot_odds
  + risk_margin
  + opponent_pressure_margin
  + hand_pressure_margin
  + multiway_pressure_margin
  + player_style_margin
  + stack_preservation_margin
  + vulnerable_board_margin
  + multiway_big_call_margin
```

Not every margin applies in every situation. Some are mainly heads-up, some are mainly multiway, and some are general risk controls.

---

## 4. Raise Logic

Before choosing call or fold, the bot checks whether a value raise is justified.

The raise system is equity-gated:

- raising with no bet requires strong equity
- reraising against pressure requires higher equity
- big-risk reraises require even more equity
- vulnerable board states can restrict risky value raises

The bot tries to build the pot when it has a strong enough edge, but avoids raising marginal hands simply because they are ahead of pot odds.

The high-level idea:

```text
strong equity + acceptable risk -> raise
medium equity + acceptable price -> call
insufficient equity or too much risk -> fold
```

---

## 5. Risk Controls

v4.2 uses multiple risk controls. They overlap somewhat, but each one addresses a different failure mode.

| Signal | Main Purpose |
|---|---|
| `risk_margin` | Penalize large calls relative to our stack |
| `opponent_pressure` | Require more equity against more active opponents |
| `hand_pressure_call_margin` | Tighten heads-up decisions after repeated pressure |
| `multiway_hand_pressure_call_margin` | Tighten repeated-pressure decisions in multiway pots |
| `player_style_call_margin` | Adjust later-street calls using recent opponent style |
| `stack_preservation_call_margin` | Protect short or large stacks in dangerous spots |
| `vulnerable_board_call_margin` | Avoid overpaying fragile made hands on wet boards |
| `multiway_big_call_extra_margin` | Add extra caution for large multiway calls |

### 5.1 Stack-Risk Margin

The larger the call is relative to our stack, the more equity the bot requires.

This prevents the bot from risking too much of its stack with hands that are only slightly ahead.

### 5.2 Opponent Count Pressure

More active opponents make equity harder to realize.

The bot therefore requires more equity in multiway pots than in heads-up pots.

### 5.3 Hand Pressure

The bot tracks repeated betting and raising pressure.

If the hand has seen multiple raises, especially heads-up or on later streets, the bot becomes more cautious.

### 5.4 Stack Preservation

The bot protects unusual stack states:

- short stacks should avoid unnecessary elimination risk
- large stacks should avoid donating a strong chip position in marginal spots

---

## 6. Opponent Style Profiling

The bot estimates simple player styles from recent action history.

Possible styles include:

- `aggressive`
- `passive`
- `calling_station`
- `tight`
- `normal`
- `unknown`

The estimate uses recent frequencies of:

- raise
- call
- fold

The style signal is mainly used for postflop call discipline. For example, a tight player applying later-street pressure is treated as a stronger warning sign than a loose/aggressive player applying the same pressure.

This signal is intentionally moderate. Overly harsh style penalties were tested and often reduced profitable bluff-catching and value lines.

---

## 7. Board Texture and Vulnerable Hands

The bot checks whether the board is dangerous, or "wet".

A board may be wet because it is:

- paired
- flushy
- straighty

The bot also detects vulnerable made hands:

- High Card
- Pair
- Two Pair

The main danger pattern is:

```text
wet board + vulnerable made hand + pressure + meaningful call size
```

v4.2 uses this cautiously rather than aggressively. Broader wet-board guards were tested, but they blocked too many profitable river value and bluff-catch situations.

---

## 8. Why the Final Strategy Is Not Over-Cleaned

v4.2 contains some historically evolved margins and heuristics.

Some later candidates made the logic cleaner, especially around call margins and board danger. However, those candidates often reduced the bot's ability to win large pots.

The final version keeps the strategy that performed best in testing, even if it is not the cleanest theoretical design.

The practical lesson:

> In this project, the strongest bot was not the prettiest formula. It was the policy that best preserved profitable paths while controlling obvious risks.
