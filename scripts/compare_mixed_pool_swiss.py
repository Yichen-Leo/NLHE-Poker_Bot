#!/usr/bin/env python3
import argparse
import random
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sandbox.match import run_match
from scripts.evaluate_mybot import _bot_id_for_path, _path_map, _percentile
from scripts.qualifier_sim import DEFAULT_BOT_POOL, MYBOT, _make_tables, _pad_table, _rank


MC_BOTS = [
    "bots/sparring_mc_balanced/bot.py",
    "bots/sparring_mc_tight_value/bot.py",
    "bots/sparring_mc_loose_bluffcatcher/bot.py",
    "bots/sparring_mc_pressure/bot.py",
]

STRONG_BOTS = [
    "bots/shark/bot.py",
    "bots/mathematician/bot.py",
    "bots/ref_bot_2/bot.py",
    "bots/sparring_tight_value/bot.py",
    "bots/sparring_river_value/bot.py",
    "bots/sparring_trapper/bot.py",
    "bots/sparring_small_ball/bot.py",
    "bots/sparring_nit/bot.py",
]

PRESSURE_BOTS = [
    "bots/aggressor/bot.py",
    "bots/sparring_aggro_plus/bot.py",
    "bots/sparring_loose_bluffer/bot.py",
    "bots/sparring_polarized_overbet/bot.py",
    "bots/sparring_short_stack_jammer/bot.py",
    "bots/sparring_draw_chaser/bot.py",
    "bots/sparring_calling_station/bot.py",
    "bots/sparring_random_reg/bot.py",
]

FULL_PROFILE_BOTS = [
    path for path in DEFAULT_BOT_POOL + MC_BOTS if path != MYBOT
]


def _existing_bot_paths(paths):
    return [path for path in paths if (ROOT / path).exists()]


def _unique_paths(paths):
    seen = set()
    result = []
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        result.append(path)
    return result


def _allocate_counts(total, groups_and_ratios):
    raw = []
    allocated = 0
    for name, ratio, capacity in groups_and_ratios:
        exact = max(0.0, ratio) * total
        count = min(capacity, int(exact))
        raw.append([name, count, exact - int(exact), capacity])
        allocated += count

    while allocated < total:
        candidates = [item for item in raw if item[1] < item[3]]
        if not candidates:
            break
        candidates.sort(key=lambda item: (item[2], item[3] - item[1]), reverse=True)
        candidates[0][1] += 1
        allocated += 1

    return {name: count for name, count, _, _ in raw}


def _sample_group(rng, group, count):
    if count <= 0:
        return []
    shuffled = list(group)
    rng.shuffle(shuffled)
    return shuffled[: min(count, len(shuffled))]


def build_mixed_pool(seed, target, opponents, mc_ratio, strong_ratio, pressure_ratio):
    rng = random.Random(seed)
    ratios = [
        ("mc", mc_ratio, len(MC_BOTS)),
        ("strong", strong_ratio, len(STRONG_BOTS)),
        ("pressure", pressure_ratio, len(PRESSURE_BOTS)),
    ]
    ratio_total = sum(max(0.0, ratio) for _, ratio, _ in ratios)
    if ratio_total <= 0:
        raise ValueError("At least one pool ratio must be positive.")

    normalized = [(name, ratio / ratio_total, capacity) for name, ratio, capacity in ratios]
    counts = _allocate_counts(opponents, normalized)
    selected = (
        _sample_group(rng, MC_BOTS, counts["mc"])
        + _sample_group(rng, STRONG_BOTS, counts["strong"])
        + _sample_group(rng, PRESSURE_BOTS, counts["pressure"])
    )

    if len(selected) < opponents:
        fallback = _unique_paths(_existing_bot_paths(MC_BOTS + STRONG_BOTS + PRESSURE_BOTS))
        rng.shuffle(fallback)
        for path in fallback:
            if path in selected:
                continue
            selected.append(path)
            if len(selected) >= opponents:
                break

    rng.shuffle(selected)
    return [target] + selected, {
        "mc": sum(1 for path in selected if path in MC_BOTS),
        "strong": sum(1 for path in selected if path in STRONG_BOTS),
        "pressure": sum(1 for path in selected if path in PRESSURE_BOTS),
    }


