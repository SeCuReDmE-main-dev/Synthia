# Synthia public site

This is the canonical static source for <https://synthia.securedme.ca/>.

| Surface | Canonical location |
| --- | --- |
| Release base branch | `new/synthia-public-landing` |
| Public source directory | `web/landing/` |
| cPanel document root | `/home/xacm7978/synthia.securedme.ca/` |
| Deployment configuration | repository-root `.cpanel.yml` |

The responsive worktree may use a child branch during review. Merge the reviewed
change into `new/synthia-public-landing` before cPanel deploys it. `.cpanel.yml`
does not select a Git branch; it copies the checked-out release branch directly
from `web/landing/` to the document root. `dist/synthia-public/` is legacy
guidance and is not part of the deployment path.

## Public shell contract

All three public routes load only local Synthia assets:

- `index.html` — Synthia overview;
- `trace-lab.html` — public-safe candidate-memory trace;
- `neutrosophic-lexicon.html` — source-linked lexicon surface;
- `assets/synthia-public-shell.<sha16>.css` and `.js` — shared responsive shell;
- `assets/synthia-public-shell.manifest.json` — version and SHA-256 verification record.

The shell owns the compact navigation and the single fixed action dock. It has
no remote support-widget, payment-widget, API-key, or server-side dependency.
The dock provides theme and access controls only; it is not a payment prompt.

When the shell changes, run the deterministic publisher before review:

```powershell
python scripts/publish_public_shell_assets.py --write
python scripts/publish_public_shell_assets.py --check
```

It derives the first 16 filename characters and the manifest SHA-256 values
from the bytes on disk, then updates all three HTML references and the cPanel
asset copy lines. `--check` fails on a stale fingerprint, route reference, or
deploy order. Deploy the new hashed assets before the HTML files so cached pages
never reference an unavailable asset.

## Deployment check

1. Confirm the checked-out cPanel Git repository is on the reviewed
   `new/synthia-public-landing` release line.
2. Run the repository tests and the static link/asset check before deployment.
3. Trigger the cPanel deployment defined by `.cpanel.yml`; it publishes assets
   and JSON before the three HTML entry points.
4. Fetch the three public routes and both `assets/synthia-public-shell.*`
   files. Compare their SHA-256 values with the manifest after cache/CDN purge.
5. Check at phone and desktop widths that the menu opens, the action dock has no
   competing fixed control, and the Trace Lab CTA remains reachable.

The site presents Synthia as an educational research project for
context-preserving lexicon intelligence, biology classification, source
traceability, taxonomy memory, and uncertainty-aware classification. It does
not present Synthia as a production scientific authority, medical tool,
environmental deployment system, drone-control platform, or formal
nomenclatural authority.
