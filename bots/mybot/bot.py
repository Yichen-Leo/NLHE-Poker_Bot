BOT_NAME = "MyBot_v4_2"
BOT_AVATAR = "robot_1"

import eval7
import random


RANK_ORDER = "23456789TJQKA"

# ----------------------------- Preflop ranges -----------------------------
PREMIUM_PAIRS = {"AA", "KK", "QQ", "JJ", "TT"}
STRONG_BROADWAY = {"AKs", "AKo", "AQs", "AQo", "AJs", "KQs"}
MEDIUM_HANDS = {"ATs", "ATo", "AJo", "KJs", "KJo", "KQo", "QJs", "QJo", "JTs", "99", "88", "77", "66"}
SPECULATIVE_HANDS = {"A9s", "A8s", "KTs", "QTs", "T9s", "98s", "87s", "76s"}
LATE_POSITION_EXTRA_HANDS = {"A7s", "A6s", "A5s", "A4s", "A3s", "A2s", "KTo", "QTo", "65s", "54s"}

EARLY_POSITION_CALL_HANDS = {"AJo", "ATs", "KJs", "QJs", "JTs", "99", "88", "77"}
MIDDLE_POSITION_CALL_HANDS = EARLY_POSITION_CALL_HANDS | {"ATo", "KQo", "KJo", "QJo", "66", "T9s", "98s"}
LATE_POSITION_CALL_HANDS = MIDDLE_POSITION_CALL_HANDS | {
    "A9s",
    "A8s",
    "A7s",
    "A6s",
    "A5s",
    "A4s",
    "A3s",
    "A2s",
    "KTs",
    "KTo",
    "QTs",
    "QTo",
    "87s",
    "76s",
    "65s",
    "54s",
}
MULTIWAY_DOMINATED_OFFSUIT_HANDS = {"ATo", "KJo", "QJo", "KTo", "QTo"}

# ----------------------------- V3 parameters ------------------------------
MONTE_CARLO_SIMS = 250

CALL_MARGIN = 0.05
RISKY_CALL_MARGIN = 0.12
VALUE_RAISE_EQUITY = 0.66
STRONG_RAISE_EQUITY = 0.78
RERAISE_EQUITY = 0.84
BIG_RISK_RERAISE_EQUITY = 0.92

MAX_NORMAL_CALL_STACK_RATIO = 0.25
MAX_RISKY_CALL_STACK_RATIO = 0.45
MAX_VALUE_RAISE_STACK_RATIO = 0.35
MAX_RERAISE_STACK_RATIO = 0.25
ALL_IN_CALL_EQUITY = 0.88
MULTIWAY_ALL_IN_CALL_EQUITY = 0.94
OPPONENT_PRESSURE_PER_PLAYER = 0.03
MAX_OPPONENT_PRESSURE = 0.09
MULTIWAY_BIG_CALL_EXTRA_MARGIN = 0.06
TABLE_STYLE_LOOKBACK = 80
OPPONENT_PROFILE_LOOKBACK = 120
MIN_OPPONENT_PROFILE_ACTIONS = 8
AGGRESSIVE_RAISE_FREQUENCY = 0.38
PASSIVE_RAISE_FREQUENCY = 0.18
CALLING_STATION_CALL_FREQUENCY = 0.45
TIGHT_FOLD_FREQUENCY = 0.52
AGGRESSIVE_CALL_MARGIN = 0.05
PASSIVE_CALL_MARGIN = -0.02
AGGRESSIVE_RAISE_MARGIN = 0.04
PASSIVE_RAISE_MARGIN = -0.03
PLAYER_STYLE_FLOP_MARGINS = {
    "aggressive": 0.00,
    "normal": 0.00,
    "unknown": 0.00,
    "calling_station": 0.01,
    "passive": 0.01,
    "tight": 0.02,
}
PLAYER_STYLE_TURN_MARGINS = {
    "aggressive": 0.00,
    "normal": 0.00,
    "unknown": 0.00,
    "calling_station": 0.04,
    "passive": 0.04,
    "tight": 0.05,
}
PLAYER_STYLE_RIVER_MARGINS = {
    "aggressive": 0.00,
    "normal": 0.00,
    "unknown": 0.00,
    "calling_station": 0.07,
    "passive": 0.07,
    "tight": 0.09,
}

