# Synchronized publishing

GitHub `VENGEAANCE/dcost-daily` main is the source of truth for site code.
The Full Charge redesign is merged. Do not copy an older operations directory
over current source. There are no automatic GitHub Actions deployments here.

## Content refresh

1. Back up the operations workspace and latest production `data/*.json` first.
2. Fetch main into a Git checkout. Reconcile any uncommitted work without reset,
   deletion or blind overwrite. Preserve newer digest dates and reviewed data.
3. Update content from current main. Regenerate SEO pages through their generators
   when input prices/vehicle data change; regenerate the sitemap after digests.
4. Commit the data and generated outputs on a branch and open a PR. Include
   desktop 1280/mobile 390 screenshots for UI changes. Do not merge without Jared.
5. After Jared directly approves the exact release, use the canonical publisher:

```sh
bash scripts/deploy.sh --approved-commit FULL_APPROVED_HEAD_SHA
```

The script stages only tracked public files from the approved clean commit,
requires latest GitHub main to be included, checks routes, and records commit,
digest date/count and asset SHA-256 hashes in `/release.json`. Credentials must
already be supplied by the environment or Wrangler login; never print them.
Wrangler must be installed in the publishing environment. This script does not
install software or generate content during release. It always targets the
existing Cloudflare Pages `dcost-daily` production project.

Do not deploy directly from another folder or use the former fixed
`/workspace/dcost-daily-stage` upload. Updating this repository does not update
an external bot's copy or scheduler: its owner must fetch this script and amend
the actual routine. Until reconciled, that routine must not publish competing
uploads. Existing production approval gates remain in force.

## Verification and recovery

Compare `/release.json` and live asset hashes with the staged release. Check
today's digest, calculator, archive, newsletter, a generated page and custom 404.
Never roll back newer live JSON blindly. Recover design from reviewed Git source
and preserve the newest content in a new reviewed commit. Cloudflare deployment
IDs identify old releases, but older releases may contain stale data.
