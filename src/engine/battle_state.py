"""
Módulo de estado de batalla para BattleRPG AI.

Mantiene el estado completo de una batalla incluyendo equipos, turno actual,
historial de acciones y condiciones de victoria.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from src.core.team import Team
from src.core.character import Character
from src.core.stats import ActionType


class BattlePhase(Enum):
    """
    Fases de una batalla.

    Define el estado actual del combate.
    """
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


@dataclass
class ActionRecord:
    """
    Registro de una acción realizada en combate.

    Attributes:
        turn_number: Número del turno
        player_id: ID del jugador que realizó la acción
        character_name: Nombre del personaje que actuó
        action_type: Tipo de acción (ATTACK, USE_ABILITY, SWITCH)
        target_name: Nombre del objetivo (si aplica)
        damage_dealt: Daño infligido
        ability_used: Nombre de la habilidad usada (si aplica)
        result_description: Descripción del resultado
    """
    turn_number: int
    player_id: int
    character_name: str
    action_type: ActionType
    target_name: Optional[str] = None
    damage_dealt: int = 0
    ability_used: Optional[str] = None
    result_description: str = ""


class BattleState:
    """
    Mantiene el estado completo de una batalla.

    Coordina los equipos, turnos, historial y determina el ganador.

    Attributes:
        team1: Primer equipo
        team2: Segundo equipo
        current_turn: Número del turno actual
        phase: Fase actual de la batalla
        winner_id: ID del equipo ganador (None si no ha terminado)
        action_history: Historial de todas las acciones realizadas
        max_turns: Límite máximo de turnos (para evitar batallas infinitas)

    Examples:
        >>> team1 = Team([char1, char2, char3])
        >>> team2 = Team([char4, char5, char6])
        >>> battle = BattleState(team1, team2)
        >>> battle.start_battle()
        >>> battle.phase
        <BattlePhase.IN_PROGRESS: 'in_progress'>
    """

    def __init__(
        self,
        team1: Team,
        team2: Team,
        max_turns: int = 100
    ) -> None:
        """
        Inicializa el estado de batalla.

        Args:
            team1: Primer equipo (jugador 1)
            team2: Segundo equipo (jugador 2)
            max_turns: Límite máximo de turnos
        """
        self.team1 = team1
        self.team2 = team2
        self.current_turn = 0
        self.phase = BattlePhase.NOT_STARTED
        self.winner_id: Optional[int] = None
        self.action_history: List[ActionRecord] = []
        self.max_turns = max_turns

    def start_battle(self) -> None:
        """
        Inicia la batalla.

        Cambia la fase a IN_PROGRESS y prepara los equipos.
        """
        if self.phase != BattlePhase.NOT_STARTED:
            raise RuntimeError("La batalla ya ha sido iniciada")

        self.phase = BattlePhase.IN_PROGRESS
        self.current_turn = 1

    def end_battle(self, winner_id: int) -> None:
        """
        Termina la batalla y declara un ganador.

        Args:
            winner_id: ID del equipo ganador (1 o 2)
        """
        if self.phase == BattlePhase.FINISHED:
            return

        self.phase = BattlePhase.FINISHED
        self.winner_id = winner_id

    def advance_turn(self) -> None:
        """
        Avanza al siguiente turno.

        Incrementa el contador de turnos y procesa efectos de inicio de turno.
        """
        if self.phase != BattlePhase.IN_PROGRESS:
            raise RuntimeError("La batalla no está en progreso")

        self.current_turn += 1

        # Verificar si se alcanzó el límite de turnos
        if self.current_turn > self.max_turns:
            # Empate o victoria por HP total
            self._resolve_max_turns()

    def _resolve_max_turns(self) -> None:
        """
        Resuelve la batalla cuando se alcanza el máximo de turnos.

        Gana el equipo con mayor HP total.
        """
        team1_hp = self.team1.get_total_hp()
        team2_hp = self.team2.get_total_hp()

        if team1_hp > team2_hp:
            self.end_battle(winner_id=1)
        elif team2_hp > team1_hp:
            self.end_battle(winner_id=2)
        else:
            # Empate: gana el equipo 1 por defecto
            self.end_battle(winner_id=1)

    def get_team(self, player_id: int) -> Team:
        """
        Obtiene un equipo por ID de jugador.

        Args:
            player_id: ID del jugador (1 o 2)

        Returns:
            El equipo correspondiente

        Raises:
            ValueError: Si player_id no es 1 o 2
        """
        if player_id == 1:
            return self.team1
        elif player_id == 2:
            return self.team2
        else:
            raise ValueError(f"player_id debe ser 1 o 2, recibido: {player_id}")

    def get_opponent_team(self, player_id: int) -> Team:
        """
        Obtiene el equipo oponente.

        Args:
            player_id: ID del jugador (1 o 2)

        Returns:
            El equipo oponente
        """
        return self.get_team(3 - player_id)

    def record_action(
        self,
        player_id: int,
        character: Character,
        action_type: ActionType,
        target: Optional[Character] = None,
        damage_dealt: int = 0,
        ability_used: Optional[str] = None,
        result_description: str = ""
    ) -> None:
        """
        Registra una acción en el historial.

        Args:
            player_id: ID del jugador que actuó
            character: Personaje que realizó la acción
            action_type: Tipo de acción
            target: Objetivo de la acción (si aplica)
            damage_dealt: Daño infligido
            ability_used: Nombre de la habilidad usada
            result_description: Descripción del resultado
        """
        record = ActionRecord(
            turn_number=self.current_turn,
            player_id=player_id,
            character_name=character.name,
            action_type=action_type,
            target_name=target.name if target else None,
            damage_dealt=damage_dealt,
            ability_used=ability_used,
            result_description=result_description
        )
        self.action_history.append(record)

    def get_turn_actions(self, turn_number: int) -> List[ActionRecord]:
        """
        Obtiene todas las acciones de un turno específico.

        Args:
            turn_number: Número del turno

        Returns:
            Lista de acciones realizadas en ese turno
        """
        return [
            action for action in self.action_history
            if action.turn_number == turn_number
        ]

    def get_player_actions(self, player_id: int) -> List[ActionRecord]:
        """
        Obtiene todas las acciones de un jugador.

        Args:
            player_id: ID del jugador

        Returns:
            Lista de acciones realizadas por ese jugador
        """
        return [
            action for action in self.action_history
            if action.player_id == player_id
        ]

    def get_battle_summary(self) -> Dict[str, Any]:
        """
        Genera un resumen de la batalla.

        Returns:
            Diccionario con estadísticas y resultados
        """
        return {
            "total_turns": self.current_turn,
            "winner_id": self.winner_id,
            "team1_final_hp": self.team1.get_total_hp(),
            "team2_final_hp": self.team2.get_total_hp(),
            "team1_alive": self.team1.get_alive_count(),
            "team2_alive": self.team2.get_alive_count(),
            "total_actions": len(self.action_history),
            "phase": self.phase.value
        }

    def is_finished(self) -> bool:
        """
        Verifica si la batalla ha terminado.

        Returns:
            True si la fase es FINISHED
        """
        return self.phase == BattlePhase.FINISHED

    def is_in_progress(self) -> bool:
        """
        Verifica si la batalla está en progreso.

        Returns:
            True si la fase es IN_PROGRESS
        """
        return self.phase == BattlePhase.IN_PROGRESS

    def reset(self) -> None:
        """
        Resetea el estado de batalla para una nueva partida.

        NOTA: No resetea los equipos, solo el estado de batalla.
        """
        self.current_turn = 0
        self.phase = BattlePhase.NOT_STARTED
        self.winner_id = None
        self.action_history.clear()

    def __repr__(self) -> str:
        """Representación para debugging."""
        return (f"BattleState(Turn {self.current_turn}, "
                f"Phase: {self.phase.value}, "
                f"Winner: {self.winner_id})")

    def __str__(self) -> str:
        """Representación legible."""
        if self.phase == BattlePhase.NOT_STARTED:
            return "Battle not started"
        elif self.phase == BattlePhase.FINISHED:
            winner = f"Team {self.winner_id}" if self.winner_id else "Draw"
            return f"Battle finished - Winner: {winner} (Turn {self.current_turn})"
        else:
            return (f"Battle in progress - Turn {self.current_turn}\n"
                    f"Team 1: {self.team1.get_alive_count()}/3 alive\n"
                    f"Team 2: {self.team2.get_alive_count()}/3 alive")
