# Hooks

`.git/hooks/` is not version-controlled, so the pre-commit gate does not survive a fresh clone. Install with:

    cp curvature/scripts/hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

**The gate runs the documentation-claims audit and REFUSES the commit on failure.** It deliberately does not
run `verify.sh` (~30 min); the hook must be fast enough that nobody is tempted to disable it. Bypass a single
commit with `git commit --no-verify`.

**Known-fail control, run at install:** plant a wrong `silent_nulls` count in `CLAUDE.md`, attempt a commit,
and confirm it is refused with the reason printed; then confirm a clean commit succeeds. A hook that has only
ever been seen to pass has not been tested.
