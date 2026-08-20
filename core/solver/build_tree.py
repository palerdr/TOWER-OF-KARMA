from core.solver.primitives import (
    Action,
    GameState,
    InformationState,
    apply,
    current_actor,
    information_state,
    initial_state,
    legal_actions,
    terminal_returns,
)
from core.solver.tree import Edge, GameTree, TreeNode


def build_tree(horizon: int) -> GameTree:

    nodes: list[TreeNode | None] = []
    information_nodes: dict[InformationState, list[int]] = {}
    remembered_sequences: dict[InformationState, tuple[Action, ...]] = {}
    information_actions: dict[InformationState, tuple[Action, ...]] = {}

    def visit(
        state: GameState,
        parent_id: int | None,
        incoming_action: Action | None,
        player_history: tuple[tuple[Action, ...], tuple[Action, ...]],
    ) -> int:
        node_id = len(nodes)
        nodes.append(None)
        actor = current_actor(state)

        if actor is None:
            # base case if there is no actor it is Terminal

            nodes[node_id] = TreeNode(
                state=state,
                parent_id=parent_id,
                incoming_action=incoming_action,
                actor=None,
                information_set=None,
                edges=(),
                returns=terminal_returns(state),
            )
            return node_id

        else:
            # psuedocode
            # get info,actions
            # for action in actions
            # child_id is visit that next node of the tree
            # nodes[node_id] = TreeNode of the new tree

            info = information_state(state, actor)
            actions = legal_actions(state)
            # all nodes in the IS must offer identical actions
            previous_actions = information_actions.setdefault(info, actions)
            if previous_actions != actions:
                raise RuntimeError(
                    f"inconsistent legal actions inside information set {info!r}"
                )

            own_history = player_history[actor]
            previous_history = remembered_sequences.setdefault(info, own_history)
            if previous_history != own_history:
                raise RuntimeError(
                    f"perfect-recall violation at information set {info!r}"
                )

            information_nodes.setdefault(info, []).append(node_id)

            edges: list[Edge] = []
            for action in actions:
                next_histories = [player_history[0], player_history[1]]
                next_histories[actor] = own_history + (action,)

                child_id = visit(
                    apply(state, action),
                    parent_id=node_id,
                    incoming_action=action,
                    player_history=(next_histories[0], next_histories[1]),
                )
                edges.append(Edge(action, child_id))

            nodes[node_id] = TreeNode(
                state=state,
                parent_id=parent_id,
                incoming_action=incoming_action,
                actor=actor,
                information_set=info,
                edges=tuple(edges),
                returns=None,
            )
        return node_id

    root_id = visit(
        initial_state(horizon),
        parent_id=None,
        incoming_action=None,
        player_history=((), ()),
    )

    if any(node is None for node in nodes):
        raise RuntimeError("tree contains unfinished node palceholders")

    return GameTree(
        root_id=root_id,
        nodes=tuple(node for node in nodes if node is not None),
        information_sets={
            info: tuple(node_ids) for info, node_ids in information_nodes.items()
        },
    )


if __name__ == "__main__":
    build_tree(horizon=4)
