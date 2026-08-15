# P5 Rebrand — Rollback Plan

## What this document covers

- **Local rollback** (this checkout) — instructions to revert the branch to
  the exact base SHA without losing the migration ledgers.
- **Future production rollback** — the pre-approved procedure to promote the
  last known-good Vercel deployment if / when this branch is ever deployed
  and needs to be reverted. Deployment is **NOT** authorized by the current
  packet; this section exists so the rollback is ready when the next phase
  authorizes it.

## 1. Local rollback (this branch)

The rebrand is committed on the feature branch. `main` is untouched.

### 1.1 Preserve baseline manifests

The `artifacts/` folder contains:
- `baseline-manifest.json` — pinned identity + counts
- `baseline-routes.json` — pinned baseline sitemap URLs (122)
- `baseline-integration-hashes.json` — pinned integration snippet hashes
- `route-diff.md`, `redirect-map.json`, `proposed-routes.json`
- `portfolio-proof-migration.csv` — proof ledger
- `copy-migration-manifest.md` — copy decisions

**Do not discard these.** They document the analysis even if the rebrand is
rejected. Save them (copy the `artifacts/` folder out of the checkout)
before doing any destructive git operation.

### 1.2 Discard the branch entirely

If the whole rebrand is rejected:

```
# Inspect the state you are about to lose
git status
git log --oneline claude/p5-branding-marketing-sales-rebrand ^main

# Optional: keep a snapshot bundle first (recommended)
git bundle create /path/to/backup/p5-rebrand-snapshot.bundle \
    claude/p5-branding-marketing-sales-rebrand

# Return the working tree to the base SHA
git checkout main
git branch -D claude/p5-branding-marketing-sales-rebrand

# The isolated D: checkout is safe to delete after that — its ownership
# is exclusive to this rebrand run.
```

### 1.3 Discard only the LAST commit(s)

If a specific commit in the stack is defective:

```
# Show recent commits
git log --oneline -10

# Undo the last N commits, keeping the changes UNSTAGED for review
git reset HEAD~N

# Or drop the changes entirely
git reset --hard HEAD~N
```

The commit stack is intentionally scoped one-responsibility-per-commit so
individual commits can be reverted with `git revert <sha>` without
disturbing the others.

### 1.4 Rebuild artifacts after a partial rollback

Every artifact in `artifacts/` is regenerated deterministically by:

```
C:/Python314/python.exe scripts/baseline_snapshot.py
C:/Python314/python.exe scripts/build_routes_artifacts.py
C:/Python314/python.exe scripts/write_vercel_and_sitemap.py
C:/Python314/python.exe scripts/verify_integration_preservation.py
C:/Python314/python.exe scripts/run_tests.py
```

`baseline-routes.json` is PINNED and is only regenerated if it is deleted
first — this prevents drift after the sitemap is rewritten.

## 2. Future production rollback (only when a future phase deploys this)

**Preconditions before this section applies:**
- A separate phase / dispatcher has been authorized to deploy this branch.
- That deploy has actually shipped to production (`www.revelationagency.com`
  serves the rebrand).
- A production defect has been observed OR the operator wants to revert.

### 2.1 Primary rollback — promote the last known-good Vercel deployment

The known-good production deployment at packet preparation was:

- Vercel scope: `connect-9983s-projects`
- Vercel project: `revelationagency-com`
- Deployment ID: **`dpl_7XJxEcwMPadne4REF5pzP3hyVQ69`**
- Deployment SHA: `4a0b076c37189216a263dfab5c481464cf251a96`
- Aligned primary alias: `https://www.revelationagency.com/`

Promotion procedure (executed by the authorized deploy lane, not by this
editor):

```
# 1. Confirm the target deployment is still present in Vercel and healthy
vercel inspect dpl_7XJxEcwMPadne4REF5pzP3hyVQ69 --scope connect-9983s-projects

# 2. Promote it to production
vercel promote dpl_7XJxEcwMPadne4REF5pzP3hyVQ69 --scope connect-9983s-projects

# 3. Verify aliases
vercel alias ls --scope connect-9983s-projects | grep revelationagency
```

### 2.2 Post-rollback verification checklist

Run these against the LIVE site after promotion:

- [ ] `https://www.revelationagency.com/` returns 200 and shows pre-rebrand
      Systems / Creative / Marketing homepage
- [ ] `https://revelationagency.com/` 301s to `https://www.revelationagency.com/`
- [ ] Canonical tag on `/` reads `https://www.revelationagency.com/`
- [ ] `robots.txt` accessible, sitemap URL matches
- [ ] `sitemap.xml` returns 200 and matches base-SHA content
- [ ] A representative legacy 301 still resolves — e.g.
      `curl -I https://www.revelationagency.com/services/creative/branding.html`
      hits the pre-rebrand behavior
- [ ] Homepage contact form POST target is byte-identical to the base-SHA
      configuration (webhook URL sha256 unchanged)
- [ ] Booking iframe embed unchanged
- [ ] Chat widget loads
- [ ] `mailto:connect@revelationagency.com` and `tel:+15592017039` links present
- [ ] Custom 404 renders on an unknown URL

### 2.3 Do NOT use DNS as the first rollback mechanism

The `www.revelationagency.com` and apex `revelationagency.com` records
remain unchanged for this entire packet. DNS is the last-resort rollback
mechanism, not the first. Vercel deployment promotion is faster,
reversible in seconds, and does not touch the DNS provider.

## 3. Configuration rollback (analytics / forms — deferred)

This rebrand does not change any production form endpoint, chat widget
ID, GHL webhook, or analytics measurement ID. The event layer added at
`assets/js/analytics-events.js` is inert (no network destination).

If a FUTURE phase configures a real analytics destination or edits any of
those endpoint contracts, that phase must:

- version the previous configuration in a separately-committed rollback
  file (`artifacts/config-rollback-<date>.json`),
- publish a live read-back checklist,
- and store the swap procedure alongside this rollback doc.

Nothing in the current packet has that footprint, so nothing extra is
required today.

## 4. What NEVER to do during rollback

- Do NOT force-push to `main`.
- Do NOT reset the base SHA on the remote repository.
- Do NOT delete artifacts that document the migration analysis, even if
  the rebrand itself is discarded.
- Do NOT clean or reset the other desktop checkouts
  (`C:/Users/blain/Desktop/Revelation Command Center/…`) or the Reviii
  Portal checkout. They are outside this rebrand's scope.
- Do NOT change DNS as a first response to a production defect.

## 5. Attestation

At the time of writing, no rollback has been executed. The rebrand is a
locally committed candidate on the isolated feature branch. The
content-parent SHA (parent of the current repair commit written by the
pillar-nav/footer repair pass) is
`de7493479904baa58e34b8d7b55c9d719a443f91`; the final HEAD SHA of the
branch is discoverable with `git rev-parse HEAD` (it is intentionally
not self-referenced inside the commit body). The last known-good
production deployment `dpl_7XJxEcwMPadne4REF5pzP3hyVQ69` at base SHA
`4a0b076c37189216a263dfab5c481464cf251a96` is untouched.

Prior editions of this file quoted a self-referential final SHA
(`ecc5d0e…`) that pre-dated later commits; that value has been retired
in favour of the content-parent + read-back framing above.
