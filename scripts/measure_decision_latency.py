#!/usr/bin/env python3
import argparse
import importlib.util
import random
import statistics
import time
from pathlib import Path


RANKS = "23456789TJQKA"
SUITS = "cdhs"


def _load_bot(path):
    spec = importlib.util.spec_from_file_location(f"latency_bot_{time.time_ns()}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _percentile(values, percent):
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    index = (len(ordered) - 1) * percent / 100
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _deck():
    return [rank + suit for rank in RANKS for suit in SUITS]


def _players(active_players, seat_to_act, rng):
    players = []
    for seat in range(active_players):
        players.append(
            {
                "seat": seat,
                "bot_id": f"p{seat}",
                "stack": rng.randint(2500, 25000),
                "state": "active",
                "is_active": True,
                "is_folded": False,
                "is_all_in": False,
                "bet_this_street": rng.choice([0, 50, 100, 200, 400]),
            }
        )
    players[seat_to_act]["bot_id"] = "mybot"
    return players


def _action_log(active_players, seat_to_act, rng, pressure):
    actions = []
    for _ in range(pressure):
        seat = rng.choice([seat for seat in range(active_players) if seat != seat_to_act])
        actions.append({"seat": seat, "action": "raise", "amount": rng.randint(100, 2500)})
        if rng.random() < 0.5:
            actions.append({"seat": seat_to_act, "action": "call", "amount": rng.randint(50, 1500)})
    return actions


def _match_action_log(rng, count):
    actions = []
    choices = ["raise", "call", "fold", "check"]
    weights = [0.24, 0.34, 0.24, 0.18]
    for _ in range(count):
        action = rng.choices(choices, weights=weights, k=1)[0]
        actions.append(
            {
                "bot_id": f"p{rng.randint(0, 5)}",
                "action": action,
                "amount": rng.randint(0, 4000),
            }
        )
    return actions


def _state(rng, street):
    cards = _deck()
    rng.shuffle(cards)
    your_cards = cards[:2]
    community_count = {"preflop": 0, "flop": 3, "turn": 4, "river": 5}[street]
    community_cards = cards[2 : 2 + community_count]
    active_players = rng.choice([2, 3, 4, 5, 6])
    seat_to_act = rng.randrange(active_players)
    stack = rng.randint(1000, 25000)
    pot = rng.randint(200, 30000)
    amount_owed = rng.choice(
        [
            0,
            rng.randint(10, 200),
            rng.randint(200, 1500),
            rng.randint(1500, min(max(stack, 1500), 12000)),
            stack,
        ]
    )
    pressure = rng.choice([0, 1, 2, 3, 4])
    min_raise_to = rng.randint(100, max(200, min(stack + 100, 8000)))
    can_check = amount_owed == 0
    return {
        "type": "decision",
        "street": street,
        "your_cards": your_cards,
        "community_cards": community_cards,
        "pot": pot,
        "amount_owed": amount_owed,
        "your_stack": stack,
        "your_bet_this_street": rng.choice([0, 50, 100, 250, 500]),
        "min_raise_to": min_raise_to,
        "can_check": can_check,
        "seat_to_act": seat_to_act,
        "players": _players(active_players, seat_to_act, rng),
        "action_log": _action_log(active_players, seat_to_act, rng, pressure),
        "match_action_log": _match_action_log(rng, 140),
    }


def main():
    parser = argparse.ArgumentParser(description="Measure bot decide() latency on synthetic states.")
    parser.add_argument("bot")
    parser.add_argument("--states", type=int, default=400)
    parser.add_argument("--seed", type=int, default=7000)
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--warn", type=float, default=1.5)
    args = parser.parse_args()

    bot_path = Path(args.bot)
    bot = _load_bot(bot_path)
    rng = random.Random(args.seed)
    timings = []
    slow = []
    errors = 0
    street_counts = {"preflop": 0, "flop": 0, "turn": 0, "river": 0}
    street_timings = {street: [] for street in street_counts}

    for index in range(args.states):
        street = rng.choice(["preflop", "flop", "turn", "river"])
        state = _state(rng, street)
        start = time.perf_counter()
        try:
            bot.decide(state)
        except Exception:
            errors += 1
        elapsed = time.perf_counter() - start
        timings.append(elapsed)
        street_counts[street] += 1
        street_timings[street].append(elapsed)
        if elapsed >= args.warn:
            slow.append((index, street, elapsed, state["active_players"] if "active_players" in state else len(state["players"])))

    over_timeout = sum(1 for value in timings if value >= args.timeout)
    print(f"bot={bot_path}")
    print(f"states={args.states} seed={args.seed} errors={errors}")
    print(f"avg_ms={statistics.mean(timings) * 1000:.2f}")
    print(f"median_ms={statistics.median(timings) * 1000:.2f}")
    print(f"p90_ms={_percentile(timings, 90) * 1000:.2f}")
    print(f"p95_ms={_percentile(timings, 95) * 1000:.2f}")
    print(f"p99_ms={_percentile(timings, 99) * 1000:.2f}")
    print(f"max_ms={max(timings) * 1000:.2f}")
    print(f"over_{args.warn:.1f}s={len(slow)}")
    print(f"over_{args.timeout:.1f}s={over_timeout}")
    print("")
    for street, values in street_timings.items():
        if not values:
            continue
        print(
            f"{street:7} n={len(values):>4} avg_ms={statistics.mean(values) * 1000:>8.2f} "
            f"p95_ms={_percentile(values, 95) * 1000:>8.2f} max_ms={max(values) * 1000:>8.2f}"
        )
    if slow:
        print("")
        print("slow_examples")
        for index, street, elapsed, active_players in sorted(slow, key=lambda item: item[2], reverse=True)[:10]:
            print(f"index={index} street={street} active_players={active_players} elapsed_ms={elapsed * 1000:.2f}")


if __name__ == "__main__":
    main()
