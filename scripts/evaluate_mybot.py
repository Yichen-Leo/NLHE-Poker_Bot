#!/usr/bin/env python3
import argparse
import csv
import statistics
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.game import STARTING_STACK
from sandbox.match import run_match


MYBOT = "bots/mybot/bot.py"

SCENARIOS = {
    "heads_up_shark": [
        MYBOT,
        "bots/shark/bot.py",
    ],
    "heads_up_aggressor": [
        MYBOT,
        "bots/aggressor/bot.py",
    ],
    "heads_up_mathematician": [
        MYBOT,
        "bots/mathematician/bot.py",
    ],
    "heads_up_template": [
        MYBOT,
        "bots/template/bot.py",
    ],
    "self_play_heads_up": [
        MYBOT,
        MYBOT,
    ],
    "three_bot_pressure": [
        MYBOT,
        "bots/shark/bot.py",
        "bots/aggressor/bot.py",
    ],
    "four_bot_mixed": [
        MYBOT,
        "bots/shark/bot.py",
        "bots/aggressor/bot.py",
        "bots/mathematician/bot.py",
    ],
    "self_play_six": [
        MYBOT,
        MYBOT,
        MYBOT,
        MYBOT,
        MYBOT,
        MYBOT,
    ],
    "six_bot_reference": [
        MYBOT,
        "bots/shark/bot.py",
        "bots/aggressor/bot.py",
        "bots/mathematician/bot.py",
        "bots/template/bot.py",
        "bots/ref_bot_2/bot.py",
    ],
    "strong_sparring_pool_ref2": [
        MYBOT,
        "bots/ref_bot_2/bot.py",
        "bots/sparring_aggro_plus/bot.py",
        "bots/sparring_tight_value/bot.py",
        "bots/sparring_calling_station/bot.py",
        "bots/shark/bot.py",
    ],
    "strong_sparring_pool": [
        MYBOT,
        "bots/sparring_aggro_plus/bot.py",
        "bots/sparring_tight_value/bot.py",
        "bots/sparring_calling_station/bot.py",
        "bots/sparring_nit/bot.py",
        "bots/shark/bot.py",
    ],
    "pressure_sparring_pool_ref2": [
        MYBOT,
        "bots/ref_bot_2/bot.py",
        "bots/sparring_aggro_plus/bot.py",
        "bots/aggressor/bot.py",
        "bots/sparring_tight_value/bot.py",
        "bots/sparring_calling_station/bot.py",
    ],
    "pressure_sparring_pool": [
        MYBOT,
        "bots/sparring_aggro_plus/bot.py",
        "bots/aggressor/bot.py",
        "bots/sparring_tight_value/bot.py",
        "bots/sparring_calling_station/bot.py",
        "bots/shark/bot.py",
    ],
    "generalization_value_pool_ref2": [
        MYBOT,
        "bots/ref_bot_2/bot.py",
        "bots/sparring_river_value/bot.py",
        "bots/sparring_tight_value/bot.py",
        "bots/sparring_trapper/bot.py",
        "bots/shark/bot.py",
    ],
    "generalization_value_pool": [
        MYBOT,
        "bots/sparring_river_value/bot.py",
        "bots/sparring_tight_value/bot.py",
        "bots/sparring_trapper/bot.py",
        "bots/sparring_nit/bot.py",
        "bots/shark/bot.py",
    ],
    "generalization_pressure_pool_ref2": [
        MYBOT,
        "bots/ref_bot_2/bot.py",
        "bots/sparring_loose_bluffer/bot.py",
        "bots/sparring_aggro_plus/bot.py",
        "bots/sparring_short_stack_jammer/bot.py",
        "bots/aggressor/bot.py",
    ],
    "generalization_pressure_pool": [
        MYBOT,
        "bots/sparring_loose_bluffer/bot.py",
        "bots/sparring_aggro_plus/bot.py",
        "bots/sparring_short_stack_jammer/bot.py",
        "bots/sparring_calling_station/bot.py",
        "bots/aggressor/bot.py",
    ],
    "generalization_mixed_pool_ref2": [
        MYBOT,
        "bots/ref_bot_2/bot.py",
        "bots/sparring_river_value/bot.py",
        "bots/sparring_loose_bluffer/bot.py",
        "bots/sparring_trapper/bot.py",
        "bots/sparring_short_stack_jammer/bot.py",
    ],
    "generalization_mixed_pool": [
        MYBOT,
        "bots/sparring_river_value/bot.py",
        "bots/sparring_loose_bluffer/bot.py",
        "bots/sparring_trapper/bot.py",
        "bots/sparring_short_stack_jammer/bot.py",
        "bots/sparring_calling_station/bot.py",
    ],
    "expanded_style_pool": [
        MYBOT,
        "bots/sparring_small_ball/bot.py",
        "bots/sparring_draw_chaser/bot.py",
        "bots/sparring_polarized_overbet/bot.py",
        "bots/sparring_random_reg/bot.py",
        "bots/ref_bot_2/bot.py",
    ],
    "expanded_pressure_pool": [
        MYBOT,
        "bots/sparring_polarized_overbet/bot.py",
        "bots/sparring_loose_bluffer/bot.py",
        "bots/sparring_aggro_plus/bot.py",
        "bots/sparring_short_stack_jammer/bot.py",
        "bots/aggressor/bot.py",
    ],
    "expanded_value_pool": [
        MYBOT,
        "bots/sparring_small_ball/bot.py",
        "bots/sparring_draw_chaser/bot.py",
        "bots/sparring_river_value/bot.py",
        "bots/sparring_trapper/bot.py",
        "bots/sparring_tight_value/bot.py",
    ],
}