VALUE_BET_POT_RATIO = 0.55
STRONG_BET_POT_RATIO = 0.70
PREFLOP_STRONG_RAISE_MULTIPLIER = 2
MAX_PREFLOP_RAISE_STACK_RATIO = 0.32
AGGRESSIVE_PREFLOP_RAISE_CAP = 0.22
SHORT_STACK_THRESHOLD = 0.75
SHORT_STACK_CALL_MARGIN = 0.05
SHORT_STACK_RAISE_MARGIN = 0.08
SHORT_STACK_MAX_RAISE_RATIO = 0.18
BIG_STACK_THRESHOLD = 1.50
BIG_STACK_CALL_MARGIN = 0.04
BIG_STACK_RAISE_MARGIN = 0.08
BIG_STACK_MAX_RAISE_RATIO = 0.20
MULTIWAY_VALUE_RAISE_EQUITY = 0.80
MULTIWAY_BIG_STACK_VALUE_RAISE_EQUITY = 0.86
MULTIWAY_PRESSURE_CALL_MARGIN = 0.06
MULTIWAY_BIG_PRESSURE_STACK_RATIO = 0.15
MULTIWAY_PREFLOP_RAISE_CAP = 0.20
PROTECTED_PREFLOP_RAISE_CAP = 0.16
VULNERABLE_BOARD_RAISE_MARGIN = 0.12
VULNERABLE_BOARD_CALL_MARGIN = 0.06
VULNERABLE_BOARD_MAX_RAISE_RATIO = 0.10
VULNERABLE_BIG_RAISE_EQUITY = 0.96
MID_STACK_THRESHOLD = 0.90
MID_STACK_BIG_PREFLOP_CALL_RATIO = 0.18
HAND_PRESSURE_RAISE_COUNT = 2
HAND_PRESSURE_CALL_MARGIN = 0.06
HAND_PRESSURE_BIG_CALL_MARGIN = 0.10

PREFLOP_ALL_IN_HANDS = {"AA", "KK"}
PREFLOP_BIG_CALL_HANDS = {"AA", "KK", "QQ", "JJ", "TT", "AKs", "AKo", "AQs", "AQo"}
PREFLOP_PROTECTED_BIG_CALL_HANDS = {"AA", "KK", "QQ", "JJ", "AKs", "AKo"}
PREFLOP_HUGE_PRESSURE_HANDS = {"AA", "KK"}
PREFLOP_VALUE_RERAISE_HANDS = {"AA", "KK"}
PREFLOP_RERAISE_DEFENSE_HANDS = {"AA", "KK", "QQ", "AKs"}
PREFLOP_MEDIUM_RERAISE_DEFENSE_HANDS = PREFLOP_RERAISE_DEFENSE_HANDS | {"JJ", "AKo", "AQs"}
VULNERABLE_HAND_TYPES = {"High Card", "Pair", "Two Pair"}


def _rank(card: str) -> str:
    return card[0]


def _hand_code(two_cards: list[str]) -> str:
    first = _rank(two_cards[0])
    second = _rank(two_cards[1])

    if first == second:
        return first + second

    first_index = RANK_ORDER.index(first)
    second_index = RANK_ORDER.index(second)
    high = first if first_index > second_index else second
    low = second if first_index > second_index else first
    return high + low


def _is_suited(two_cards: list[str]) -> bool:
    return len(two_cards) == 2 and two_cards[0][1] == two_cards[1][1]


def _preflop_code(two_cards: list[str]) -> str:
    base_code = _hand_code(two_cards)
    if len(base_code) == 2 and base_code[0] == base_code[1]:
        return base_code
    suffix = "s" if _is_suited(two_cards) else "o"
    return base_code + suffix


def _active_opponent_count(state: dict) -> int:
    players = state.get("players", [])
    seat_to_act = state.get("seat_to_act")
    count = 0
    for player in players:
        if player.get("seat") == seat_to_act:
            continue
        if player.get("state") in ("active", "all_in"):
            count += 1
    return max(1, count)


def _active_player_count(state: dict) -> int:
    return sum(
        1
        for player in state.get("players", [])
        if player.get("state") in ("active", "all_in")
    )


def _position_score(state: dict) -> float:
    players = state.get("players", [])
    seat = state.get("seat_to_act", 0)
    return seat / max(len(players) - 1, 1)


