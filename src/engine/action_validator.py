"""
Módulo de validación de acciones para BattleRPG AI.

Valida que las acciones solicitadas sean legales según las reglas del juego.
"""

from typing import Optional

from src.core.character import Character
from src.core.team import Team
from src.core.ability import Ability
from src.core.stats import ActionType, StatusEffect


class ActionValidator:
    """
    Valida acciones de combate.

    Verifica que las acciones cumplan con las reglas del juego:
    - Personajes estén vivos
    - Habilidades estén disponibles
    - Cambios sean válidos
    - Personajes no estén aturdidos

    Examples:
        >>> validator = ActionValidator()
        >>> char = Character("Test", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
        >>> validator.can_attack(char)
        True
        >>> char.apply_status_effect(StatusEffect.STUN)
        True
        >>> validator.can_attack(char)
        False
    """

    def can_attack(self, character: Character) -> tuple[bool, str]:
        """
        Verifica si un personaje puede atacar.

        Args:
            character: Personaje a validar

        Returns:
            Tupla (puede_atacar, razón)

        Examples:
            >>> validator = ActionValidator()
            >>> char = Character("Test", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> can, reason = validator.can_attack(char)
            >>> can
            True
        """
        if not character.is_alive():
            return False, "Character is fainted"

        if character.is_stunned():
            return False, "Character is stunned"

        return True, ""

    def can_use_ability(
        self,
        character: Character,
        ability: Ability
    ) -> tuple[bool, str]:
        """
        Verifica si un personaje puede usar una habilidad.

        Args:
            character: Personaje que quiere usar la habilidad
            ability: Habilidad a usar

        Returns:
            Tupla (puede_usar, razón)

        Examples:
            >>> validator = ActionValidator()
            >>> char = Character("Test", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> from src.core.ability import create_basic_abilities
            >>> abilities = create_basic_abilities()
            >>> ability = abilities["power_strike"]
            >>> can, reason = validator.can_use_ability(char, ability)
            >>> can
            True
        """
        # Verificar si puede atacar (vivo y no aturdido)
        can, reason = self.can_attack(character)
        if not can:
            return False, reason

        # Verificar si la habilidad está en cooldown
        if not ability.is_available():
            return False, f"Ability is on cooldown ({ability.current_cooldown} turns left)"

        # Verificar si el personaje puede usar esta habilidad (restricción de clase)
        if not ability.can_be_used_by(character.char_class):
            return False, f"Character class {character.char_class} cannot use this ability"

        return True, ""

    def can_switch(
        self,
        team: Team,
        target_index: int
    ) -> tuple[bool, str]:
        """
        Verifica si un equipo puede cambiar a un personaje.

        Args:
            team: Equipo que quiere cambiar
            target_index: Índice del personaje destino

        Returns:
            Tupla (puede_cambiar, razón)

        Examples:
            >>> validator = ActionValidator()
            >>> char1 = Character("A", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> char2 = Character("B", CharacterClass.MAGE, Stats(80, 60, 10, 40))
            >>> char3 = Character("C", CharacterClass.ROGUE, Stats(90, 55, 15, 45))
            >>> team = Team([char1, char2, char3])
            >>> can, reason = validator.can_switch(team, 1)
            >>> can
            True
        """
        # Verificar índice válido
        if target_index < 0 or target_index >= 3:
            return False, "Invalid character index"

        # Verificar que no sea el personaje activo
        if target_index == team.active_index:
            return False, "Character is already active"

        # Verificar que el personaje esté vivo
        if not team.characters[target_index].is_alive():
            return False, "Character is fainted"

        return True, ""

    def validate_action(
        self,
        action_type: ActionType,
        character: Character,
        team: Team,
        ability: Optional[Ability] = None,
        switch_target: Optional[int] = None
    ) -> tuple[bool, str]:
        """
        Valida una acción completa.

        Args:
            action_type: Tipo de acción a realizar
            character: Personaje que realiza la acción
            team: Equipo al que pertenece el personaje
            ability: Habilidad a usar (si action_type es USE_ABILITY)
            switch_target: Índice del personaje destino (si action_type es SWITCH)

        Returns:
            Tupla (es_válida, razón)

        Examples:
            >>> validator = ActionValidator()
            >>> char = Character("Test", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> team = Team([char, char, char])  # Simplified example
            >>> can, reason = validator.validate_action(ActionType.ATTACK, char, team)
            >>> can
            True
        """
        if action_type == ActionType.ATTACK:
            return self.can_attack(character)

        elif action_type == ActionType.USE_ABILITY:
            if ability is None:
                return False, "No ability specified"
            return self.can_use_ability(character, ability)

        elif action_type == ActionType.SWITCH:
            if switch_target is None:
                return False, "No switch target specified"
            return self.can_switch(team, switch_target)

        elif action_type == ActionType.ITEM:
            return False, "Items not implemented in MVP"

        else:
            return False, f"Unknown action type: {action_type}"