def build_all_profile_pool(seed, target, opponents, mc_ratio):
    rng = random.Random(seed)
    mc_count = min(len(MC_BOTS), max(0, round(opponents * mc_ratio)))
    selected = _sample_group(rng, MC_BOTS, mc_count)

    fallback = [
        path
        for path in _unique_paths(_existing_bot_paths(FULL_PROFILE_BOTS))
        if path not in selected
    ]
    rng.shuffle(fallback)
    selected.extend(fallback[: max(0, opponents - len(selected))])
    rng.shuffle(selected)

    return [target] + selected, {
        "mc": sum(1 for path in selected if path in MC_BOTS),
        "strong": sum(1 for path in selected if path in STRONG_BOTS),
        "pressure": sum(1 for path in selected if path in PRESSURE_BOTS),
        "other": sum(
            1
            for path in selected
            if path not in MC_BOTS and path not in STRONG_BOTS and path not in PRESSURE_BOTS
        ),
    }


def _count_errors(errors):
    return {
        "errors": len(errors),
        "timeouts": sum(1 for error in errors if error == "timeout"),
    }


def _run_trial(trial_index, seed, bot_paths, hands, rounds, table_size, target_id):
    rng = random.Random(seed)
    bot_ids = [_bot_id_for_path(path) for path in bot_paths]
    id_to_path = dict(zip(bot_ids, bot_paths))
    scores = {bot_id: 0 for bot_id in bot_ids}
    target_errors = 0
    target_timeouts = 0

    for round_index in range(rounds):
        tables = _make_tables(bot_ids, scores, rng, round_index, table_size)
        for table_index, table in enumerate(tables):
            table = _pad_table(table, bot_ids, rng, table_size)
            if target_id not in table and len(table) < 2:
                continue

            table_paths = [id_to_path[bot_id] for bot_id in table]
            match_seed = seed * 100000 + round_index * 1000 + table_index
            random.seed(match_seed)
            result = run_match(
                match_id=f"mixed_pool_trial_{trial_index}_r{round_index}_t{table_index}",
                bot_paths=_path_map(table_paths),
                n_hands=hands,
                verbose=False,
                seed=match_seed,
            )

            for bot_id, delta in result["chip_delta"].items():
                scores[bot_id] += delta

            if target_id in table:
                counts = _count_errors(result["bot_errors"].get(target_id, []))
                target_errors += counts["errors"]
                target_timeouts += counts["timeouts"]

    return {
        "trial": trial_index,
        "seed": seed,
        "target_delta": scores[target_id],
        "target_rank": _rank(scores, target_id),
        "field_size": len(bot_ids),
        "target_errors": target_errors,
        "target_timeouts": target_timeouts,
    }


def _summary(trials):
    deltas = [trial["target_delta"] for trial in trials]
    ranks = [trial["target_rank"] for trial in trials]
    return {
        "avg": statistics.mean(deltas),
        "median": statistics.median(deltas),
        "p10": _percentile(deltas, 10),
        "min": min(deltas),
        "max": max(deltas),
        "rank1": sum(1 for rank in ranks if rank == 1),
        "rank_le2": sum(1 for rank in ranks if rank <= 2),
        "rank_le5": sum(1 for rank in ranks if rank <= 5),
        "negative": sum(1 for value in deltas if value < 0),
        "timeouts": sum(trial["target_timeouts"] for trial in trials),
        "errors": sum(trial["target_errors"] for trial in trials),
    }