def _bot_id_for_path(path_text):
    path = Path(path_text)
    if path.suffix in (".py", ".zip"):
        bot_id = path.stem
    else:
        bot_id = path.name
    if bot_id == "bot":
        bot_id = path.parent.name
    return bot_id


def _path_map(paths):
    result = {}
    for index, path_text in enumerate(paths):
        bot_id = _bot_id_for_path(path_text)
        if bot_id in result:
            bot_id = f"{bot_id}_{index}"
        result[bot_id] = str(ROOT / path_text)
    return result


def _percentile(values, percent):
    if not values:
        return 0

    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]

    index = (len(sorted_values) - 1) * percent / 100
    lower = int(index)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = index - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def _stack_rank(final_stacks, mybot_id):
    ordered = sorted(final_stacks.items(), key=lambda item: item[1], reverse=True)
    for index, (bot_id, _) in enumerate(ordered, start=1):
        if bot_id == mybot_id:
            return index
    return len(ordered)


def _summarize(values, final_stacks, hands_played, ranks):
    busts = sum(1 for stack in final_stacks if stack <= 0)
    wins = sum(1 for value in values if value > 0)
    losses = sum(1 for value in values if value < 0)

    return {
        "avg": statistics.mean(values),
        "median": statistics.median(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
        "p10": _percentile(values, 10),
        "p25": _percentile(values, 25),
        "p75": _percentile(values, 75),
        "p90": _percentile(values, 90),
        "min": min(values),
        "max": max(values),
        "busts": busts,
        "bust_rate": busts / len(values),
        "win_rate": wins / len(values),
        "loss_rate": losses / len(values),
        "avg_hands": statistics.mean(hands_played),
        "avg_rank": statistics.mean(ranks),
    }


def _print_summary(name, summary, worst_seed, best_seed):
    print(f"\n{name}", flush=True)
    print("-" * len(name), flush=True)
    print(f"avg_delta:   {summary['avg']:>8.1f}", flush=True)
    print(f"median:      {summary['median']:>8.1f}", flush=True)
    print(f"stdev:       {summary['stdev']:>8.1f}", flush=True)
    print(f"p10/p25:     {summary['p10']:>8.1f} / {summary['p25']:>8.1f}", flush=True)
    print(f"p75/p90:     {summary['p75']:>8.1f} / {summary['p90']:>8.1f}", flush=True)
    print(f"min_delta:   {summary['min']:>8}", flush=True)
    print(f"max_delta:   {summary['max']:>8}", flush=True)
    print(f"busts:       {summary['busts']:>8} ({summary['bust_rate']:.1%})", flush=True)
    print(f"win_rate:    {summary['win_rate']:>8.1%}", flush=True)
    print(f"loss_rate:   {summary['loss_rate']:>8.1%}", flush=True)
    print(f"avg_hands:   {summary['avg_hands']:>8.1f}", flush=True)
    print(f"avg_rank:    {summary['avg_rank']:>8.2f}", flush=True)
    print(f"worst_seed:  {worst_seed:>8}", flush=True)
    print(f"best_seed:   {best_seed:>8}", flush=True)


def _print_worst_runs(rows, limit):
    if limit <= 0:
        return

    print(f"\nWorst {limit} runs", flush=True)
    print("-" * 12, flush=True)
    for row in sorted(rows, key=lambda item: item["delta"])[:limit]:
        print(
            f"{row['scenario']:22} seed={row['seed']:<5} "
            f"delta={row['delta']:>7} stack={row['final_stack']:>6} "
            f"rank={row['rank']}/{row['players']} busted={row['busted']}",
            flush=True,
        )


def _write_csv(path, rows):
    if not path:
        return

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "scenario",
        "seed",
        "hands",
        "delta",
        "final_stack",
        "rank",
        "players",
        "busted",
        "duration_s",
    ]
    with output_path.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote CSV: {output_path}", flush=True)


def _write_summary_csv(path, summaries):
    if not path:
        return

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "scenario",
        "avg",
        "median",
        "stdev",
        "p10",
        "p25",
        "p75",
        "p90",
        "min",
        "max",
        "busts",
        "bust_rate",
        "win_rate",
        "loss_rate",
        "avg_hands",
        "avg_rank",
        "worst_seed",
        "best_seed",
    ]
    with output_path.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summaries)
    print(f"Wrote summary CSV: {output_path}", flush=True)