def _position_bucket(state: dict) -> str:
    score = _position_score(state)
    if score < 0.35:
        return "early"
    if score > 0.65:
        return "late"
    return "middle"


def _opponent_pressure(opponents: int) -> float:
    return min(MAX_OPPONENT_PRESSURE, max(0, opponents - 1) * OPPONENT_PRESSURE_PER_PLAYER)


def _table_style(state: dict) -> str:
    logs = state.get("match_action_log", [])[-TABLE_STYLE_LOOKBACK:]
    actions = []
    for item in logs:
        action = item.get("action")
        if action in ("raise", "call", "fold"):
            actions.append(action)

    if len(actions) < 12:
        return "normal"

    raise_frequency = actions.count("raise") / len(actions)
    if raise_frequency >= AGGRESSIVE_RAISE_FREQUENCY:
        return "aggressive"
    if raise_frequency <= PASSIVE_RAISE_FREQUENCY:
        return "passive"
    return "normal"


def _table_call_margin(state: dict) -> float:
    style = _table_style(state)
    if style == "aggressive":
        return AGGRESSIVE_CALL_MARGIN
    if style == "passive":
        return PASSIVE_CALL_MARGIN
    return 0.0


def _table_raise_margin(state: dict) -> float:
    style = _table_style(state)
    if style == "aggressive":
        return AGGRESSIVE_RAISE_MARGIN
    if style == "passive":
        return PASSIVE_RAISE_MARGIN
    return 0.0


def _table_is_aggressive(state: dict) -> bool:
    return _table_style(state) == "aggressive"


def _seat_to_bot_id(state: dict) -> dict:
    return {player.get("seat"): player.get("bot_id") for player in state.get("players", [])}


def _style_action(action: str) -> str:
    if action == "all_in":
        return "raise"
    if action in ("raise", "call", "fold"):
        return action
    return ""


def _style_from_actions(actions: list[str]) -> str:
    normalized = [_style_action(action) for action in actions]
    normalized = [action for action in normalized if action]
    if len(normalized) < MIN_OPPONENT_PROFILE_ACTIONS:
        return "unknown"

    raise_frequency = normalized.count("raise") / len(normalized)
    call_frequency = normalized.count("call") / len(normalized)
    fold_frequency = normalized.count("fold") / len(normalized)

    if raise_frequency >= AGGRESSIVE_RAISE_FREQUENCY:
        return "aggressive"
    if call_frequency >= CALLING_STATION_CALL_FREQUENCY and raise_frequency <= PASSIVE_RAISE_FREQUENCY:
        return "calling_station"
    if fold_frequency >= TIGHT_FOLD_FREQUENCY and call_frequency <= 0.30:
        return "tight"
    if raise_frequency <= PASSIVE_RAISE_FREQUENCY:
        return "passive"
    return "normal"


def _opponent_profile(state: dict, bot_id: str) -> str:
    if not bot_id:
        return "unknown"

    actions = [
        item.get("action")
        for item in state.get("match_action_log", [])[-OPPONENT_PROFILE_LOOKBACK:]
        if item.get("bot_id") == bot_id
    ]
    return _style_from_actions(actions)


def _last_raise_player_id(state: dict) -> str:
    seat = state.get("seat_to_act")
    seat_to_bot_id = _seat_to_bot_id(state)
    for action in reversed(state.get("action_log", [])):
        if action.get("seat") == seat:
            continue
        if action.get("action") in ("raise", "all_in"):
            return seat_to_bot_id.get(action.get("seat"), "")
    return ""


def _last_raise_player_style(state: dict) -> str:
    return _opponent_profile(state, _last_raise_player_id(state))


def _hand_raise_pressure(state: dict) -> int:
    seat = state.get("seat_to_act")
    pressure = 0
    for action in state.get("action_log", []):
        if action.get("seat") == seat:
            continue
        if action.get("action") == "raise":
            pressure += 1
    return pressure


def _hand_pressure_call_margin(state: dict) -> float:
    if _active_opponent_count(state) != 1:
        return 0.0

    pressure = _hand_raise_pressure(state)
    if pressure < HAND_PRESSURE_RAISE_COUNT:
        return 0.0
    if state.get("amount_owed", 0) > state.get("your_stack", 0) * MAX_NORMAL_CALL_STACK_RATIO:
        return HAND_PRESSURE_BIG_CALL_MARGIN
    return HAND_PRESSURE_CALL_MARGIN


