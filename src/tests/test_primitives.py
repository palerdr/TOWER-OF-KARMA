from dataclasses import FrozenInstanceError, replace
import unittest

from src.solver.primitives import (
    ChooseBeads,
    GameState,
    Guess,
    Miss,
    Phase,
    Player,
    apply,
    current_actor,
    information_state,
    initial_state,
    legal_actions,
    terminal_returns,
)


def after_bead_choices(p0: int, p1: int, *, horizon: int = 1) -> GameState:
    state = apply(initial_state(horizon), ChooseBeads(p0))
    return apply(state, ChooseBeads(p1))


class InitialStateTests(unittest.TestCase):
    def test_phases_are_distinct(self) -> None:
        self.assertEqual(len(set(Phase)), 5)

    def test_initial_state(self) -> None:
        state = initial_state(3)
        self.assertIs(state.phase, Phase.CHOOSE_P0)
        self.assertEqual(state.horizon, 3)
        self.assertEqual(state.turn, 0)
        self.assertEqual(state.beads, (None, None))
        self.assertEqual(state.public_history, ())
        self.assertIsNone(state.winner)
        self.assertFalse(state.draw)

    def test_horizon_must_be_a_positive_literal_integer(self) -> None:
        for invalid in (0, -1, True, False, 1.5, "3", None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    initial_state(invalid)  # type: ignore[arg-type]

    def test_state_is_immutable(self) -> None:
        state = initial_state(1)
        with self.assertRaises(FrozenInstanceError):
            state.turn = 1  # type: ignore[misc]


class ActorAndLegalActionTests(unittest.TestCase):
    def test_current_actor_follows_phase(self) -> None:
        state = initial_state(1)
        self.assertIs(current_actor(state), Player.P0)

        state = apply(state, ChooseBeads(4))
        self.assertIs(current_actor(state), Player.P1)

        state = apply(state, ChooseBeads(7))
        self.assertIs(current_actor(state), Player.P0)

        state = apply(state, Guess(5))
        self.assertIs(current_actor(state), Player.P1)

        state = apply(state, Guess(8))
        self.assertIsNone(current_actor(state))

    def test_bead_selection_actions_are_one_through_ten(self) -> None:
        expected = tuple(ChooseBeads(count) for count in range(1, 11))
        state = initial_state(1)
        self.assertEqual(legal_actions(state), expected)
        self.assertEqual(legal_actions(apply(state, ChooseBeads(4))), expected)

    def test_guess_actions_depend_on_current_actors_beads(self) -> None:
        state = after_bead_choices(4, 7)
        self.assertEqual(
            legal_actions(state),
            tuple(Guess(total) for total in range(5, 15)),
        )

        state = apply(state, Guess(5))
        self.assertEqual(
            legal_actions(state),
            tuple(Guess(total) for total in range(8, 18)),
        )

    def test_terminal_state_has_no_legal_actions(self) -> None:
        state = after_bead_choices(1, 1)
        terminal = apply(state, Guess(2))
        self.assertEqual(legal_actions(terminal), ())


class InformationStateTests(unittest.TestCase):
    def test_p1_does_not_observe_p0_beads_while_choosing(self) -> None:
        observations = set()
        for p0_beads in range(1, 11):
            state = apply(initial_state(1), ChooseBeads(p0_beads))
            observations.add(information_state(state, Player.P1))

        self.assertEqual(len(observations), 1)
        observation = observations.pop()
        self.assertIs(observation.player, Player.P1)
        self.assertIs(observation.phase, Phase.CHOOSE_P1)
        self.assertIsNone(observation.own_beads)

    def test_guessing_player_observes_only_own_beads_and_public_history(self) -> None:
        state = after_bead_choices(4, 7, horizon=2)
        state = apply(state, Guess(5))

        p0_view = information_state(state, Player.P0)
        p1_view = information_state(state, Player.P1)
        self.assertEqual(p0_view.own_beads, 4)
        self.assertEqual(p1_view.own_beads, 7)
        self.assertEqual(p0_view.public_history, (Miss(Player.P0, 5),))
        self.assertEqual(p1_view.public_history, p0_view.public_history)

        alternate_p0_state = apply(after_bead_choices(4, 8, horizon=2), Guess(5))
        self.assertEqual(
            p0_view,
            information_state(alternate_p0_state, Player.P0),
        )
        self.assertEqual(
            information_state(after_bead_choices(4, 7), Player.P1),
            information_state(after_bead_choices(5, 7), Player.P1),
        )


class TransitionTests(unittest.TestCase):
    def test_hidden_bead_choice_transition(self) -> None:
        initial = initial_state(2)
        after_p0 = apply(initial, ChooseBeads(9))
        self.assertIs(after_p0.phase, Phase.CHOOSE_P1)
        self.assertEqual(after_p0.beads, (9, None))
        self.assertEqual(initial.beads, (None, None))

        after_p1 = apply(after_p0, ChooseBeads(8))
        self.assertIs(after_p1.phase, Phase.GUESS_P0)
        self.assertEqual(after_p1.turn, 1)
        self.assertEqual(after_p1.beads, (9, 8))

    def test_p0_miss_passes_to_p1_without_advancing_round(self) -> None:
        state = after_bead_choices(9, 9, horizon=2)
        next_state = apply(state, Guess(11))
        self.assertIs(next_state.phase, Phase.GUESS_P1)
        self.assertEqual(next_state.turn, 1)
        self.assertEqual(next_state.public_history, (Miss(Player.P0, 11),))

    def test_p1_miss_advances_round(self) -> None:
        state = after_bead_choices(9, 9, horizon=2)
        state = apply(state, Guess(11))
        state = apply(state, Guess(10))
        self.assertIs(state.phase, Phase.GUESS_P0)
        self.assertEqual(state.turn, 2)
        self.assertEqual(
            state.public_history,
            (Miss(Player.P0, 11), Miss(Player.P1, 10)),
        )

    def test_p0_correct_guess_wins_immediately(self) -> None:
        state = after_bead_choices(4, 7)
        terminal = apply(state, Guess(11))
        self.assertIs(terminal.phase, Phase.TERMINAL)
        self.assertIs(terminal.winner, Player.P0)
        self.assertFalse(terminal.draw)
        self.assertEqual(terminal.public_history, ())

    def test_p1_correct_guess_wins_after_p0_miss(self) -> None:
        state = after_bead_choices(4, 7)
        state = apply(state, Guess(5))
        terminal = apply(state, Guess(11))
        self.assertIs(terminal.phase, Phase.TERMINAL)
        self.assertIs(terminal.winner, Player.P1)
        self.assertFalse(terminal.draw)
        self.assertEqual(terminal.public_history, (Miss(Player.P0, 5),))

    def test_final_p1_miss_draws(self) -> None:
        state = after_bead_choices(9, 9)
        state = apply(state, Guess(11))
        terminal = apply(state, Guess(10))
        self.assertIs(terminal.phase, Phase.TERMINAL)
        self.assertIsNone(terminal.winner)
        self.assertTrue(terminal.draw)
        self.assertEqual(
            terminal.public_history,
            (Miss(Player.P0, 11), Miss(Player.P1, 10)),
        )

    def test_previously_missed_total_remains_legal(self) -> None:
        state = after_bead_choices(9, 9, horizon=2)
        state = apply(state, Guess(10))
        self.assertIn(Guess(10), legal_actions(state))
        state = apply(state, Guess(10))
        self.assertIn(Guess(10), legal_actions(state))

    def test_canonical_three_round_miss_transcript(self) -> None:
        state = after_bead_choices(9, 9, horizon=3)
        line = (
            (Player.P0, 11),
            (Player.P1, 10),
            (Player.P0, 12),
            (Player.P1, 14),
            (Player.P0, 13),
            (Player.P1, 15),
        )
        for _, total in line:
            state = apply(state, Guess(total))

        self.assertIs(state.phase, Phase.TERMINAL)
        self.assertTrue(state.draw)
        self.assertIsNone(state.winner)
        self.assertEqual(state.turn, 3)
        self.assertEqual(
            state.public_history,
            tuple(Miss(player, total) for player, total in line),
        )

    def test_all_bead_pairs_and_legal_guesses(self) -> None:
        for p0_beads in range(1, 11):
            for p1_beads in range(1, 11):
                with self.subTest(p0=p0_beads, p1=p1_beads):
                    p0_state = after_bead_choices(p0_beads, p1_beads)
                    true_total = p0_beads + p1_beads
                    p0_actions = legal_actions(p0_state)
                    self.assertEqual(len(p0_actions), 10)

                    for action in p0_actions:
                        result = apply(p0_state, action)
                        if action.total == true_total:
                            self.assertIs(result.winner, Player.P0)
                        else:
                            self.assertIs(result.phase, Phase.GUESS_P1)
                            self.assertEqual(
                                result.public_history[-1],
                                Miss(Player.P0, action.total),
                            )

                    p0_miss = next(
                        action for action in p0_actions if action.total != true_total
                    )
                    p1_state = apply(p0_state, p0_miss)
                    p1_actions = legal_actions(p1_state)
                    self.assertEqual(len(p1_actions), 10)

                    for action in p1_actions:
                        result = apply(p1_state, action)
                        if action.total == true_total:
                            self.assertIs(result.winner, Player.P1)
                            self.assertFalse(result.draw)
                        else:
                            self.assertTrue(result.draw)
                            self.assertIsNone(result.winner)

    def test_terminal_returns(self) -> None:
        p0_state = after_bead_choices(4, 7)
        p0_win = apply(p0_state, Guess(11))
        self.assertEqual(terminal_returns(p0_win), (1, -1))

        p1_state = apply(after_bead_choices(4, 7), Guess(5))
        p1_win = apply(p1_state, Guess(11))
        self.assertEqual(terminal_returns(p1_win), (-1, 1))

        draw_state = apply(p1_state, Guess(8))
        self.assertEqual(terminal_returns(draw_state), (0, 0))

    def test_terminal_returns_reject_live_or_inconsistent_states(self) -> None:
        with self.assertRaises(ValueError):
            terminal_returns(initial_state(1))

        malformed_draw = replace(
            after_bead_choices(1, 1),
            phase=Phase.TERMINAL,
            winner=Player.P0,
            draw=True,
        )
        with self.assertRaises(ValueError):
            terminal_returns(malformed_draw)

        malformed_non_draw = replace(
            after_bead_choices(1, 1),
            phase=Phase.TERMINAL,
            winner=None,
            draw=False,
        )
        with self.assertRaises(ValueError):
            terminal_returns(malformed_non_draw)


class RejectionTests(unittest.TestCase):
    def test_illegal_bead_choices_are_rejected(self) -> None:
        state = initial_state(1)
        for action in (
            ChooseBeads(0),
            ChooseBeads(11),
            ChooseBeads(True),
            ChooseBeads(1.5),
            Guess(2),
        ):
            with self.subTest(action=action):
                with self.assertRaises(ValueError):
                    apply(state, action)  # type: ignore[arg-type]

    def test_illegal_guesses_and_action_types_are_rejected(self) -> None:
        state = after_bead_choices(4, 7)
        for action in (
            Guess(4),
            Guess(15),
            Guess(True),
            Guess(5.5),
            ChooseBeads(5),
            object(),
        ):
            with self.subTest(action=action):
                with self.assertRaises(ValueError):
                    apply(state, action)  # type: ignore[arg-type]

    def test_terminal_state_rejects_actions(self) -> None:
        state = after_bead_choices(1, 1)
        terminal = apply(state, Guess(2))
        with self.assertRaises(ValueError):
            apply(terminal, Guess(2))

    def test_guess_phase_requires_current_players_beads(self) -> None:
        malformed = replace(
            initial_state(1),
            phase=Phase.GUESS_P0,
            turn=1,
        )
        with self.assertRaises(ValueError):
            legal_actions(malformed)


if __name__ == "__main__":
    unittest.main()
