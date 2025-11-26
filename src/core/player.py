"""
Módulo de jugadores para BattleRPG AI.

Define la interfaz base de jugadores y implementaciones básicas.
"""

import random
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from dataclasses import dataclass

from src.core.team import Team
from src.core.character import Character
from src.core.ability import Ability
from src.core.stats import ActionType


@dataclass
class PlayerAction:
    """
    Representa una acción decidida por un jugador.

    Attributes:
        action_type: Tipo de acción a realizar
        ability: Habilidad a usar (si action_type es USE_ABILITY)
        switch_target: Índice del personaje destino (si action_type es SWITCH)
    """
    action_type: ActionType
    ability: Optional[Ability] = None
    switch_target: Optional[int] = None


class Player(ABC):
    """
    Clase base abstracta para jugadores.

    Define la interfaz que todos los jugadores (humanos, IA, RL agents)
    deben implementar.

    Attributes:
        team: Equipo del jugador
        player_id: ID único del jugador (1 o 2)
        name: Nombre del jugador

    Examples:
        >>> # Los jugadores se implementan como subclases
        >>> class MyPlayer(Player):
        ...     def decide_action(self, opponent_team):
        ...         return PlayerAction(ActionType.ATTACK)
    """

    def __init__(
        self,
        team: Team,
        player_id: int,
        name: str = "Player"
    ) -> None:
        """
        Inicializa un jugador.

        Args:
            team: Equipo del jugador
            player_id: ID único (1 o 2)
            name: Nombre del jugador
        """
        self.team = team
        self.player_id = player_id
        self.name = name

    @abstractmethod
    def decide_action(
        self,
        opponent_team: Team,
        battle_state: Optional[any] = None
    ) -> PlayerAction:
        """
        Decide qué acción realizar en el turno actual.

        Este método debe ser implementado por cada subclase.

        Args:
            opponent_team: Equipo del oponente
            battle_state: Estado actual de la batalla (opcional)

        Returns:
            PlayerAction con la acción decidida

        Raises:
            NotImplementedError: Si no se implementa en la subclase
        """
        raise NotImplementedError("Subclasses must implement decide_action")

    def get_active_character(self) -> Character:
        """
        Obtiene el personaje activo del jugador.

        Returns:
            El personaje actualmente en combate
        """
        return self.team.active_character

    def get_available_actions(self) -> list[ActionType]:
        """
        Obtiene las acciones disponibles.

        Returns:
            Lista de tipos de acción que el jugador puede realizar
        """
        actions = [ActionType.ATTACK]

        # Verificar si hay habilidades disponibles
        active = self.get_active_character()
        for ability in active.abilities:
            if ability.is_available():
                actions.append(ActionType.USE_ABILITY)
                break

        # Verificar si hay personajes vivos para cambiar
        if len(self.team.get_alive_characters()) > 1:
            actions.append(ActionType.SWITCH)

        return actions

    def __repr__(self) -> str:
        """Representación para debugging."""
        return f"{self.__class__.__name__}(ID: {self.player_id}, Name: {self.name})"

    def __str__(self) -> str:
        """Representación legible."""
        return f"{self.name} (Player {self.player_id})"


class RandomPlayer(Player):
    """
    Jugador que toma decisiones aleatorias.

    Sirve como baseline para comparar otros agentes.

    Examples:
        >>> team = Team([char1, char2, char3])
        >>> player = RandomPlayer(team, player_id=1)
        >>> opponent_team = Team([char4, char5, char6])
        >>> action = player.decide_action(opponent_team)
        >>> action.action_type in [ActionType.ATTACK, ActionType.USE_ABILITY, ActionType.SWITCH]
        True
    """

    def __init__(
        self,
        team: Team,
        player_id: int,
        name: str = "RandomPlayer",
        attack_probability: float = 0.6,
        ability_probability: float = 0.3,
        switch_probability: float = 0.1
    ) -> None:
        """
        Inicializa un jugador aleatorio.

        Args:
            team: Equipo del jugador
            player_id: ID único
            name: Nombre del jugador
            attack_probability: Probabilidad de atacar
            ability_probability: Probabilidad de usar habilidad
            switch_probability: Probabilidad de cambiar personaje
        """
        super().__init__(team, player_id, name)
        self.attack_probability = attack_probability
        self.ability_probability = ability_probability
        self.switch_probability = switch_probability

    def decide_action(
        self,
        opponent_team: Team,
        battle_state: Optional[any] = None
    ) -> PlayerAction:
        """
        Decide una acción aleatoria.

        Args:
            opponent_team: Equipo del oponente
            battle_state: Estado de la batalla (no usado)

        Returns:
            PlayerAction con una acción aleatoria
        """
        active = self.get_active_character()
        available_actions = self.get_available_actions()

        # Si está aturdido, solo puede intentar cambiar
        if active.is_stunned():
            if ActionType.SWITCH in available_actions:
                return self._random_switch()
            else:
                # No puede hacer nada
                return PlayerAction(ActionType.ATTACK)

        # Decidir acción basándose en probabilidades
        choice = random.random()

        if choice < self.attack_probability:
            return PlayerAction(ActionType.ATTACK)

        elif choice < self.attack_probability + self.ability_probability:
            # Intentar usar habilidad
            if ActionType.USE_ABILITY in available_actions:
                ability = self._random_ability()
                if ability:
                    return PlayerAction(ActionType.USE_ABILITY, ability=ability)

        elif ActionType.SWITCH in available_actions:
            return self._random_switch()

        # Por defecto, atacar
        return PlayerAction(ActionType.ATTACK)

    def _random_ability(self) -> Optional[Ability]:
        """
        Selecciona una habilidad disponible al azar.

        Returns:
            Habilidad seleccionada, o None si no hay disponibles
        """
        active = self.get_active_character()
        available = [a for a in active.abilities if a.is_available()]

        if not available:
            return None

        return random.choice(available)

    def _random_switch(self) -> PlayerAction:
        """
        Genera una acción de cambio aleatorio.

        Returns:
            PlayerAction con un cambio a personaje aleatorio
        """
        alive_chars = self.team.get_alive_characters()
        active = self.get_active_character()

        # Filtrar el personaje activo
        available = [c for c in alive_chars if c != active]

        if not available:
            # No hay personajes para cambiar, atacar
            return PlayerAction(ActionType.ATTACK)

        target_char = random.choice(available)
        target_index = self.team.get_character_index(target_char)

        return PlayerAction(ActionType.SWITCH, switch_target=target_index)


class HumanPlayer(Player):
    """
    Jugador humano que requiere input manual.

    Esta es una implementación básica que podría extenderse con una UI.

    Examples:
        >>> team = Team([char1, char2, char3])
        >>> player = HumanPlayer(team, player_id=1)
        >>> # En un juego real, decide_action solicitaría input del usuario
    """

    def decide_action(
        self,
        opponent_team: Team,
        battle_state: Optional[any] = None
    ) -> PlayerAction:
        """
        Solicita decisión al jugador humano.

        NOTA: Implementación básica que retorna ataque.
        En una versión completa, esto solicitaría input del usuario.

        Args:
            opponent_team: Equipo del oponente
            battle_state: Estado de la batalla

        Returns:
            PlayerAction decidida por el usuario
        """
        print(f"\n{self.name}'s turn")
        print(f"Active character: {self.get_active_character()}")
        print("\nAvailable actions:")
        print("1. Attack")
        print("2. Use Ability")
        print("3. Switch Character")

        # En una implementación completa, aquí iría input()
        # Por ahora, retorna ataque por defecto
        return PlayerAction(ActionType.ATTACK)
