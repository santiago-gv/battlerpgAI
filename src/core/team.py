"""
Módulo de equipos para BattleRPG AI.

Define la clase Team que gestiona un equipo de 3 personajes en combate.
Similar al sistema de Pokémon, solo un personaje puede estar activo a la vez.
"""

from typing import List, Optional

from src.core.character import Character


class Team:
    """
    Representa un equipo de 3 personajes en combate.

    Similar al sistema de Pokémon, solo un personaje puede estar activo
    a la vez, pero el jugador puede cambiar entre ellos durante la batalla.

    Attributes:
        characters: Lista de exactamente 3 personajes
        active_index: Índice del personaje activo (0-2)
        team_name: Nombre opcional del equipo

    Examples:
        >>> char1 = Character("Warrior", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
        >>> char2 = Character("Mage", CharacterClass.MAGE, Stats(80, 60, 10, 40))
        >>> char3 = Character("Rogue", CharacterClass.ROGUE, Stats(90, 55, 15, 45))
        >>> team = Team([char1, char2, char3])
        >>> team.active_character.name
        'Warrior'
        >>> team.switch_character(1)
        True
        >>> team.active_character.name
        'Mage'
    """

    def __init__(
        self,
        characters: List[Character],
        team_name: Optional[str] = None
    ) -> None:
        """
        Inicializa un equipo.

        Args:
            characters: Lista de exactamente 3 personajes
            team_name: Nombre opcional para el equipo

        Raises:
            ValueError: Si no hay exactamente 3 personajes
            TypeError: Si algún elemento no es un Character
        """
        if len(characters) != 3:
            raise ValueError(
                f"Un equipo debe tener exactamente 3 personajes, "
                f"recibido: {len(characters)}"
            )

        for i, char in enumerate(characters):
            if not isinstance(char, Character):
                raise TypeError(
                    f"El elemento {i} no es un Character: {type(char)}"
                )

        self.characters = characters
        self.active_index = 0
        self.team_name = team_name or "Team"

        # Marcar el primer personaje como activo
        self.characters[0].is_active = True

    @property
    def active_character(self) -> Character:
        """
        Retorna el personaje activo actual.

        Returns:
            El personaje que está actualmente en combate
        """
        return self.characters[self.active_index]

    def switch_character(self, new_index: int) -> bool:
        """
        Cambia el personaje activo.

        Args:
            new_index: Índice del nuevo personaje activo (0-2)

        Returns:
            True si el cambio fue exitoso, False si no es válido

        Examples:
            >>> team.switch_character(1)  # Cambiar al segundo personaje
            True
            >>> team.switch_character(5)  # Índice fuera de rango
            False
            >>> team.active_character.current_hp = 0  # Personaje derrotado
            >>> team.switch_character(0)  # No puede cambiar a personaje muerto
            False
        """
        # Validar índice
        if new_index < 0 or new_index >= 3:
            return False

        # No puede cambiar al mismo personaje
        if new_index == self.active_index:
            return False

        # No puede cambiar a personaje derrotado
        if not self.characters[new_index].is_alive():
            return False

        # Realizar cambio
        self.characters[self.active_index].is_active = False
        self.active_index = new_index
        self.characters[self.active_index].is_active = True

        return True

    def switch_to_character(self, character_name: str) -> bool:
        """
        Cambia al personaje especificado por nombre.

        Args:
            character_name: Nombre del personaje al que cambiar

        Returns:
            True si el cambio fue exitoso, False si no se encontró o no es válido
        """
        for i, char in enumerate(self.characters):
            if char.name == character_name:
                return self.switch_character(i)
        return False

    def auto_switch_on_faint(self) -> Optional[Character]:
        """
        Cambia automáticamente a un personaje vivo si el activo fue derrotado.

        Este método es útil cuando el personaje activo es derrotado y
        necesitamos cambiar automáticamente al siguiente personaje vivo.

        Returns:
            El nuevo personaje activo, o None si el equipo está derrotado

        Examples:
            >>> team.active_character.current_hp = 0  # Personaje activo derrotado
            >>> new_char = team.auto_switch_on_faint()
            >>> new_char is not None
            True
        """
        # Si el personaje activo sigue vivo, no hacer nada
        if self.active_character.is_alive():
            return self.active_character

        # Buscar el primer personaje vivo
        for i, char in enumerate(self.characters):
            if i != self.active_index and char.is_alive():
                self.switch_character(i)
                return self.active_character

        # Si no hay personajes vivos, retornar None
        return None

    def is_defeated(self) -> bool:
        """
        Verifica si el equipo ha sido completamente derrotado.

        Returns:
            True si todos los personajes están derrotados, False en caso contrario

        Examples:
            >>> team.is_defeated()
            False
            >>> for char in team.characters:
            ...     char.current_hp = 0
            >>> team.is_defeated()
            True
        """
        return all(not char.is_alive() for char in self.characters)

    def get_alive_characters(self) -> List[Character]:
        """
        Retorna lista de personajes vivos.

        Returns:
            Lista con los personajes que tienen HP > 0

        Examples:
            >>> alive = team.get_alive_characters()
            >>> len(alive)
            3
            >>> team.characters[0].current_hp = 0
            >>> alive = team.get_alive_characters()
            >>> len(alive)
            2
        """
        return [char for char in self.characters if char.is_alive()]

    def get_alive_count(self) -> int:
        """
        Retorna la cantidad de personajes vivos.

        Returns:
            Número de personajes con HP > 0
        """
        return len(self.get_alive_characters())

    def get_defeated_characters(self) -> List[Character]:
        """
        Retorna lista de personajes derrotados.

        Returns:
            Lista con los personajes que tienen HP == 0
        """
        return [char for char in self.characters if not char.is_alive()]

    def get_character_by_name(self, name: str) -> Optional[Character]:
        """
        Busca un personaje por nombre.

        Args:
            name: Nombre del personaje a buscar

        Returns:
            El personaje encontrado, o None si no existe
        """
        for char in self.characters:
            if char.name == name:
                return char
        return None

    def get_character_index(self, character: Character) -> Optional[int]:
        """
        Obtiene el índice de un personaje en el equipo.

        Args:
            character: Personaje a buscar

        Returns:
            Índice del personaje (0-2), o None si no pertenece al equipo
        """
        try:
            return self.characters.index(character)
        except ValueError:
            return None

    def get_total_hp(self) -> int:
        """
        Calcula el HP total del equipo (suma de HP actual de todos).

        Returns:
            Suma de current_hp de todos los personajes

        Examples:
            >>> total = team.get_total_hp()
            >>> total == sum(char.current_hp for char in team.characters)
            True
        """
        return sum(char.current_hp for char in self.characters)

    def get_total_hp_ratio(self) -> float:
        """
        Calcula el ratio de HP total respecto al máximo del equipo.

        Returns:
            Valor entre 0.0 y 1.0 representando el HP total del equipo

        Examples:
            >>> ratio = team.get_total_hp_ratio()
            >>> 0.0 <= ratio <= 1.0
            True
        """
        current_total = sum(char.current_hp for char in self.characters)
        max_total = sum(char.stats.hp for char in self.characters)
        return current_total / max_total if max_total > 0 else 0.0

    def reset_all_combat_stats(self) -> None:
        """
        Resetea las estadísticas de combate de todos los personajes.

        Útil al finalizar una batalla para preparar el equipo para la siguiente.
        """
        for char in self.characters:
            char.reset_combat_stats()

    def heal_all(self, amount: int) -> int:
        """
        Cura a todos los personajes del equipo.

        Args:
            amount: Cantidad de HP a restaurar a cada personaje

        Returns:
            Cantidad total de HP restaurado al equipo
        """
        total_healed = 0
        for char in self.characters:
            total_healed += char.heal(amount)
        return total_healed

    def revive_all(self) -> None:
        """
        Revive a todos los personajes derrotados con 50% de HP.

        Útil para entrenamientos o modos de juego especiales.
        """
        for char in self.characters:
            if not char.is_alive():
                char.current_hp = char.stats.hp // 2

    def __repr__(self) -> str:
        """Representación del equipo para debugging."""
        alive_count = self.get_alive_count()
        active_name = self.active_character.name
        return (f"Team({self.team_name}, {alive_count}/3 alive, "
                f"Active: {active_name})")

    def __str__(self) -> str:
        """Representación legible del equipo."""
        chars_str = ", ".join(
            f"{char.name} ({char.current_hp}/{char.stats.hp})"
            for char in self.characters
        )
        return f"{self.team_name}: [{chars_str}]"

    def __getitem__(self, index: int) -> Character:
        """Permite acceso por índice: team[0], team[1], team[2]."""
        return self.characters[index]

    def __len__(self) -> int:
        """Retorna siempre 3 (tamaño fijo del equipo)."""
        return 3
