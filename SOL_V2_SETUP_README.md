# Challenger SOL V2 — Standalone Repository Setup

This repository is intentionally separate from the production Challenger repository.

## What is protected

- `app.py` = SOL V2 experimental K app.
- `SOL_V2_BASELINE_DO_NOT_EDIT.py` = byte-for-byte frozen copy of the SOL V2 baseline.
- The original Challenger repository is read only to this setup and is never modified.
- Challenger `app.py` is never allowed to replace SOL V2 `app.py`.
- SOL V2 does not reapply Challenger K, Moneyline, or Pitching Outs model patches at runtime.

## Pinned support snapshot

Supporting repository files are pinned to Challenger commit:

`1e696e484ada2fc4cb8a8a8b71a994e2988bc868`

That snapshot supplies `learning_data/`, Savant files, helper modules, runtime tools, and other tracked support files. Challenger workflow YAML files are copied only into `.github/challenger_workflows_disabled/`, never activated in SOL V2.

## Runtime behavior

Railway starts:

`python sol_v2_bootstrap.py`

The bootstrap first ensures the pinned Challenger support snapshot exists locally, then hands control to `sol_v2_launch_stable.py`.

`sol_v2_launch_stable.py` copies the protected SOL `app.py` to disposable `runtime_app.py` and applies ONLY operational stability guards:

- `apply_runtime_stability_v1.py`
- `apply_manual_refresh_state_v2.py`
- `apply_savant_manual_only_v3.py`
- `apply_recency_cache_guard_v3.py`
- `apply_recency_lazy_guard_v2.py`

This preserves Challenger-style Save / explicit Refresh / Savant / cache stability while keeping SOL V2's K experiment independent. K-model patches, Moneyline patches, and Pitching Outs patches are intentionally NOT re-applied over SOL V2 at startup.

Streamlit source watching and run-on-save are disabled in production, matching the stable Challenger runtime pattern.

## Self-hydration

`.github/workflows/complete_sol_v2_setup.yml` hydrates the pinned support snapshot into this repository and verifies:

- SOL `app.py` still matches `SOL_V2_BASELINE_DO_NOT_EDIT.py` byte-for-byte.
- Required learning/Savant support files exist.
- Required operational runtime guard scripts exist.
- SOL source and launcher compile.

The workflow commits hydrated support into SOL V2 only. It never writes to Challenger.

## Manual hydration

To populate support manually without launching Streamlit:

```bash
python sol_v2_bootstrap.py --populate-only
```

To force-refresh the local support tree from the same pinned Challenger commit:

```bash
python sol_v2_bootstrap.py --populate-only --force
```

## Railway

Connect this repository to its own Railway service. Copy any private environment variables/secrets used by Challenger into the SOL V2 Railway service manually; secrets are not stored in GitHub or copied by this bootstrap.

The intended A/B setup is:

- Challenger = primary Codex-updated model.
- SOL V2 = separate shadow/aggressive K candidate.
- UD2.0 = existing benchmark.
- Undefeated = existing benchmark.
