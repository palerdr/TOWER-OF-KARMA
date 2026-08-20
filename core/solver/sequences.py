from dataclasses import dataclass

from core.solver.primitives import Action, InformationState, Player
from core.solver.tree import GameTree

type SequenceId = int
type InformationSetId = int


@dataclass(frozen=True, slots=True)
class Sequence:
    parent_id: SequenceId | None
    information_set_id: InformationSetId | None
    action: Action | None


@dataclass(frozen=True, slots=True)
class SequenceInformationSet:
    information_state: InformationState
    parent_sequence_id: SequenceId
    action_sequence_ids: tuple[SequenceId, ...]


@dataclass(frozen=True, slots=True)
class PlayerSequences:
    sequences: tuple[Sequence, ...]
    information_sets: tuple[SequenceInformationSet, ...]
    information_set_ids: dict[InformationState, InformationSetId]
    sequence_ids: dict[tuple[InformationSetId, Action], SequenceId]


@dataclass(frozen=True, slots=True)
class SequenceIndex:
    players: tuple[PlayerSequences, PlayerSequences]
    node_sequences: tuple[tuple[SequenceId, SequenceId], ...]


def build_sequence_index(tree: GameTree) -> SequenceIndex:
    sequences: list[list[Sequence]] = [
        [Sequence(parent_id=None, information_set_id=None, action=None)],
        [Sequence(parent_id=None, information_set_id=None, action=None)],
    ]
    information_sets: list[list[SequenceInformationSet]] = [[], []]
    information_set_ids: list[dict[InformationState, InformationSetId]] = [
        {},
        {},
    ]
    sequence_ids: list[dict[tuple[InformationSetId, Action], SequenceId]] = [
        {},
        {},
    ]
    node_sequences: list[tuple[SequenceId, SequenceId] | None] = [None] * len(
        tree.nodes
    )

    def visit(
        node_id: int,
        current_sequences: tuple[SequenceId, SequenceId],
    ) -> None:
        if not 0 <= node_id < len(tree.nodes):
            raise RuntimeError(f"tree references invalid node ID {node_id}")
        if node_sequences[node_id] is not None:
            raise RuntimeError(f"tree node {node_id} is reachable by multiple paths")
        node_sequences[node_id] = current_sequences

        node = tree.nodes[node_id]
        actor = node.actor
        if actor is None:
            return
        if node.information_set is None:
            raise RuntimeError(f"acting node {node_id} has no information set")

        player = int(actor)
        info = node.information_set
        if info.player is not actor:
            raise RuntimeError(
                f"information set player does not match actor at node {node_id}"
            )

        actions = tuple(edge.action for edge in node.edges)
        if len(set(actions)) != len(actions):
            raise RuntimeError(f"duplicate actions at node {node_id}")

        info_id = information_set_ids[player].get(info)
        if info_id is None:
            info_id = len(information_sets[player])
            information_set_ids[player][info] = info_id

            action_sequence_ids: list[SequenceId] = []
            for action in actions:
                sequence_id = len(sequences[player])
                sequences[player].append(
                    Sequence(
                        parent_id=current_sequences[player],
                        information_set_id=info_id,
                        action=action,
                    )
                )
                sequence_ids[player][(info_id, action)] = sequence_id
                action_sequence_ids.append(sequence_id)

            information_sets[player].append(
                SequenceInformationSet(
                    information_state=info,
                    parent_sequence_id=current_sequences[player],
                    action_sequence_ids=tuple(action_sequence_ids),
                )
            )
        else:
            sequence_info = information_sets[player][info_id]
            if sequence_info.parent_sequence_id != current_sequences[player]:
                raise RuntimeError(
                    f"perfect-recall violation at information set {info!r}"
                )
            previous_actions = tuple(
                sequences[player][sequence_id].action
                for sequence_id in sequence_info.action_sequence_ids
            )
            if previous_actions != actions:
                raise RuntimeError(f"inconsistent actions at information set {info!r}")

        for edge in node.edges:
            child_sequence_id = sequence_ids[player][(info_id, edge.action)]
            child_sequences = list(current_sequences)
            child_sequences[player] = child_sequence_id
            visit(
                edge.child_id,
                (child_sequences[Player.P0], child_sequences[Player.P1]),
            )

    if not 0 <= tree.root_id < len(tree.nodes):
        raise ValueError(f"invalid root node ID {tree.root_id}")
    visit(tree.root_id, (0, 0))

    if any(sequence_pair is None for sequence_pair in node_sequences):
        raise RuntimeError("tree contains nodes unreachable from its root")

    return SequenceIndex(
        players=(
            PlayerSequences(
                sequences=tuple(sequences[Player.P0]),
                information_sets=tuple(information_sets[Player.P0]),
                information_set_ids=information_set_ids[Player.P0],
                sequence_ids=sequence_ids[Player.P0],
            ),
            PlayerSequences(
                sequences=tuple(sequences[Player.P1]),
                information_sets=tuple(information_sets[Player.P1]),
                information_set_ids=information_set_ids[Player.P1],
                sequence_ids=sequence_ids[Player.P1],
            ),
        ),
        node_sequences=tuple(
            sequence_pair
            for sequence_pair in node_sequences
            if sequence_pair is not None
        ),
    )
