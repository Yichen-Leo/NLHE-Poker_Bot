#!/usr/bin/env python3
import argparse
import csv
import random
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sandbox.match import run_match
from scripts.evaluate_mybot import MYBOT, _bot_id_for_path, _path_map, _percentile


DEFAULT_BOT_POOL = [
    MYBOT,
    "bots/shark/bot.py",
    "bots/aggressor/bot.py",
    "bots/mathematician/bot.py",
    "bots/template/bot.py",
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


def _existing_bot_paths(paths):
    existing = []
    omitted = []
    for path in paths:
        if (ROOT / path).exists():
            existing.append(path)
        else:
            omitted.append(path)
    if omitted:
        print(
            f"Note: skipped {len(omitted)} unavailable private/reference bot files.",
            flush=True,
        )
    return existing


def _unique_paths(paths):
    seen = set()
    result = []
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        result.append(path)
    return result


def _rank(scores, target_id):
    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    for index, (bot_id, _) in enumerate(ordered, start=1):
        if bot_id == target_id:
            return index
    return len(ordered)


def _make_tables(bot_ids, scores, rng, round_index, table_size):
    if round_index == 0:
        shuffled = list(bot_ids)
        rng.shuffle(shuffled)
        return [shuffled[index : index + table_size] for index in range(0, len(shuffled), table_size)]

    ordered = sorted(bot_ids, key=lambda bot_id: scores[bot_id], reverse=True)
    return [ordered[index : index + table_size] for index in range(0, len(ordered), table_size)]


def _pad_table(table, bot_ids, rng, table_size):
    if len(table) >= 2:
        return table

    candidates = [bot_id for bot_id in bot_ids if bot_id not in table]
    rng.shuffle(candidates)
    return table + candidates[: max(0, min(table_size, 2) - len(table))]


def run_trial(trial_index, seed, bot_paths, hands, rounds, table_size, target_id):
    rng = random.Random(seed)
    bot_ids = [_bot_id_for_path(path) for path in bot_paths]
    id_to_path = dict(zip(bot_ids, bot_paths))
    scores = {bot_id: 0 for bot_id in bot_ids}
    round_rows = []

    for round_index in range(rounds):
        tables = _make_tables(bot_ids, scores, rng, round_index, table_size)
        for table_index, table in enumerate(tables):
            table = _pad_table(table, bot_ids, rng, table_size)
            if target_id not in table and len(table) < 2:
                continue

            table_paths = [id_to_path[bot_id] for bot_id in table]
            match_seed = seed * 100000 + round_index * 1000 + table_index
            result = run_match(
                match_id=f"qualifier_trial_{trial_index}_r{round_index}_t{table_index}",
                bot_paths=_path_map(table_paths),
                n_hands=hands,
                verbose=False,
                seed=match_seed,
            )

            for bot_id, delta in result["chip_delta"].items():
                scores[bot_id] += delta

            if target_id in table:
                round_rows.append(
                    {
                        "trial": trial_index,
                        "seed": seed,
                        "round": round_index + 1,
                        "table": table_index,
                        "target_delta": result["chip_delta"][target_id],
                        "target_cumulative": scores[target_id],
                        "target_rank_after_round": _rank(scores, target_id),
                        "table_bots": "|".join(table),
                    }
                )

    return {
        "trial": trial_index,
        "seed": seed,
        "target_delta": scores[target_id],
        "target_rank": _rank(scores, target_id),
        "field_size": len(bot_ids),
        "advanced_top_64": _rank(scores, target_id) <= min(64, len(bot_ids)),
        "round_rows": round_rows,
    }


def _summarize(trials):
    deltas = [trial["target_delta"] for trial in trials]
    ranks = [trial["target_rank"] for trial in trials]
    return {
        "trials": len(trials),
        "avg_delta": statistics.mean(deltas),
        "median_delta": statistics.median(deltas),
        "p10_delta": _percentile(deltas, 10),
        "p25_delta": _percentile(deltas, 25),
        "p75_delta": _percentile(deltas, 75),
        "p90_delta": _percentile(deltas, 90),
        "min_delta": min(deltas),
        "max_delta": max(deltas),
        "avg_rank": statistics.mean(ranks),
        "median_rank": statistics.median(ranks),
        "advance_rate_top_64": sum(trial["advanced_top_64"] for trial in trials) / len(trials),
    }


def _write_csv(path, trials):
    if not path:
        return
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["trial", "seed", "target_delta", "target_rank", "field_size", "advanced_top_64"],
        )
        writer.writeheader()
        for trial in trials:
            writer.writerow({key: trial[key] for key in writer.fieldnames})
    print(f"Wrote CSV: {output}", flush=True)


def _write_round_csv(path, trials):
    if not path:
        return
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = [row for trial in trials for row in trial["round_rows"]]
    with output.open("w", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "trial",
                "seed",
                "round",
                "table",
                "target_delta",
                "target_cumulative",
                "target_rank_after_round",
                "table_bots",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote round CSV: {output}", flush=True)


def _write_notes(path, summary, trials):
    if not path:
        return
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Qualifier Simulation", ""]
    lines.append("## Summary")
    for key, value in summary.items():
        if isinstance(value, float):
            lines.append(f"- {key}: {value:.2f}")
        else:
            lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Worst Trials")
    for trial in sorted(trials, key=lambda item: item["target_delta"])[:10]:
        lines.append(
            f"- trial={trial['trial']} seed={trial['seed']} delta={trial['target_delta']} "
            f"rank={trial['target_rank']}/{trial['field_size']}"
        )
    lines.append("")
    lines.append("## Best Trials")
    for trial in sorted(trials, key=lambda item: item["target_delta"], reverse=True)[:10]:
        lines.append(
            f"- trial={trial['trial']} seed={trial['seed']} delta={trial['target_delta']} "
            f"rank={trial['target_rank']}/{trial['field_size']}"
        )
    output.write_text("\n".join(lines))
    print(f"Wrote notes: {output}", flush=True)


def parse_args():
    parser = argparse.ArgumentParser(description="Simulate 3-round Swiss-style qualifier standings.")
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--start-seed", type=int, default=4000)
    parser.add_argument("--hands", type=int, default=400)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--table-size", type=int, default=6)
    parser.add_argument("--bot", action="append", help="Bot path to include. Defaults to expanded local pool.")
    parser.add_argument("--csv")
    parser.add_argument("--round-csv")
    parser.add_argument("--notes")
    return parser.parse_args()


def main():
    args = parse_args()
    bot_paths = _unique_paths(args.bot or _existing_bot_paths(DEFAULT_BOT_POOL))
    if MYBOT not in bot_paths:
        bot_paths.insert(0, MYBOT)

    target_id = _bot_id_for_path(MYBOT)
    trials = []
    print(
        f"trials={args.trials} rounds={args.rounds} hands={args.hands} "
        f"field={len(bot_paths)} table_size={args.table_size}",
        flush=True,
    )
    for offset in range(args.trials):
        seed = args.start_seed + offset
        trial = run_trial(offset, seed, bot_paths, args.hands, args.rounds, args.table_size, target_id)
        trials.append(trial)
        print(
            f"trial={offset:<3} seed={seed:<5} delta={trial['target_delta']:>7} "
            f"rank={trial['target_rank']}/{trial['field_size']}",
            flush=True,
        )

    summary = _summarize(trials)
    print("\nSummary", flush=True)
    for key, value in summary.items():
        print(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}", flush=True)

    _write_csv(args.csv, trials)
    _write_round_csv(args.round_csv, trials)
    _write_notes(args.notes, summary, trials)


if __name__ == "__main__":
    main()