def _stack_ratio(state: dict) -> float:
    return state.get("your_stack", 0) / 10000


def _is_multiway(state: dict) -> bool:
    return _active_opponent_count(state) >= 2


def _is_multi_player_table(state: dict) -> bool:
    return _active_player_count(state) >= 3


def _is_short_stack(state: dict) -> bool:
    return _stack_ratio(state) < SHORT_STACK_THRESHOLD and _is_multiway(state)


def _is_mid_or_short_stack(state: dict) -> bool:
    return _stack_ratio(state) < MID_STACK_THRESHOLD


def _is_big_stack(state: dict) -> bool:
    return _stack_ratio(state) >= BIG_STACK_THRESHOLD


def _is_protected_stack(state: dict) -> bool:
    return _is_multiway(state) and (_is_short_stack(state) or _is_big_stack(state))


def _multiway_hand_pressure_call_margin(state: dict) -> float:
    if not _is_multiway(state):
        return 0.0

    pressure = _hand_raise_pressure(state)
    if pressure < HAND_PRESSURE_RAISE_COUNT:
        return 0.0

    stack = state.get("your_stack", 0)
    amount_owed = state.get("amount_owed", 0)
    is_large_decision = stack > 0 and amount_owed > stack * MULTIWAY_BIG_PRESSURE_STACK_RATIO
    if is_large_decision or _is_protected_stack(state):
        return MULTIWAY_PRESSURE_CALL_MARGIN
    return 0.0


def _player_style_call_margin(state: dict) -> float:
    if state.get("street") == "preflop":
        return 0.0
    if state.get("amount_owed", 0) <= 0:
        return 0.0
    if _active_player_count(state) > 3:
        return 0.0

    style = _last_raise_player_style(state)
    street = state.get("street")
    if street == "flop":
        table = PLAYER_STYLE_FLOP_MARGINS
    elif street == "turn":
        table = PLAYER_STYLE_TURN_MARGINS
    elif street == "river":
        table = PLAYER_STYLE_RIVER_MARGINS
    else:
        return 0.0

    margin = table.get(style, 0.0)
    if margin <= 0:
        return margin

    pressure = _hand_raise_pressure(state)
    if pressure >= HAND_PRESSURE_RAISE_COUNT and street in ("turn", "river"):
        margin += 0.02
    return margin


def _stack_preservation_call_margin(state: dict) -> float:
    if not _is_multiway(state):
        return 0.0
    if _is_short_stack(state):
        return SHORT_STACK_CALL_MARGIN
    if _is_big_stack(state):
        return BIG_STACK_CALL_MARGIN
    return 0.0


def _stack_preservation_raise_margin(state: dict) -> float:
    if not _is_multiway(state):
        return 0.0
    if _is_short_stack(state):
        return SHORT_STACK_RAISE_MARGIN
    if _is_big_stack(state):
        return BIG_STACK_RAISE_MARGIN
    return 0.0


def _board_is_paired(state: dict) -> bool:
    counts = {}
    for card in state.get("community_cards", []):
        rank = _rank(card)
        counts[rank] = counts.get(rank, 0) + 1
    return any(count >= 2 for count in counts.values())


def _board_is_flushy(state: dict) -> bool:
    counts = {}
    for card in state.get("community_cards", []):
        suit = card[1]
        counts[suit] = counts.get(suit, 0) + 1
    return any(count >= 3 for count in counts.values())


def _board_is_straighty(state: dict) -> bool:
    rank_values = sorted({RANK_ORDER.index(_rank(card)) for card in state.get("community_cards", [])})
    if len(rank_values) < 3:
        return False

    if RANK_ORDER.index("A") in rank_values:
        rank_values = sorted(set(rank_values + [-1]))

    for start in range(len(rank_values)):
        window = [value for value in rank_values if rank_values[start] <= value <= rank_values[start] + 4]
        if len(window) >= 3:
            return True
    return False


def _board_is_wet(state: dict) -> bool:
    return _board_is_paired(state) or _board_is_flushy(state) or _board_is_straighty(state)


def _hand_type(state: dict) -> str:
    cards = state.get("your_cards", []) + state.get("community_cards", [])
    if len(cards) < 5:
        return ""
    score = eval7.evaluate([eval7.Card(card) for card in cards])
    return str(eval7.handtype(score))


