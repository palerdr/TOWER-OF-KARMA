# Pure Dotty evidence ledger

This ledger separates depicted rules and events from interpretations and solver
assumptions. `RULES.md` may depend only on entries marked **rule**, **event**, or
**model**. Interpretations belong in analysis or opponent models.

## Evidence classes

- **rule** — presented as a mechanical rule of the manga game;
- **event** — an action or result depicted in the canonical match;
- **interpretation** — a proposed explanation of a player's intent;
- **ambiguous** — the available sources do not settle the rule;
- **model** — a deliberate rule of the pure solver, not a canon claim.

The linked articles are secondary commentary that cites manga volumes and
chapters. A later primary-source audit may strengthen or correct this ledger.

## Mechanical evidence

| ID | Class | Claim | Source |
|---|---|---|---|
| E-BEADS | rule | Each principal secretly takes 1–10 beads; their sum is in 2–20. | [overview], [S1] |
| E-DOTTY-ORDER | rule | A Dotty turn is sequential: the first player guesses, then the second if the first misses. Two misses end the turn. | [overview] |
| E-DOTTY-LEGAL | rule | A guess must be possible given the guesser's own beads: for own count `x`, legal totals are `x+1..x+10`. | [S1], [overview] |
| E-DOTTY-RESULT | rule | A correct guess releases the guesser and subjects the opponent to the full blood penalty. Dotty does not itself transfer the main wager. | [overview] |
| E-DOTTY-TIME | rule | Each answer has ten minutes; timeout triggers a partial blood penalty. | [overview] |
| E-PRIVATE | rule | Each player knows their own bead count, not the opponent's. Guesses and their results are observed by both Dotty players. | [S1], [overview] |
| E-GAMMA | ambiguous | It is unclear whether a total known false for reasons beyond the own-bead legality interval is formally forbidden. The article series analyzes the game without this extra rule. | [S1] |

The blood volumes and timing exist in canon but do not affect the first pure
solver once a correct guess is represented as terminal victory and delay is
removed.

## Canonical events

| ID | Class | Claim | Source |
|---|---|---|---|
| E-COUNTS-99 | event | Baku and Suteguma each held 9 beads; the true total was 18. | [S1] |
| E-LINE | event | The Dotty guesses were `11/10`, `12/14`, and `13/15`; all missed. | [S1] |
| E-FIRST | event | Baku acted first and Suteguma second in each depicted turn. | [S1] |
| E-TERMINALS | event | Hyougo entered 8 and missed, Suteguma entered 16 and missed, and Marco entered 18 correctly. | [S1], [S10] |
| E-EIGHT-BLUFF | event | The rooftop 8 was a deliberate impossible input used to conceal Suteguma's true count. Rooftop inputs do not inherit Dotty legality. | [S3], [S4] |

## Strategic interpretations

These motivate later experiments but are not engine rules.

| ID | Class | Claim | Source |
|---|---|---|---|
| I-OPEN-11 | interpretation | Baku chose 11 because it is legal for every possible own count and therefore leaks the least information. | [S2] |
| I-OPEN-10 | interpretation | Suteguma chose 10 partly to support the later 8-bluff while limiting early leakage. | [S2] |
| I-BAKU-12 | interpretation | Baku chose 12 to conceal his suspicion of the bluff while minimizing information leakage. | [S7] |
| I-SUTE-14 | interpretation | Suteguma chose 14 because larger guesses risked exposing the 8-bluff and 14 encouraged a false commitment. | [S8] |
| I-BAKU-13 | interpretation | Baku's spoken and Dotty 13 was a counter-bluff intended to imply that he held 6 or 7. | [S9] |
| I-TOWER-PLAN | interpretation | Baku may also have been manipulating the order of terminal use and the conflict among outside factions. | [S5], [S6] |

Articles S5–S10 explicitly warn that parts of their intent reconstruction are
speculative. None of these interpretations constrain optimal core behavior.

## Frozen model assumptions

| ID | Class | Decision |
|---|---|---|
| M-HORIZON | model | `D_K` has an externally fixed positive number `K` of turns. |
| M-FIRST | model | Player 0 is the first guesser in every turn. |
| M-BETA-ONLY | model | Only the own-bead legality interval is enforced; the ambiguous gamma rule is absent. |
| M-REPEAT | model | A previously missed total may be guessed again. |
| M-PAYOFF | model | First correct guess wins `+1`; the opponent receives `-1`; no correct guess by turn `K` is a draw worth `0`. |
| M-NO-TIME | model | Timing and blood quantities are omitted because they do not change transitions before a correct guess in this formulation. |

## Sources

[overview]: https://www.wikizero.org/wiki/ja/%E5%98%98%E5%96%B0%E3%81%84
[S1]: https://note.com/krkrkr/n/nf450fcf6da59
[S2]: https://note.com/krkrkr/n/nbb416b6caa41
[S3]: https://note.com/krkrkr/n/n25dcf0fa5ac3
[S4]: https://note.com/krkrkr/n/n0e9ede5edfe0
[S5]: https://note.com/krkrkr/n/nb641c08e928a
[S6]: https://note.com/krkrkr/n/n3134a0a4dd26
[S7]: https://note.com/krkrkr/n/n997f55c23f66
[S8]: https://note.com/krkrkr/n/n47b5386e4e3a
[S9]: https://note.com/krkrkr/n/n889b31fb656c
[S10]: https://note.com/krkrkr/n/nfdb44ae3ec62
