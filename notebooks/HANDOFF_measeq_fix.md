
### Round 7 addendum: container verified on Biowulf (2026-08-19)

The insomnia cross-check (25 iters, --cpus 14) matches the laptop
BITWISE: all four combos fail at the same pair/level/reason, parametric
p's identical to the last floating-point digit across osx-arm64 and
linux-64, and every permutation-gated abandonment point coincides.
Field fixes folded in along the way: explicit -B binds (lab shares are
not auto-bound; unbound paths appear as empty dirs), no pixi at runtime
(baked activate.sh; NFS-home cache writes + no network on compute
nodes), bash-wrapped runscript (%runscript runs under /bin/sh),
LC_ALL=C.UTF-8, and --threads-per-core=1 with --cpus-per-task=14 (14
physical cores for the 14 pinned workers). Incidental demonstration of
the worker-count rule: at 25 iters the borderline insomnia combo passes
with 12 workers but fails with 14 -- worker count changes the
permutation draws, hence the hard --cpus 14 pin.
