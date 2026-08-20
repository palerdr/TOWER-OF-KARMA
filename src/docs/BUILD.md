# Pure Dotty build contract

Build the smallest exact game first. Each phase must remain independently
testable and preserve [`RULES.md`](RULES.md).

## Target layout

```text
src/
  docs/
    EVIDENCE.md
    RULES.md
    SOLVER.md
    BUILD.md
  solver/
    primitives.py
    build_tree.py
    tree.py
    sequences.py
    constraints.py
    payoff.py
    solve.py
    best_response.py
    cfr_plus.py
    entropy.py
    cli.py
  tests/
  artifacts/       # generated, gitignored
  outputs/         # generated, gitignored
```

The Python engine is behavioral authority. A later Rust backend must consume
shared conformance vectors and prove parity rather than becoming a second rules
implementation.

## Build phases

### 1. Rules and inference

- immutable validated state and action types;
- legal-action and transition tests for all bead pairs;
- information-state noninterference tests;
- canonical `9/9` transcript replay;
- exhaustive hard-support inference checks.

### 2. Complete `D_1` tree

- deterministic tree generation;
- perfect-recall audit;
- sequence-form construction;
- fixed-policy evaluator and exact best response.

Gate: every history is reachable only through engine transitions, and no policy
key contains hidden opponent state.

### 3. Exact solve and certificate

- sequence-form primal and dual LPs;
- independent saddle-gap calculation;
- artifact manifest binding `K`, rules hash, action ordering, and solver
  tolerance;
- maximum-entropy representative selected only after certification.

Gate: `D_1` passes the `1e-6` certificate under reproducible builds.

### 4. Independent CFR+

- exact full-tree traversal;
- deterministic small-iteration tests;
- convergence against the LP value and best-response evaluator.

### 5. Scale deliberately

- repeat all gates for `D_2`, then `D_3`;
- profile before introducing compression, parallelism, or Rust;
- preserve the uncompressed lower rung as the correctness oracle.

## Validation interface

Once the package exists, keep these commands stable:

```powershell
uv run pytest src/tests -q
uv run python -m tok_core.cli solve --turns 1
uv run python -m tok_core.cli certify --turns 1
```

## Definition of done

A horizon is solved only when its engine, information audit, complete tree,
primal/dual solve, exact best responses, saddle-gap certificate, artifact
integrity checks, and independent CFR+ comparison all pass. A plausible
self-play curve alone is not a solution.
