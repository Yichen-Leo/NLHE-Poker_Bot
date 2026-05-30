# Fullhouse Final Submission Checklist

Current candidate: `MyBot_v4_2`

Final local files:
- Main bot source: `bots/mybot/bot.py`

Recommendation:
- For the portal, upload the final single-file bot requested by the contest.
- For GitHub, keep only `bots/mybot/bot.py` and do not upload local packaging artifacts.

## Status Checked

- [x] Main bot name is `MyBot_v4_2`.
- [x] Bot uses only `eval7` and `random` imports.
- [x] No network / file write / subprocess / reflection calls detected by quick scan.
- [x] `sandbox/validator.py bots/mybot/bot.py` passed.
- [x] Heads-up smoke match ran successfully.
- [x] 6-max smoke match ran successfully.

## Final Validation Commands

Run these from repo root:

```bash
source .venv/bin/activate
python sandbox/validator.py bots/mybot/bot.py
python sandbox/match.py bots/mybot/bot.py bots/shark/bot.py --hands 100 --seed 9001
python sandbox/match.py bots/mybot/bot.py bots/shark/bot.py bots/aggressor/bot.py bots/mathematician/bot.py bots/template/bot.py bots/ref_bot_2/bot.py --hands 100 --seed 9002
```

Expected:
- Validator says `PASSED`.
- Match commands complete without bot errors.

## Five-Day Plan

### Day 5 — Freeze

- [x] Freeze `v4.2` as main candidate.
- [x] Confirm validator and smoke matches.

### Day 4 — Final Stability

- [x] Run one final Swiss-style simulation on fresh seeds.
- [x] Record avg, median, p10, bust rounds, and worst trials.
- [x] Do not tune based on one bad seed.

Result, seeds `5000-5029`:
- avg_delta: +28,775.7
- median_delta: +17,999.5
- p10_delta: +4,047.5
- min_delta: -5,103
- max_delta: +81,515
- rank 1: 9 / 30
- rank <= 2: 13 / 30
- rank <= 5: 23 / 30
- rank <= 8: 30 / 30
- full bust rounds: 13
- negative cumulative trials: 1 / 30

Suggested command:

```bash
python scripts/qualifier_sim.py \
  --trials 30 \
  --start-seed 5000 \
  --hands 400 \
  --rounds 3
```

### Day 3 — Candidate Gate Only

- [ ] Only test an experimental candidate if it has a very narrow, evidence-backed hypothesis.
- [ ] Reject unless it improves OOS Swiss score without increasing bust risk.
- [ ] If uncertain, keep `v4.2`.

### Day 2 — Documentation

- [ ] Write short strategy summary for GitHub / personal notes.
- [ ] Include high-level ideas only; do not overfit story to one seed.
- [ ] Save final experiment summary.

### Day 1 — Submission Rehearsal

- [ ] Run validator again.
- [ ] Upload the file requested by portal.
- [ ] Save exact uploaded file somewhere safe.

## Risk Register

### Biggest Strategic Risk

`v4.2` has high EV but occasional bust rounds. Previous guard attempts reduced profitability, so we are accepting controlled tail risk rather than weakening the value engine.

### Biggest Operational Risk

Uploading the wrong file or a dirty directory. Upload the single-file bot requested by the portal, not a folder with local cache files.

### Dependency Risk

Local environment uses `eval7>=0.1.10` successfully, while the original hackathon README may mention an older pinned version. The contest sandbox claims `eval7` is available, so validator passing locally is the main check.

### File Hygiene Risk

Repo has many untracked experiment files. This is okay locally, but GitHub should include only the final bot, documentation, and selected evaluation scripts.
