from dataclasses import dataclass, replace
from enum import Enum, IntEnum, auto


class Player(IntEnum):
    P0 = 0
    P1 = 1


@dataclass(frozen=True, slots=True)
class ChooseBeads:
    count: int


@dataclass(frozen=True, slots=True)
class Guess:
    total: int


type Action = ChooseBeads | Guess


@dataclass(frozen=True, slots=True)
class Miss:
    player: Player
    total: int


class Phase(Enum):
    CHOOSE_P0 = auto()
    CHOOSE_P1 = auto()
    GUESS_P0 = auto()
    GUESS_P1 = auto()
    TERMINAL = auto()


@dataclass(frozen=True, slots=True)
class GameState:
    phase: Phase
    horizon: int
    turn: int
    beads: tuple[int | None, int | None]
    public_history: tuple[Miss, ...]
    winner: Player | None
    draw: bool


@dataclass(frozen=True, slots=True)
class InformationState:
    player: Player
    phase: Phase
    horizon: int
    turn: int
    own_beads: int | None
    public_history: tuple[Miss, ...]


# P1 must NOT observe P0 bead count when choosing


def initial_state(k: int) -> GameState:
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError(f"horizon must be a positive integer, got {k!r}")
    return GameState(
        phase=Phase.CHOOSE_P0,
        horizon=k,
        turn=0,
        beads=(None, None),
        public_history=(),
        winner=None,
        draw=False,
    )


def current_actor(state: GameState) -> Player | None:
    if state.phase == Phase.CHOOSE_P0 or state.phase == Phase.GUESS_P0:
        return Player.P0
    elif state.phase == Phase.CHOOSE_P1 or state.phase == Phase.GUESS_P1:
        return Player.P1
    else:
        return None


def legal_actions(state: GameState) -> tuple[ChooseBeads | Guess, ...]:
    actor = current_actor(state)
    if actor is None:
        return ()

    if state.phase in (Phase.CHOOSE_P0, Phase.CHOOSE_P1):
        return tuple(ChooseBeads(count) for count in range(1, 11))

    own_beads = state.beads[actor]
    if own_beads is None:
        raise ValueError(f"{actor.name} cannot guess before choosing beads")
    if not 1 <= own_beads <= 10:
        raise ValueError(f"bead count must be in 1..10, got {own_beads}")

    return tuple(Guess(total) for total in range(own_beads + 1, own_beads + 11))


def apply(state: GameState, action: Action) -> GameState:
    if state.phase is Phase.TERMINAL:
        raise ValueError("cannot apply an action to a terminal state")

    if isinstance(action, ChooseBeads):
        value = action.count
    elif isinstance(action, Guess):
        value = action.total
    else:
        raise ValueError(f"unsupported action type: {type(action).__name__}")
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"action value must be a literal integer, got {value!r}")

    if action not in legal_actions(state):
        raise ValueError(f"illegal action {action!r} during {state.phase.name}")

    if state.phase is Phase.CHOOSE_P0:
        if not isinstance(action, ChooseBeads):
            raise ValueError("P0 bead selection requires ChooseBeads")
        return replace(
            state,
            phase=Phase.CHOOSE_P1,
            beads=(action.count, None),
        )

    if state.phase is Phase.CHOOSE_P1:
        if not isinstance(action, ChooseBeads):
            raise ValueError("P1 bead selection requires ChooseBeads")
        if state.beads[Player.P0] is None:
            raise ValueError("P1 cannot choose before P0 has chosen beads")
        return replace(
            state,
            phase=Phase.GUESS_P0,
            turn=1,
            beads=(state.beads[Player.P0], action.count),
        )

    if not isinstance(action, Guess):
        raise ValueError("guess phase requires Guess")
    if not 1 <= state.turn <= state.horizon:
        raise ValueError(
            f"guess phase turn must be in 1..{state.horizon}, got {state.turn}"
        )
    p0_beads, p1_beads = state.beads
    if p0_beads is None or p1_beads is None:
        raise ValueError("both players must choose beads before guessing")

    actor = current_actor(state)
    assert actor is not None
    true_total = p0_beads + p1_beads
    if action.total == true_total:
        return replace(
            state,
            phase=Phase.TERMINAL,
            winner=actor,
            draw=False,
        )

    history = state.public_history + (Miss(actor, action.total),)
    if actor is Player.P0:
        return replace(
            state,
            phase=Phase.GUESS_P1,
            public_history=history,
        )

    if state.turn == state.horizon:
        return replace(
            state,
            phase=Phase.TERMINAL,
            public_history=history,
            winner=None,
            draw=True,
        )

    return replace(
        state,
        phase=Phase.GUESS_P0,
        turn=state.turn + 1,
        public_history=history,
    )


def information_state(state: GameState, player: Player) -> InformationState:
    return InformationState(
        player=player,
        phase=state.phase,
        horizon=state.horizon,
        turn=state.turn,
        own_beads=state.beads[0] if player == Player.P0 else state.beads[1],
        public_history=state.public_history,
    )


def terminal_returns(state: GameState) -> tuple[int, int]:
    if state.phase is not Phase.TERMINAL:
        raise ValueError("terminal returns require a terminal state")
    if state.draw:
        if state.winner is not None:
            raise ValueError("a terminal draw cannot also have a winner")
        return (0, 0)
    if state.winner is Player.P0:
        return (1, -1)
    if state.winner is Player.P1:
        return (-1, 1)
    raise ValueError("a terminal non-draw state must have a winner")
