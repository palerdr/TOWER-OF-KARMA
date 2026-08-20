from dataclasses import dataclass

from src.solver.primitives import (
    Action,
    GameState,
    InformationState,
    Player,
)

kNodes = 10111
kEdges = 10110
kLeaves = 9100
kP0Wins = 100
kP1Wins = 900
kDraws = 8100
kInformationSets = 200
kP0InformationSets = 11
kP1InformationSets = 189


@dataclass(frozen=True, slots=True)
class Edge:
    action: Action
    child_id: int


@dataclass(frozen=True, slots=True)
class TreeNode:
    state: GameState
    parent_id: int | None
    incoming_action: Action | None
    actor: Player | None
    information_set: InformationState | None
    edges: tuple[Edge, ...]
    returns: tuple[int, int] | None


@dataclass(frozen=True, slots=True)
class GameTree:
    root_id: int
    nodes: tuple[TreeNode, ...]
    information_sets: dict[InformationState, tuple[int, ...]]