def _has_vulnerable_made_hand(state: dict) -> bool:
    return _hand_type(state) in VULNERABLE_HAND_TYPES


def _is_vulnerable_board_raise(state: dict) -> bool:
    return _is_multi_player_table(state) and _board_is_wet(state) and _has_vulnerable_made_hand(state)


def _pot_odds(amount_owed: int, pot: int) -> float:
    if amount_owed <= 0:
        return 0.0
    return amount_owed / max(1, pot + amount_owed)


def _risk_margin(amount_owed: int, your_stack: int) -> float:
    if your_stack <= 0:
        return RISKY_CALL_MARGIN

    stack_ratio = amount_owed / your_stack
    if stack_ratio > MAX_RISKY_CALL_STACK_RATIO:
        return RISKY_CALL_MARGIN + 0.10
    if stack_ratio > MAX_NORMAL_CALL_STACK_RATIO:
        return RISKY_CALL_MARGIN
    return CALL_MARGIN


def _legal_bet_total(target_total: int, state: dict) -> int:
    min_raise_to = state.get("min_raise_to", 0)
    stack = state.get("your_stack", 0)
    current_invested = state.get("your_bet_this_street", 0)
    max_total = current_invested + stack

    if min_raise_to <= 0:
        return 0

    if max_total < min_raise_to:
        return 0

    return min(max(target_total, min_raise_to), max_total)


def _raise_by_strength(equity: float, state: dict):
    pot = state.get("pot", 0)
    min_raise_to = state.get("min_raise_to", 0)
    current_invested = state.get("your_bet_this_street", 0)
    stack = state.get("your_stack", 0)
    amount_owed = state.get("amount_owed", 0)
    opponents = _active_opponent_count(state)
    pressure = _opponent_pressure(opponents)
    style_margin = _table_raise_margin(state)
    stack_margin = _stack_preservation_raise_margin(state)
    vulnerable_raise_margin = VULNERABLE_BOARD_RAISE_MARGIN if _is_vulnerable_board_raise(state) else 0.0

    if min_raise_to <= 0 or stack <= 0:
        return None

    if amount_owed > 0:
        required_equity = RERAISE_EQUITY + pressure + style_margin + stack_margin + vulnerable_raise_margin
        if amount_owed > stack * MAX_NORMAL_CALL_STACK_RATIO:
            required_equity = (
                BIG_RISK_RERAISE_EQUITY
                + pressure
                + style_margin
                + stack_margin
                + vulnerable_raise_margin
            )
        if equity < required_equity:
            return None

    value_raise_equity = VALUE_RAISE_EQUITY
    if opponents >= 2:
        value_raise_equity = MULTIWAY_VALUE_RAISE_EQUITY
    if _is_big_stack(state) and opponents >= 2:
        value_raise_equity = MULTIWAY_BIG_STACK_VALUE_RAISE_EQUITY

    if equity >= STRONG_RAISE_EQUITY + pressure + style_margin + stack_margin + vulnerable_raise_margin:
        target_total = current_invested + int(pot * STRONG_BET_POT_RATIO)
    elif equity >= value_raise_equity + pressure + style_margin + stack_margin + vulnerable_raise_margin:
        target_total = current_invested + int(pot * VALUE_BET_POT_RATIO)
    else:
        return None

    amount = _legal_bet_total(target_total, state)
    chips_to_add = amount - current_invested
    max_raise_ratio = MAX_RERAISE_STACK_RATIO if amount_owed > 0 else MAX_VALUE_RAISE_STACK_RATIO
    if _is_short_stack(state):
        max_raise_ratio = min(max_raise_ratio, SHORT_STACK_MAX_RAISE_RATIO)
    if _is_big_stack(state) and opponents >= 2:
        max_raise_ratio = min(max_raise_ratio, BIG_STACK_MAX_RAISE_RATIO)
    if _is_vulnerable_board_raise(state):
        max_raise_ratio = min(max_raise_ratio, VULNERABLE_BOARD_MAX_RAISE_RATIO)
    if chips_to_add > stack * max_raise_ratio and equity < BIG_RISK_RERAISE_EQUITY:
        return None
    if _is_vulnerable_board_raise(state) and chips_to_add > stack * max_raise_ratio and equity < VULNERABLE_BIG_RAISE_EQUITY:
        return None

    if amount >= min_raise_to:
        return {"action": "raise", "amount": amount}
    return None


