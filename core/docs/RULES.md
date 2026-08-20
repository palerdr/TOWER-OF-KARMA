# Pure Dotty rules

**Status:** frozen core contract
**Evidence:** [`EVIDENCE.md`](EVIDENCE.md)

`D_K` is the numerical Dotty game with a fixed horizon of `K >= 1` turns. It
models winning Dotty, not winning Tower of Karma.

## Players and hidden commitment

There are two strategic players, `P0` and `P1`. Each secretly chooses a bead
count:

```text
x0, x1 in {1, ..., 10}
total = x0 + x1
```

The choices are simultaneous and hidden. An extensive-form implementation may
place `P0` first and `P1` second only if `P1`'s choice information set merges all
possible `P0` choices. Each player observes and remembers only their own count.

## Turn transition

`P0` guesses first in every turn.

1. The actor publicly announces a total `g`.
2. If `g == total`, that actor wins immediately.
3. Otherwise the guess and miss become public.
4. After a `P0` miss, `P1` guesses in the same turn.
5. After a `P1` miss, advance to the next turn.
6. If the `P1` miss completes turn `K`, the game is a draw.

For a player holding `x`, the legal action set is exactly:

```text
legal(x) = {x + 1, ..., x + 10}
```

Previously missed totals remain legal. No additional rationality-based
restriction is a rule.

## State and observation

Ground-truth state contains:

```text
(x0, x1, turn, actor, public_transcript, winner)
```

At a decision, player `i` observes only:

```text
(own_beads=xi, turn, actor, public_transcript)
```

The transcript is ordered and contains every prior guess and public miss. It is
not replaced by a set of surviving bead counts: different action histories can
carry different strategic information even when their hard logical support is
the same.

Policies must be keyed by information state, never by ground-truth state.

## Returns

Returns to `(P0, P1)` are:

```text
P0 guesses correctly first: (+1, -1)
P1 guesses correctly first: (-1, +1)
K turns end without a hit:  ( 0,  0)
```

This is a finite, two-player, zero-sum, perfect-recall extensive-form game with
imperfect information and no chance moves.

## Invariants

- Bead counts never change or become public.
- The true total is always in `2..20`.
- Every accepted guess is legal for the actor's private bead count.
- Only a correct guess or the second miss of turn `K` is terminal.
- A public miss proves only that the announced total is false; further belief
  changes come from the opponent's strategy.
- No observation reveals an opponent-private action or bead count.

## Excluded mechanics

The core excludes negotiated continuation, rooftop inputs, input rights,
helpers, violence, locations, third parties, speech, tells, answer timing,
transfusion physiology, and opponent personality. Adding any of them defines a
different formulation.
