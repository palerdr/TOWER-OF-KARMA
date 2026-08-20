# Pure Dotty solver

**Mechanical authority:** [`RULES.md`](RULES.md)
**Target:** complete solution of `D_K`, beginning with `K = 1`

## Claim

For a fixed `K`, solve the complete two-player zero-sum extensive-form game over
strategic hidden bead choices and all legal Dotty histories. Do not assign
Baku-like or Suteguma-like personalities: optimal behavior is the equilibrium
behavioral strategy at each information set.

## Primary solver

Generate the extensive form and solve its sequence-form primal and dual linear
programs. Sequence form preserves information sets and perfect recall without
enumerating complete contingent normal-form strategies.

Required engine boundary:

```text
initial_state(K)
current_actor(state)
legal_actions(state)
apply(state, action)
information_state(state, player)
terminal_returns(state)
```

The solver may optimize representation but may not reproduce or alter rules.

## Certification

For every solved profile, independently compute exact information-set-consistent
best responses and the saddle gap:

```text
max_response_value_against_P1 - min_response_value_against_P0
```

A profile is certified when:

- sequence-flow, probability, and legality residuals pass;
- primal and dual values agree;
- the independently computed saddle gap is at most `1e-6`.

“Exact” means complete traversal of the frozen model with this numerical
certificate. Literal rational arithmetic is optional because rational game data
guarantees that a rational equilibrium exists.

## Independent reference

Implement alternating exact-traversal CFR+ after the LP solver. CFR+ must
converge toward the LP value and declining exploitability on `D_1` and `D_2`.
Finite CFR+ output is approximate and must never be labeled exact without the
same best-response certificate.

MCCFR, neural policies, and state abstraction are out of scope until complete
tree measurements show they are necessary.

## Choosing one optimal behavior

Zero-sum games can have many equilibrium strategies. A linear program normally
returns an arbitrary sparse vertex, so two correct solvers may produce visibly
different policies with the same value and exploitability.

Use this two-stage selection:

1. Solve for the equilibrium value `v` and each player's complete set of
   security-optimal realization plans.
2. Within that optimal set, choose the realization plan with maximum dilated
   entropy, subject to retaining value `v` within the certification tolerance.

In behavioral terms, entropy at information set `I` is:

```text
H(I) = -sum_a sigma(a | I) * log(sigma(a | I))
```

Dilated entropy weights this by the player's probability of reaching `I` and
expresses the result in sequence-form realization variables. It selects the
most spread-out strategy among strategies that remain fully optimal. It does
not trade away game value, model mistakes, or claim to imitate a character.

Convert the selected realization plan `r` back to behavior by:

```text
sigma(a | I) = r(sequence_to_I_then_a) / r(sequence_to_I)
```

Maximum entropy does not determine actions at zero-reach information sets. For
an arena policy that must act everywhere, solve a documented perturbed game with
a small minimum probability on every legal action, then decrease the perturbation
and verify that values and on-path behavior stabilize.

Publish both the raw equilibrium certificate and the selected representative.
The entropy-selected policy is a reproducible convention, not a stronger
equilibrium claim.

## Scaling order

Solve and certify in order:

```text
D_1 -> D_2 -> D_3
```

A deepest all-miss branch multiplies by `9 * 9 = 81` per turn for each hidden
bead pair. Measure tree nodes, information sets, sequences, matrix nonzeros,
memory, and solve time at every rung before adding compression or Rust.