def _stable_seed(values: list) -> int:
    text = "|".join(str(value) for value in values)
    seed = 2166136261
    for char in text:
        seed ^= ord(char)
        seed = (seed * 16777619) % (2**32)
    return seed


def _estimate_equity(your_cards: list[str], community_cards: list[str], opponents: int, state: dict) -> float:
    known_cards = [eval7.Card(card) for card in your_cards + community_cards]
    hero_cards = [eval7.Card(card) for card in your_cards]
    board_cards = [eval7.Card(card) for card in community_cards]
    rng = random.Random(
        _stable_seed(
            [
                sorted(your_cards),
                sorted(community_cards),
                opponents,
                state.get("street"),
                state.get("pot"),
                state.get("amount_owed"),
                state.get("your_stack"),
                state.get("your_bet_this_street"),
            ]
        )
    )

    wins = 0.0
    needed_board_cards = 5 - len(board_cards)

    for _ in range(MONTE_CARLO_SIMS):
        deck = eval7.Deck()
        for card in known_cards:
            deck.cards.remove(card)
        rng.shuffle(deck.cards)

        trial_board = list(board_cards)
        trial_board += deck.deal(needed_board_cards)
        hero_value = eval7.evaluate(hero_cards + trial_board)

        hero_won = True
        tied = 1
        for _ in range(opponents):
            opponent_cards = deck.deal(2)
            opponent_value = eval7.evaluate(opponent_cards + trial_board)
            if opponent_value > hero_value:
                hero_won = False
                break
            if opponent_value == hero_value:
                tied += 1

        if hero_won:
            wins += 1.0 / tied

    return wins / MONTE_CARLO_SIMS


def _call_or_fold_by_equity(equity: float, state: dict, opponents: int) -> dict:
    amount_owed = state.get("amount_owed", 0)
    pot = state.get("pot", 0)
    stack = state.get("your_stack", 0)

    if amount_owed <= 0 or state.get("can_check", False):
        return {"action": "check"}

    required_equity = (
        _pot_odds(amount_owed, pot)
        + _risk_margin(amount_owed, stack)
        + _opponent_pressure(opponents)
        + _hand_pressure_call_margin(state)
        + _multiway_hand_pressure_call_margin(state)
        + _player_style_call_margin(state)
        + _stack_preservation_call_margin(state)
    )
    if _is_vulnerable_board_raise(state) and amount_owed > stack * MAX_NORMAL_CALL_STACK_RATIO:
        required_equity += VULNERABLE_BOARD_CALL_MARGIN

    if opponents >= 2 and amount_owed > stack * MAX_NORMAL_CALL_STACK_RATIO:
        required_equity += MULTIWAY_BIG_CALL_EXTRA_MARGIN

    if amount_owed >= stack:
        all_in_equity = MULTIWAY_ALL_IN_CALL_EQUITY if opponents >= 2 else ALL_IN_CALL_EQUITY
        required_equity = max(required_equity, all_in_equity)

    if equity >= required_equity:
        if amount_owed >= stack:
            return {"action": "all_in"}
        return {"action": "call"}

    return {"action": "fold"}


