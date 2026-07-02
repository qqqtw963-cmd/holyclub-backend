# HolyClub backend hotfix normalization plan

Date: 2026-07-02
Repo: `/Users/parkseongjeon/Desktop/holyclub-backend`
Target: normalize the live `holyclub-api:23` recovery changes into the repo without accidentally shipping unrelated in-progress work.

## Current inventory buckets

### A. Release-critical / live-recovery bundle (`ship-now`)
Files that directly match the deployed ECS recovery image or are required for the `home_content` API path:
- `Dockerfile`
- `gunicorn.conf.py`
- `requirements.txt`
- `app/home_content/**`
- `app/urls/api.py`
- `config/settings/base.py`
- `config/settings/prod.py`
- `config/settings/test.py`
- `docs/runtime-content-smoke-test.md`

### B. Unrelated feature work present in working tree (`defer`)
Keep out of the normalization commit unless separately requested:
- `app/bible/**`
- `app/email_log/utils.py`
- `app/prayer_bgm_track/v1/views.py`
- `app/testimony_journal/**`
- `app/user/**`
- `app/verifier/v1/serializers.py`
- other non-`home_content` API/schema work currently modified

## Safe cleanup candidates
- Do not delete source files from bucket B.
- Ignore transient `__pycache__/` files under `app/home_content/`; they are not part of the commit.
- Temporary deployment build directories under `/tmp/holyclub-backend-hotfix*` are reference-only and should not become source of truth.

## Release-in criteria
A file belongs in this normalization pass only if one of the following is true:
1. It was part of the deployed recovery image used to restore production.
2. It is required to run or route the `home_content` API in source control.
3. It documents the validated deploy/smoke-test path for this exact recovery.

## Release-out criteria
A file stays out of this pass if:
1. It is unrelated feature work already in progress before/alongside the incident.
2. It was not needed for the deployed production recovery.
3. It requires separate product verification unrelated to the `home_content` outage.

## Validation gates
Before commit/push:
- verify release-critical files in the repo match the deployed hotfix reference content
- verify only the intended file bundle is staged
- run targeted sanity checks where possible (`manage.py check` or tests if settings permit)
- keep unrelated modifications unstaged

## Branching / staging order
1. Inventory current working tree and confirm deployed-reference parity.
2. Stage only the live-recovery bundle.
3. Commit as a focused hotfix normalization commit on the current branch unless the user requests a separate branch.
4. Push only after remote/auth confirmation.
5. Add/update deploy documentation and follow-up notes for:
   - migration requirement
   - SCRAM/libpq dependency pitfall
   - gunicorn/ALB port alignment
   - Firebase warning follow-up
   - `home_content` data seeding/activation follow-up

## Expected outcome
- Production recovery changes are preserved in git.
- Unrelated feature work remains untouched in the working tree.
- The next deployment can be reproduced from the repo instead of temporary build directories.
