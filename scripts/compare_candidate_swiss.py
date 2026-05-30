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


DETERMINISTIC_POOL = [
    MYBOT,
    "bots/mathematician/bot.py",
    "bots/ref_bot_2/bot.py",
    "bots/sparring_aggro_plus/bot.py",
    "bots/sparring_calling_station/bot.py",
    "bots/sparring_nit/bot.py",
    "bots/sparring_tight_value/bot.py",
    "bots/sparring_loose_bluffer/bot.py",
    "bots/sparring_river_value/bot.py",
    "bots/sparring_short_stack_jammer/bot.py",
    "bots/sparring_trapper/bot.py",
    "bots/sparring_small_ball/bot.py",
    "bots/sparring_draw_chaser/bot.py",
    "bots/sparring_polarized_overbet/bot.py",
    "bots/sparring_random_reg/bot.py",
]

MC_RANDOM_POOL = [
    MYBOT,
    "bots/ref_bot_2/bot.py",
    "bots/mathematician/bot.py",
    "bots/shark/bot.py",
    "bots/aggressor/bot.py",
    "bots/sparring_mc_balanced/bot.py",
    "bots/sparring_mc_tight_value/bot.py",
    "bots/sparring_mc_loose_bluffcatcher/bot.py",
    "bots/sparring_mc_pressure/bot.py",
    "bots/sparring_aggro_plus/bot.py",
    "bots/sparring_tight_value/bot.py",
    "bots/sparring_river_value/bot.py",
    "bots/sparring_loose_bluffer/bot.py",
    "bots/sparring_polarized_overbet/bot.py",
    "bots/sparring_random_reg/bot.py",
    "bots/sparring_trapper/bot.py",
]


def _existing_bot_paths(paths):
    existing = []
    for path in paths:
        if (ROOT / path).exists():
            existing.append(path)
    return existing


def _summary(trials):
    deltas = [trial["target_delta"] for trial in trials]
    ranks = [trial["target_rank"] for trial in trials]
    timeouts = [trial["target_timeouts"] for trial in trials]
    errors = [trial["target_errors"] for trial in trials]
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
        "timeouts": sum(timeouts),
        "errors": sum(errors),
    }


def _print_summary(label, summary):
    print(
        f"{label:10} avg={summary['avg']:>9.1f} med={summary['median']:>9.1f} "
        f"p10={summary['p10']:>9.1f} min={summary['min']:>8} max={summary['max']:>8} "
        f"rank1={summary['rank1']} rank<=2={summary['rank_le2']} "
        f"rank<=5={summary['rank_le5']} neg={summary['negative']} "
        f"timeouts={summary['timeouts']} errors={summary['errors']}"
    )


def _bot_pool_for(target, pool):
    return [target if path == MYBOT else path for path in pool]


def _count_errors(errors):
    return {
        "errors": len(errors),
        "timeouts": sum(1 for error in errors if error == "timeout"),
    }


def _run_trial_with_errors(trial_index, seed, bot_paths, hands, rounds, table_size, target_id):
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
                match_id=f"candidate_trial_{trial_index}_r{round_index}_t{table_index}",
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


def main():
    parser = argparse.ArgumentParser(description="Compare baseline v4.2 and candidate in Swiss-style trials.")
    parser.add_argument("--candidate", required=True, help="Candidate bot.py to compare against v4.2.")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--start-seed", type=int, default=6400)
    parser.add_argument("--hands", type=int, default=400)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--table-size", type=int, default=6)
    parser.add_argument("--pool", choices=["full", "deterministic", "mc_random"], default="full")
    args = parser.parse_args()
    if args.pool == "full":
        pool = _existing_bot_paths(DEFAULT_BOT_POOL)
    elif args.pool == "deterministic":
        pool = _existing_bot_paths(DETERMINISTIC_POOL)
    else:
        pool = _existing_bot_paths(MC_RANDOM_POOL)

    policies = [("v4.2", MYBOT), ("candidate", args.candidate)]
    results = {}
    print(
        f"trials={args.trials} seeds={args.start_seed}..{args.start_seed + args.trials - 1} "
        f"hands={args.hands} rounds={args.rounds} pool={args.pool} candidate={args.candidate}"
    )
    for label, target in policies:
        trials = []
        for offset in range(args.trials):
            seed = args.start_seed + offset
            trial = _run_trial_with_errors(
                trial_index=offset,
                seed=seed,
                bot_paths=_bot_pool_for(target, pool),
                hands=args.hands,
                rounds=args.rounds,
                table_size=args.table_size,
                target_id=Path(target).parent.name if target.endswith("/bot.py") else Path(target).stem,
            )
            trials.append(trial)
            print(
                f"{label:10} seed={seed:<5} delta={trial['target_delta']:>8} "
                f"rank={trial['target_rank']}/{trial['field_size']} "
                f"timeouts={trial['target_timeouts']} errors={trial['target_errors']}",
                flush=True,
            )
        results[label] = trials

    print("\nSummary")
    summaries = {label: _summary(trials) for label, trials in results.items()}
    for label, summary in summaries.items():
        _print_summary(label, summary)

    baseline = [trial["target_delta"] for trial in results["v4.2"]]
    candidate = [trial["target_delta"] for trial in results["candidate"]]
    diff = [candidate_value - baseline_value for baseline_value, candidate_value in zip(baseline, candidate)]
    print(
        f"diff       avg={statistics.mean(diff):>9.1f} med={statistics.median(diff):>9.1f} "
        f"p10={_percentile(diff, 10):>9.1f} min={min(diff):>8} max={max(diff):>8}"
    )


if __name__ == "__main__":
    main()