def _decide_preflop(state: dict) -> dict:
    your_cards = state.get("your_cards", [])
    hand = _preflop_code(your_cards)
    amount_owed = state.get("amount_owed", 0)
    pot = state.get("pot", 0)
    stack = state.get("your_stack", 0)
    min_raise_to = state.get("min_raise_to", 0)
    position = _position_bucket(state)
    opponents = _active_opponent_count(state)
    if hand in PREMIUM_PAIRS or hand in STRONG_BROADWAY:
        if amount_owed >= stack:
            if hand in PREFLOP_ALL_IN_HANDS:
                return {"action": "all_in"}
            return {"action": "fold"}

        if (
            _is_multi_player_table(state)
            and _is_mid_or_short_stack(state)
            and amount_owed > stack * MID_STACK_BIG_PREFLOP_CALL_RATIO
            and hand not in PREFLOP_PROTECTED_BIG_CALL_HANDS
        ):
            return {"action": "fold"}

        if amount_owed > stack * 0.16 and hand not in PREFLOP_MEDIUM_RERAISE_DEFENSE_HANDS:
            return {"action": "fold"}

        if amount_owed > stack * 0.24 and hand not in PREFLOP_RERAISE_DEFENSE_HANDS:
            return {"action": "fold"}

        if amount_owed > stack * MAX_NORMAL_CALL_STACK_RATIO and hand not in PREFLOP_BIG_CALL_HANDS:
            return {"action": "fold"}

        if (
            _is_multi_player_table(state)
            and amount_owed > stack * MAX_RISKY_CALL_STACK_RATIO
            and hand not in PREFLOP_HUGE_PRESSURE_HANDS
        ):
            return {"action": "fold"}

        if amount_owed > 0 and hand not in PREFLOP_VALUE_RERAISE_HANDS:
            return {"action": "call"}

        if min_raise_to > 0 and stack > amount_owed:
            target = min_raise_to * PREFLOP_STRONG_RAISE_MULTIPLIER
            amount = _legal_bet_total(target, state)
            added_chips = amount - state.get("your_bet_this_street", 0)
            cap_ratio = AGGRESSIVE_PREFLOP_RAISE_CAP if _table_is_aggressive(state) else MAX_PREFLOP_RAISE_STACK_RATIO
            if opponents >= 2:
                cap_ratio = min(cap_ratio, MULTIWAY_PREFLOP_RAISE_CAP)
            if _is_protected_stack(state):
                cap_ratio = min(cap_ratio, PROTECTED_PREFLOP_RAISE_CAP)
            if added_chips > stack * cap_ratio and hand not in PREFLOP_ALL_IN_HANDS:
                if state.get("can_check", False):
                    return {"action": "check"}
                return {"action": "call"}
            if amount >= min_raise_to:
                return {"action": "raise", "amount": amount}
        if state.get("can_check", False):
            return {"action": "check"}
        return {"action": "call"}

    if position == "early":
        playable_medium = hand in EARLY_POSITION_CALL_HANDS
        playable_speculative = False
        call_pot_ratio = 0.12
        call_stack_ratio = 0.14
    elif position == "late":
        playable_medium = hand in LATE_POSITION_CALL_HANDS
        playable_speculative = hand in SPECULATIVE_HANDS or hand in LATE_POSITION_EXTRA_HANDS
        call_pot_ratio = 0.22
        call_stack_ratio = 0.22
    else:
        playable_medium = hand in MIDDLE_POSITION_CALL_HANDS
        playable_speculative = hand in SPECULATIVE_HANDS
        call_pot_ratio = 0.18
        call_stack_ratio = 0.20

    if playable_medium or playable_speculative:
        if opponents >= 2 and hand in MULTIWAY_DOMINATED_OFFSUIT_HANDS:
            playable_medium = False
            playable_speculative = False
        if opponents >= 2:
            call_pot_ratio = max(0.10, call_pot_ratio - 0.03)
            call_stack_ratio = max(0.12, call_stack_ratio - 0.04)
        if _table_is_aggressive(state):
            call_pot_ratio = max(0.10, call_pot_ratio - 0.04)
            call_stack_ratio = max(0.12, call_stack_ratio - 0.04)

    if playable_medium or playable_speculative:
        if state.get("can_check", False):
            return {"action": "check"}
        if amount_owed <= max(100, int(pot * call_pot_ratio)) and amount_owed < stack * call_stack_ratio:
            return {"action": "call"}
        return {"action": "fold"}

    if state.get("can_check", False):
        return {"action": "check"}
    if amount_owed <= max(50, int(pot * 0.08)) and amount_owed < stack * 0.08:
        return {"action": "call"}
    return {"action": "fold"}


def decide(game_state: dict) -> dict:
    if game_state.get("type") == "warmup":
        return {"action": "check"}

    your_cards = game_state.get("your_cards", [])
    community_cards = game_state.get("community_cards", [])
    street = game_state.get("street", "preflop")

    if len(your_cards) != 2:
        return {"action": "fold"}

    if street == "preflop":
        return _decide_preflop(game_state)

    opponents = _active_opponent_count(game_state)
    equity = _estimate_equity(your_cards, community_cards, opponents, game_state)

    value_raise = _raise_by_strength(equity, game_state)
    if value_raise is not None:
        return value_raise

    return _call_or_fold_by_equity(equity, game_state, opponents)
