# MyBot v4.2 — Preflop Strategy Notes

Source code:
- `bots/mybot/bot.py`
- Range definitions: lines 10-37
- Preflop decision function: `_decide_preflop()` around lines 656-755

## Core Idea

Preflop is not equity simulation based. It is a rule-based range system.

The goal is:

1. Play strong hands confidently.
2. Avoid dominated medium hands in multiway pots.
3. Use position to widen or tighten playable hands.
4. Avoid committing too much stack preflop unless holding premium hands.
5. Preserve stack in multiway / aggressive environments.

Unlike postflop, preflop does not run Monte Carlo. It converts the two hole cards into a compact hand code like `AKs`, `AQo`, `TT`, then checks that hand against curated ranges.

## Hand Code System

Examples:

- `AA`, `KK`, `TT`: pocket pairs.
- `AKs`: Ace-King suited.
- `AKo`: Ace-King offsuit.
- `QJs`: Queen-Jack suited.

The helper functions normalize card order so `Kh As` and `As Kh` both become `AKo`.

## Range Groups

### Premium Pairs

```python
PREMIUM_PAIRS = {"AA", "KK", "QQ", "JJ", "TT"}
```

These are the strongest pair hands. They are treated as strong value hands.

### Strong Broadway

```python
STRONG_BROADWAY = {"AKs", "AKo", "AQs", "AQo", "AJs", "KQs"}
```

These are high-card hands that can make top pair with strong kicker, strong straights, and strong suited combinations.

### Medium Hands

Examples:

```python
{"ATs", "ATo", "AJo", "KJs", "KJo", "KQo", "QJs", "QJo", "JTs", "99", "88", "77", "66"}
```

These are playable, but sensitive to position and pressure. They can be profitable, but are more easily dominated.

### Speculative Hands

Examples:

```python
{"A9s", "A8s", "KTs", "QTs", "T9s", "98s", "87s", "76s"}
```

These hands are not always strong immediately, but can make disguised straights, flushes, or strong draws. They are better when calls are cheap and/or position is late.

### Late Position Extras

Examples:

```python
{"A7s", "A6s", "A5s", "A4s", "A3s", "A2s", "KTo", "QTo", "65s", "54s"}
```

These are only added in late position. The logic is: when fewer players act after us, we can profitably enter slightly wider.

## Position Logic

Position is bucketed into:

- early
- middle
- late

Early position is tighter. Late position is wider.

### Early Position

Playable medium hands:

```python
AJo, ATs, KJs, QJs, JTs, 99, 88, 77
```

No speculative hands are allowed in early position.

Call thresholds:

- call if owed <= max(100, 12% pot)
- and owed < 14% stack

### Middle Position

Adds hands like:

```python
ATo, KQo, KJo, QJo, 66, T9s, 98s
```

Speculative hands are allowed.

Call thresholds:

- call if owed <= max(100, 18% pot)
- and owed < 20% stack

### Late Position

Late position is widest.

Adds suited Ax, KTo, QTo, suited connectors like `65s`, `54s`.

Call thresholds:

- call if owed <= max(100, 22% pot)
- and owed < 22% stack

## Strong Hand Logic

If the hand is in `PREMIUM_PAIRS` or `STRONG_BROADWAY`, we enter the strong-hand branch.

The bot first checks whether the cost is too high.

### Facing All-In

If `amount_owed >= stack`:

- call/all-in only with `AA` or `KK`
- fold everything else

This is intentionally conservative. Even hands like `QQ`, `AKs`, or `AQs` are not automatically stacked off when facing all-in.

### Multiway / Protected Stack Fold Rules

The bot folds some strong-but-not-premium hands when:

- table is multi-player
- stack is mid/short
- call cost is large
- hand is not in protected big-call range

This prevents losing tournament life with hands like `AQo`, `AJs`, or `TT` in bad multiway pressure spots.

### Large Pressure Thresholds

The bot has several stack-ratio gates:

- if owed > 16% stack, require at least `JJ`, `AKo`, `AQs`, or better.
- if owed > 24% stack, require at least `QQ`, `AKs`, or better.
- if owed > 25% stack, require `TT+`, `AK`, `AQ` tier.
- if multi-player and owed > 45% stack, only continue with `AA` or `KK`.

The idea is not “strong hand always continue.” The hand must be strong relative to the amount of stack at risk.

## Preflop Raising

When holding a premium/value reraising hand, the bot may raise.

Key constants:

```python
PREFLOP_STRONG_RAISE_MULTIPLIER = 2
MAX_PREFLOP_RAISE_STACK_RATIO = 0.32
AGGRESSIVE_PREFLOP_RAISE_CAP = 0.22
MULTIWAY_PREFLOP_RAISE_CAP = 0.20
PROTECTED_PREFLOP_RAISE_CAP = 0.16
```

The default raise target is:

```python
min_raise_to * 2
```

But the raise is capped by stack risk:

- normal table: max 32% stack
- aggressive table: max 22% stack
- multiway: max 20% stack
- protected stack situation: max 16% stack

If the raise would be too large and the hand is not `AA` or `KK`, the bot falls back to check/call instead of forcing a risky raise.

## Medium / Speculative Logic

If the hand is not premium/strong, the bot moves into position-based playable ranges.

For playable hands:

1. Check if the hand is playable from this position.
2. Tighten in multiway spots.
3. Tighten if table is aggressive.
4. Call only if both pot ratio and stack ratio are cheap enough.

## Multiway Dominated Offsuit Filter

```python
MULTIWAY_DOMINATED_OFFSUIT_HANDS = {"ATo", "KJo", "QJo", "KTo", "QTo"}
```

These hands look decent, but are dangerous multiway because they are often dominated.

Example:

- We hold `KJo`.
- Opponent holds `AK`, `KQ`, `AJ`, or stronger Broadway.
- If we hit top pair, we may still lose a large pot due to worse kicker.

So in multiway pots, these hands are removed from playable medium/speculative ranges.

## Aggressive Table Adjustment

If the table is classified as aggressive, the bot tightens preflop calls:

- pot ratio threshold decreases by 0.04
- stack ratio threshold decreases by 0.04

This means the bot enters fewer marginal pots when opponents are likely to raise often.

## Trash Hand Logic

If the hand is outside playable ranges:

- check if free
- call only if extremely cheap
- otherwise fold

Cheap trash call rule:

```python
amount_owed <= max(50, 8% pot)
and amount_owed < 8% stack
```

This keeps the bot from overfolding tiny blind-defense spots, while still avoiding expensive weak hands.

## Summary

Preflop v4.2 is a conservative range-and-risk engine.

It does not try to solve poker theoretically. Instead, it uses practical rules:

- premium hands can raise and defend against pressure
- medium hands depend heavily on position
- speculative hands need position and cheap price
- dominated offsuit hands are removed multiway
- stack-risk thresholds prevent overcommitting
- aggressive tables and multiway pots tighten the bot

This preflop design supports the broader v4.2 strategy: survive enough to reach profitable postflop value spots, while avoiding early high-variance mistakes with dominated hands.
