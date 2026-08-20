import unittest

from core.solver.build_tree import build_tree
from core.solver.primitives import Player
from core.solver.sequences import Sequence, build_sequence_index


class D1SequenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tree = build_tree(1)
        cls.index = build_sequence_index(cls.tree)

    def test_exact_d1_counts(self) -> None:
        p0 = self.index.players[Player.P0]
        p1 = self.index.players[Player.P1]

        self.assertEqual(len(p0.sequences), 111)
        self.assertEqual(len(p1.sequences), 1_891)
        self.assertEqual(len(p0.information_sets), 11)
        self.assertEqual(len(p1.information_sets), 189)

    def test_each_player_has_empty_sequence_zero(self) -> None:
        empty = Sequence(parent_id=None, information_set_id=None, action=None)

        for player in Player:
            self.assertEqual(self.index.players[player].sequences[0], empty)

    def test_information_set_and_sequence_ids_are_dense(self) -> None:
        for player in Player:
            player_index = self.index.players[player]

            self.assertEqual(
                set(player_index.information_set_ids.values()),
                set(range(len(player_index.information_sets))),
            )
            self.assertEqual(
                set(player_index.sequence_ids.values()),
                set(range(1, len(player_index.sequences))),
            )

    def test_every_information_set_has_valid_sequence_extensions(self) -> None:
        for player in Player:
            player_index = self.index.players[player]

            for info_id, info in enumerate(player_index.information_sets):
                self.assertEqual(len(info.action_sequence_ids), 10)
                self.assertEqual(
                    player_index.information_set_ids[info.information_state],
                    info_id,
                )
                self.assertLess(
                    info.parent_sequence_id,
                    len(player_index.sequences),
                )

                for sequence_id in info.action_sequence_ids:
                    sequence = player_index.sequences[sequence_id]
                    self.assertEqual(sequence.parent_id, info.parent_sequence_id)
                    self.assertEqual(sequence.information_set_id, info_id)
                    self.assertIsNotNone(sequence.action)
                    self.assertEqual(
                        player_index.sequence_ids[(info_id, sequence.action)],
                        sequence_id,
                    )

    def test_all_members_of_an_information_set_reuse_sequences(self) -> None:
        for info, node_ids in self.tree.information_sets.items():
            player = info.player
            player_index = self.index.players[player]
            info_id = player_index.information_set_ids[info]
            sequence_info = player_index.information_sets[info_id]

            for node_id in node_ids:
                self.assertEqual(
                    self.index.node_sequences[node_id][player],
                    sequence_info.parent_sequence_id,
                )
                node = self.tree.nodes[node_id]
                self.assertEqual(
                    tuple(edge.action for edge in node.edges),
                    tuple(
                        player_index.sequences[sequence_id].action
                        for sequence_id in sequence_info.action_sequence_ids
                    ),
                )

    def test_edge_updates_only_the_actors_sequence(self) -> None:
        for node_id, node in enumerate(self.tree.nodes):
            if node.actor is None:
                continue

            actor = node.actor
            opponent = Player.P1 if actor is Player.P0 else Player.P0
            player_index = self.index.players[actor]
            info_id = player_index.information_set_ids[node.information_set]
            parent_sequences = self.index.node_sequences[node_id]

            for edge in node.edges:
                child_sequences = self.index.node_sequences[edge.child_id]
                self.assertEqual(
                    child_sequences[actor],
                    player_index.sequence_ids[(info_id, edge.action)],
                )
                self.assertEqual(
                    child_sequences[opponent],
                    parent_sequences[opponent],
                )

    def test_terminal_nodes_retain_both_players_final_sequences(self) -> None:
        for node_id, node in enumerate(self.tree.nodes):
            if node.actor is not None:
                continue

            p0_sequence, p1_sequence = self.index.node_sequences[node_id]
            self.assertNotEqual(p0_sequence, 0)
            self.assertNotEqual(p1_sequence, 0)


if __name__ == "__main__":
    unittest.main()
