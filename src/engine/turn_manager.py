"""
Módulo de gestión de turnos para BattleRPG AI.

Determina el orden de acciones basado en velocidad y prioridad de habilidades.
"""

from typing import List, Tuple
from dataclasses import dataclass

from src.core.character import Character
from src.core.ability import Ability


@dataclass
class TurnAction:
    """
    Representa una acción planificada en un turno.

    Attributes:
        character: Personaje que actuará
        player_id: ID del jugador (1 o 2)
        priority: Prioridad de la acción
        speed: Velocidad del personaje
    """
    character: Character
    player_id: int
    priority: int = 0
    speed: int = 0


class TurnManager:
    """
    Gestiona el orden de acciones en un turno.

    Basado en el sistema de Pokémon:
    1. Cambios de personaje van primero
    2. Habilidades con prioridad alta
    3. Orden por velocidad del personaje
    4. En caso de empate, aleatorio o ID menor

    Examples:
        >>> tm = TurnManager()
        >>> char1 = Character("Fast", CharacterClass.ROGUE, Stats(100, 50, 20, 50))
        >>> char2 = Character("Slow", CharacterClass.TANK, Stats(120, 60, 30, 20))
        >>> order = tm.determine_order([(char1, 1, 0), (char2, 2, 0)])
        >>> order[0].character.name
        'Fast'
    """

    def determine_order(
        self,
        actions: List[Tuple[Character, int, int]]
    ) -> List[TurnAction]:
        """
        Determina el orden de acciones en un turno.

        Args:
            actions: Lista de tuplas (personaje, player_id, priority)

        Returns:
            Lista ordenada de TurnAction

        Examples:
            >>> tm = TurnManager()
            >>> char1 = Character("A", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> char2 = Character("B", CharacterClass.MAGE, Stats(80, 60, 10, 40))
            >>> actions = [(char1, 1, 0), (char2, 2, 0)]
            >>> order = tm.determine_order(actions)
            >>> order[0].character.name
            'B'
        """
        turn_actions = []
        for char, player_id, priority in actions:
            turn_actions.append(
                TurnAction(
                    character=char,
                    player_id=player_id,
                    priority=priority,
                    speed=char.stats.speed
                )
            )

        # Ordenar por: 1) Prioridad (mayor primero), 2) Velocidad (mayor primero)
        turn_actions.sort(key=lambda x: (-x.priority, -x.speed, x.player_id))

        return turn_actions

    def get_first_striker(
        self,
        char1: Character,
        char2: Character,
        ability1: Ability = None,
        ability2: Ability = None
    ) -> int:
        """
        Determina quién ataca primero entre dos personajes.

        Args:
            char1: Primer personaje
            char2: Segundo personaje
            ability1: Habilidad del primer personaje (None si ataque básico)
            ability2: Habilidad del segundo personaje (None si ataque básico)

        Returns:
            1 si char1 va primero, 2 si char2 va primero

        Examples:
            >>> tm = TurnManager()
            >>> fast = Character("Fast", CharacterClass.ROGUE, Stats(100, 50, 20, 50))
            >>> slow = Character("Slow", CharacterClass.TANK, Stats(120, 60, 30, 20))
            >>> tm.get_first_striker(fast, slow)
            1
        """
        priority1 = ability1.priority if ability1 else 0
        priority2 = ability2.priority if ability2 else 0

        if priority1 > priority2:
            return 1
        elif priority2 > priority1:
            return 2
        elif char1.stats.speed > char2.stats.speed:
            return 1
        elif char2.stats.speed > char1.stats.speed:
            return 2
        else:
            # Empate: jugador 1 va primero por defecto
            return 1