def evaluate_scenario(name, paths, seeds, hands, quiet=False):
    bot_paths = _path_map(paths)
    mybot_id = _bot_id_for_path(MYBOT)

    deltas = []
    final_stacks = []
    hands_played = []
    ranks = []
    rows = []
    worst_seed = None
    best_seed = None
    worst_delta = None
    best_delta = None

    for seed in seeds:
        result = run_match(
            match_id=f"eval_{name}_{seed}",
            bot_paths=bot_paths,
            n_hands=hands,
            verbose=False,
            seed=seed,
        )
        delta = result["chip_delta"][mybot_id]
        final_stack = result["final_stacks"][mybot_id]
        rank = _stack_rank(result["final_stacks"], mybot_id)

        deltas.append(delta)
        final_stacks.append(final_stack)
        hands_played.append(result["n_hands"])
        ranks.append(rank)

        if worst_delta is None or delta < worst_delta:
            worst_delta = delta
            worst_seed = seed
        if best_delta is None or delta > best_delta:
            best_delta = delta
            best_seed = seed

        row = {
            "scenario": name,
            "seed": seed,
            "hands": result["n_hands"],
            "delta": delta,
            "final_stack": final_stack,
            "rank": rank,
            "players": len(result["bot_ids"]),
            "busted": final_stack <= 0,
            "duration_s": result["duration_s"],
        }
        rows.append(row)

        if not quiet:
            print(
                f"{name:22} seed={seed:<5} "
                f"delta={delta:>7} stack={final_stack:>6} "
                f"rank={rank}/{len(result['bot_ids'])} hands={result['n_hands']:>4}",
                flush=True,
            )

    summary = _summarize(deltas, final_stacks, hands_played, ranks)
    _print_summary(name, summary, worst_seed, best_seed)
    summary_row = {"scenario": name, "worst_seed": worst_seed, "best_seed": best_seed, **summary}
    return rows, summary_row


def parse_args():
    parser = argparse.ArgumentParser(description="Batch-evaluate bots/mybot against reference scenarios.")
    parser.add_argument("--hands", type=int, default=400)
    parser.add_argument("--seeds", type=int, default=5, help="Number of seeds to run per scenario.")
    parser.add_argument("--start-seed", type=int, default=100)
    parser.add_argument("--csv", help="Optional path to write per-run CSV results.")
    parser.add_argument("--summary-csv", help="Optional path to write per-scenario summary CSV.")
    parser.add_argument("--worst", type=int, default=5, help="Print the N worst runs across selected scenarios.")
    parser.add_argument("--quiet", action="store_true", help="Only print summaries, not every seed result.")
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS),
        action="append",
        help="Scenario to run. May be passed multiple times. Defaults to all scenarios.",
    )
    parser.add_argument(
        "--scenario-run",
        action="append",
        metavar="SCENARIO:START_SEED:SEEDS",
        help=(
            "Run one scenario with its own seed range. "
            "Example: --scenario-run strong_sparring_pool:1300:15. "
            "May be passed multiple times; overrides --scenario/--start-seed/--seeds."
        ),
    )
    return parser.parse_args()


def _parse_scenario_runs(items):
    runs = []
    for item in items or []:
        parts = item.split(":")
        if len(parts) != 3:
            raise SystemExit(f"Invalid --scenario-run '{item}', expected SCENARIO:START_SEED:SEEDS")
        scenario, start_seed_text, seeds_text = parts
        if scenario not in SCENARIOS:
            choices = ", ".join(sorted(SCENARIOS))
            raise SystemExit(f"Unknown scenario '{scenario}'. Choices: {choices}")
        try:
            start_seed = int(start_seed_text)
            seed_count = int(seeds_text)
        except ValueError as exc:
            raise SystemExit(f"Invalid --scenario-run '{item}', START_SEED and SEEDS must be integers") from exc
        if seed_count <= 0:
            raise SystemExit(f"Invalid --scenario-run '{item}', SEEDS must be positive")
        seeds = list(range(start_seed, start_seed + seed_count))
        runs.append((scenario, seeds))
    return runs


def main():
    args = parse_args()
    scenario_runs = _parse_scenario_runs(args.scenario_run)
    if not scenario_runs:
        selected = args.scenario or list(SCENARIOS)
        seeds = list(range(args.start_seed, args.start_seed + args.seeds))
        scenario_runs = [(name, seeds) for name in selected]
    started_at = time.time()

    run_text = ", ".join(
        f"{name}:{seeds[0]}..{seeds[-1]}" for name, seeds in scenario_runs
    )
    print(f"hands={args.hands} runs={run_text}", flush=True)

    all_rows = []
    summaries = []
    for name, seeds in scenario_runs:
        rows, summary = evaluate_scenario(name, SCENARIOS[name], seeds, args.hands, quiet=args.quiet)
        all_rows.extend(rows)
        summaries.append(summary)

    _print_worst_runs(all_rows, args.worst)
    _write_csv(args.csv, all_rows)
    _write_summary_csv(args.summary_csv, summaries)

    print(f"\nTotal eval time: {time.time() - started_at:.1f}s", flush=True)


if __name__ == "__main__":
    main()