def _print_summary(label, summary):
    print(
        f"{label:10} avg={summary['avg']:>9.1f} med={summary['median']:>9.1f} "
        f"p10={summary['p10']:>9.1f} min={summary['min']:>8} max={summary['max']:>8} "
        f"rank1={summary['rank1']} rank<=2={summary['rank_le2']} "
        f"rank<=5={summary['rank_le5']} neg={summary['negative']} "
        f"timeouts={summary['timeouts']} errors={summary['errors']}"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Compare v4.2 and a candidate on weighted mixed Swiss pools.")
    parser.add_argument("--candidate", default=None, help="Optional candidate bot.py to compare against v4.2.")
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--start-seed", type=int, default=9000)
    parser.add_argument("--hands", type=int, default=400)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--table-size", type=int, default=6)
    parser.add_argument("--opponents", type=int, default=12, help="Opponents sampled per trial, excluding mybot.")
    parser.add_argument(
        "--mode",
        choices=["weighted", "all_profiles"],
        default="all_profiles",
        help="weighted uses MC/strong/pressure groups; all_profiles samples from the full sparring pool with extra MC weight.",
    )
    parser.add_argument("--mc-ratio", type=float, default=0.45)
    parser.add_argument("--strong-ratio", type=float, default=0.25)
    parser.add_argument("--pressure-ratio", type=float, default=0.30)
    parser.add_argument("--show-pools", action="store_true", help="Print selected bots for each trial.")
    return parser.parse_args()


def main():
    args = parse_args()
    policies = [("v4.2", MYBOT)]
    if args.candidate:
        policies.append(("candidate", args.candidate))

    print(
        f"trials={args.trials} seeds={args.start_seed}..{args.start_seed + args.trials - 1} "
        f"hands={args.hands} rounds={args.rounds} opponents={args.opponents} "
        f"mode={args.mode} ratios=mc:{args.mc_ratio} strong:{args.strong_ratio} pressure:{args.pressure_ratio}"
    )

    results = {}
    for label, target in policies:
        trials = []
        target_id = _bot_id_for_path(target)
        for offset in range(args.trials):
            seed = args.start_seed + offset
            if args.mode == "all_profiles":
                pool, counts = build_all_profile_pool(
                    seed=seed,
                    target=target,
                    opponents=args.opponents,
                    mc_ratio=args.mc_ratio,
                )
            else:
                pool, counts = build_mixed_pool(
                    seed=seed,
                    target=target,
                    opponents=args.opponents,
                    mc_ratio=args.mc_ratio,
                    strong_ratio=args.strong_ratio,
                    pressure_ratio=args.pressure_ratio,
                )
            if args.show_pools:
                print(
                    f"{label:10} seed={seed:<5} pool_counts={counts} "
                    f"bots={'|'.join(Path(path).parent.name for path in pool)}"
                )
            trial = _run_trial(
                trial_index=offset,
                seed=seed,
                bot_paths=pool,
                hands=args.hands,
                rounds=args.rounds,
                table_size=args.table_size,
                target_id=target_id,
            )
            trials.append(trial)
            print(
                f"{label:10} seed={seed:<5} counts=mc:{counts.get('mc', 0)} "
                f"strong:{counts.get('strong', 0)} pressure:{counts.get('pressure', 0)} "
                f"other:{counts.get('other', 0)} delta={trial['target_delta']:>8} "
                f"rank={trial['target_rank']}/{trial['field_size']} "
                f"timeouts={trial['target_timeouts']} errors={trial['target_errors']}",
                flush=True,
            )
        results[label] = trials

    print("\nSummary")
    for label, trials in results.items():
        _print_summary(label, _summary(trials))

    if "candidate" in results:
        baseline = [trial["target_delta"] for trial in results["v4.2"]]
        candidate = [trial["target_delta"] for trial in results["candidate"]]
        diff = [candidate_value - baseline_value for baseline_value, candidate_value in zip(baseline, candidate)]
        print(
            f"diff       avg={statistics.mean(diff):>9.1f} med={statistics.median(diff):>9.1f} "
            f"p10={_percentile(diff, 10):>9.1f} min={min(diff):>8} max={max(diff):>8}"
        )


if __name__ == "__main__":
    main()
