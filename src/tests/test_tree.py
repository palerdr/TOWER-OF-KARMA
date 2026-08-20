from collections import Counter
import unittest

from src.solver.build_tree import build_tree
from src.solver.primitives import Phase, Player, apply, legal_actions
from src.solver.tree import (
    kDraws,
    kEdges,
    kInformationSets,
    kLeaves,
    kNodes,
    kP0InformationSets,
    kP0Wins,
    kP1InformationSets,
    kP1Wins,
)


class D1TreeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tree = build_tree(1)

    def test_exact_d1_constants(self) -> None:
        terminals = [node for node in self.tree.nodes if node.returns is not None]
        returns = Counter(node.returns for node in terminals)
        information_sets_by_player = Counter(
            info.player for info in self.tree.information_sets
        )

        self.assertEqual(len(self.tree.nodes), kNodes)
        self.assertEqual(
            sum(len(node.edges) for node in self.tree.nodes),
            kEdges,
        )
        self.assertEqual(len(terminals), kLeaves)
        self.assertEqual(returns[(1, -1)], kP0Wins)
        self.assertEqual(returns[(-1, 1)], kP1Wins)
        self.assertEqual(returns[(0, 0)], kDraws)
        self.assertEqual(len(self.tree.information_sets), kInformationSets)
        self.assertEqual(
            information_sets_by_player[Player.P0],
            kP0InformationSets,
        )
        self.assertEqual(
            information_sets_by_player[Player.P1],
            kP1InformationSets,
        )

    def test_root_and_every_edge_are_well_formed(self) -> None:
        self.assertEqual(self.tree.root_id, 0)
        root = self.tree.nodes[self.tree.root_id]
        self.assertIsNone(root.parent_id)
        self.assertIsNone(root.incoming_action)

        for node_id, node in enumerate(self.tree.nodes):
            if node.actor is None:
                self.assertEqual(node.state.phase, Phase.TERMINAL)
                self.assertEqual(node.edges, ())
                self.assertIsNone(node.information_set)
                self.assertIsNotNone(node.returns)
                continue

            self.assertIsNone(node.returns)
            self.assertIsNotNone(node.information_set)
            self.assertEqual(
                tuple(edge.action for edge in node.edges),
                legal_actions(node.state),
            )

            for edge in node.edges:
                child = self.tree.nodes[edge.child_id]
                self.assertEqual(child.parent_id, node_id)
                self.assertEqual(child.incoming_action, edge.action)
                self.assertEqual(child.state, apply(node.state, edge.action))

    def test_information_sets_are_consistent(self) -> None:
        for info, node_ids in self.tree.information_sets.items():
            action_sets = {
                tuple(edge.action for edge in self.tree.nodes[node_id].edges)
                for node_id in node_ids
            }

            self.assertEqual(len(action_sets), 1)
            for node_id in node_ids:
                node = self.tree.nodes[node_id]
                self.assertEqual(node.actor, info.player)
                self.assertEqual(node.information_set, info)

    def test_p1_does_not_observe_p0_bead_choice(self) -> None:
        choose_p1_sets = [
            node_ids
            for info, node_ids in self.tree.information_sets.items()
            if info.phase is Phase.CHOOSE_P1
        ]

        self.assertEqual(len(choose_p1_sets), 1)
        self.assertEqual(len(choose_p1_sets[0]), 10)


if __name__ == "__main__":
    unittest.main()
