# Challenger SOL V2 — Standalone Repository Setup

This package is intentionally separate from the production Challenger repository.

## What is protected

- `app.py` = SOL V2 experimental app.
- `SOL_V2_BASELINE_DO_NOT_EDIT.py` = byte-for-byte frozen copy of that SOL V2 app.
- The original Challenger repository is **read only** to this setup and is never modified.
- The Challenger source `app.py` is never allowed to replace SOL V2 `app.py`.

## Full support snapshot

The supporting repository files are pinned to this exact Challenger commit:

`1e696e484ada2fc4cb8a8a8b71a994e2988bc868`

That includes the Challenger support/data structure such as `learning_data/`, Savant files, tools, helper modules, and other tracked support files from that snapshot. Challenger workflow YAML files are preserved under `.github/challenger_workflows_disabled/` instead of being activated, because some original Challenger workflows can rebuild/commit `app.py`. This prevents them from ever replacing SOL V2.

Because ChatGPT's GitHub connector cannot directly export a repository archive as local bytes, this upload package completes the pinned snapshot **inside the new repository**. On the first push, `.github/workflows/complete_sol_v2_setup.yml` runs `sol_v2_bootstrap.py`, reads that pinned public Challenger snapshot, copies all support files except the SOL-owned protected files, verifies `app.py`, and commits the support into the NEW repository only.

Railway has a second safety net: `Procfile` runs `sol_v2_bootstrap.py`. If the GitHub Action has not populated support yet, Railway pulls the same pinned snapshot before starting Streamlit. After support exists, it simply starts SOL V2.

## Upload steps

1. Create a brand-new empty GitHub repository, for example `challenger-sol-v2`.
2. Unzip this package.
3. Upload **all files and folders from inside the ZIP** to the new repository and commit them.
4. Let the `Complete SOL V2 Repository` GitHub Action finish. It will add the pinned support files automatically.
5. Connect that new repository to a separate Railway service.
6. Copy any private environment variables/secrets you use in Challenger into the new Railway service manually. Secrets are not stored in this ZIP or copied from Challenger.

## Deployment behavior

The new SOL V2 service runs `app.py` directly with Streamlit. Challenger runtime patch scripts are preserved in the support snapshot for reference/integrity, but they are not automatically re-applied over SOL V2 at startup. This keeps SOL V2 behavior independent and prevents a Challenger runtime patch from unexpectedly changing the experiment.
