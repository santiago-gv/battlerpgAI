"""
Módulo de carga de configuración para BattleRPG AI.

Carga personajes, habilidades y equipos desde archivos JSON.
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path

from src.core.character import Character
from src.core.team import Team
from src.core.ability import Ability, AbilityType, AbilityEffect, AbilityTarget
from src.core.stats import CharacterClass, Stats, StatusEffect


class ConfigLoader:
    """
    Carga configuraciones desde archivos JSON.

    Attributes:
        config_dir: Directorio con archivos de configuración
        abilities: Diccionario de habilidades cargadas
        characters: Diccionario de personajes cargados
        preset_teams: Diccionario de equipos predefinidos

    Examples:
        >>> loader = ConfigLoader()
        >>> abilities = loader.load_abilities()
        >>> characters = loader.load_characters()
        >>> team = loader.create_preset_team("Balanced Team")
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Inicializa el cargador de configuración.

        Args:
            config_dir: Directorio con configs (por defecto: configs/)
        """
        if config_dir is None:
            # Buscar directorio configs/ desde la raíz del proyecto
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            config_dir = project_root / "configs"

        self.config_dir = Path(config_dir)
        self.abilities: Dict[str, Ability] = {}
        self.characters: Dict[str, Character] = {}
        self.preset_teams: Dict[str, List[str]] = {}

    def load_abilities(self, filename: str = "abilities.json") -> Dict[str, Ability]:
        """
        Carga habilidades desde archivo JSON.

        Args:
            filename: Nombre del archivo JSON

        Returns:
            Diccionario con habilidades {nombre: Ability}

        Examples:
            >>> loader = ConfigLoader()
            >>> abilities = loader.load_abilities()
            >>> "fireball" in abilities
            True
        """
        filepath = self.config_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Archivo de habilidades no encontrado: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.abilities.clear()

        for ability_data in data["abilities"]:
            # Parsear efectos
            effects = []
            for effect_data in ability_data["effects"]:
                effect = AbilityEffect(
                    effect_type=AbilityType(effect_data["effect_type"]),
                    value=effect_data.get("value", 0),
                    status_effect=StatusEffect(effect_data["status_effect"])
                        if effect_data.get("status_effect") else None,
                    probability=effect_data.get("probability", 1.0),
                    target=AbilityTarget(effect_data.get("target", "opponent"))
                )
                effects.append(effect)

            # Crear habilidad
            ability = Ability(
                name=ability_data.get("display_name", ability_data["name"]),
                description=ability_data["description"],
                ability_type=AbilityType(ability_data["ability_type"]),
                effects=effects,
                cooldown=ability_data.get("cooldown", 0),
                priority=ability_data.get("priority", 0),
                required_class=CharacterClass(ability_data["required_class"])
                    if ability_data.get("required_class") else None
            )

            self.abilities[ability_data["name"]] = ability

        return self.abilities

    def load_characters(self, filename: str = "characters.json") -> Dict[str, Character]:
        """
        Carga personajes desde archivo JSON.

        Args:
            filename: Nombre del archivo JSON

        Returns:
            Diccionario con personajes {nombre: Character}

        Examples:
            >>> loader = ConfigLoader()
            >>> loader.load_abilities()  # Necesario para las habilidades
            >>> characters = loader.load_characters()
            >>> "Goliath" in characters
            True
        """
        filepath = self.config_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Archivo de personajes no encontrado: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Asegurar que las habilidades estén cargadas
        if not self.abilities:
            self.load_abilities()

        self.characters.clear()

        for char_data in data["characters"]:
            # Parsear stats
            stats = Stats.from_dict(char_data["stats"])

            # Parsear habilidades
            abilities = []
            for ability_name in char_data.get("abilities", []):
                if ability_name in self.abilities:
                    abilities.append(self.abilities[ability_name])
                else:
                    print(f"Warning: Habilidad '{ability_name}' no encontrada para {char_data['name']}")

            # Crear personaje
            character = Character(
                name=char_data["name"],
                char_class=CharacterClass(char_data["char_class"]),
                stats=stats,
                abilities=abilities
            )

            self.characters[char_data["name"]] = character

        # Cargar equipos predefinidos
        if "preset_teams" in data:
            for team_data in data["preset_teams"]:
                self.preset_teams[team_data["name"]] = team_data["characters"]

        return self.characters

    def create_preset_team(self, team_name: str) -> Optional[Team]:
        """
        Crea un equipo predefinido.

        Args:
            team_name: Nombre del equipo predefinido

        Returns:
            Team creado, o None si no existe

        Examples:
            >>> loader = ConfigLoader()
            >>> loader.load_abilities()
            >>> loader.load_characters()
            >>> team = loader.create_preset_team("Balanced Team")
            >>> len(team) == 3
            True
        """
        if team_name not in self.preset_teams:
            print(f"Equipo '{team_name}' no encontrado")
            return None

        char_names = self.preset_teams[team_name]

        if len(char_names) != 3:
            print(f"Equipo '{team_name}' debe tener exactamente 3 personajes")
            return None

        # Crear copias de los personajes (para que cada equipo sea independiente)
        team_chars = []
        for name in char_names:
            if name not in self.characters:
                print(f"Personaje '{name}' no encontrado")
                return None

            original = self.characters[name]
            # Crear copia del personaje
            char_copy = Character(
                name=original.name,
                char_class=original.char_class,
                stats=Stats(
                    hp=original.stats.hp,
                    attack=original.stats.attack,
                    defense=original.stats.defense,
                    speed=original.stats.speed
                ),
                abilities=original.abilities.copy()
            )
            team_chars.append(char_copy)

        return Team(team_chars, team_name=team_name)

    def create_custom_team(
        self,
        char_names: List[str],
        team_name: str = "Custom Team"
    ) -> Optional[Team]:
        """
        Crea un equipo personalizado.

        Args:
            char_names: Lista con nombres de 3 personajes
            team_name: Nombre del equipo

        Returns:
            Team creado, o None si hay error

        Examples:
            >>> loader = ConfigLoader()
            >>> loader.load_abilities()
            >>> loader.load_characters()
            >>> team = loader.create_custom_team(["Goliath", "Pyro", "Shadow"])
            >>> team is not None
            True
        """
        if len(char_names) != 3:
            print(f"Debe proporcionar exactamente 3 personajes, recibido: {len(char_names)}")
            return None

        team_chars = []
        for name in char_names:
            if name not in self.characters:
                print(f"Personaje '{name}' no encontrado")
                return None

            original = self.characters[name]
            # Crear copia
            char_copy = Character(
                name=original.name,
                char_class=original.char_class,
                stats=Stats(
                    hp=original.stats.hp,
                    attack=original.stats.attack,
                    defense=original.stats.defense,
                    speed=original.stats.speed
                ),
                abilities=original.abilities.copy()
            )
            team_chars.append(char_copy)

        return Team(team_chars, team_name=team_name)

    def get_character_copy(self, name: str) -> Optional[Character]:
        """
        Obtiene una copia de un personaje.

        Args:
            name: Nombre del personaje

        Returns:
            Copia del personaje, o None si no existe
        """
        if name not in self.characters:
            return None

        original = self.characters[name]
        return Character(
            name=original.name,
            char_class=original.char_class,
            stats=Stats(
                hp=original.stats.hp,
                attack=original.stats.attack,
                defense=original.stats.defense,
                speed=original.stats.speed
            ),
            abilities=original.abilities.copy()
        )

    def list_available_characters(self) -> List[str]:
        """
        Lista todos los personajes disponibles.

        Returns:
            Lista de nombres de personajes
        """
        return list(self.characters.keys())

    def list_available_teams(self) -> List[str]:
        """
        Lista todos los equipos predefinidos.

        Returns:
            Lista de nombres de equipos
        """
        return list(self.preset_teams.keys())

    def print_character_info(self, name: str) -> None:
        """
        Imprime información de un personaje.

        Args:
            name: Nombre del personaje
        """
        if name not in self.characters:
            print(f"Personaje '{name}' no encontrado")
            return

        char = self.characters[name]
        print(f"\n=== {char.name} ===")
        print(f"Clase: {char.char_class.value}")
        print(f"HP: {char.stats.hp} | ATK: {char.stats.attack} | "
              f"DEF: {char.stats.defense} | SPD: {char.stats.speed}")
        print(f"Habilidades: {', '.join(a.name for a in char.abilities)}")


# Instancia global del loader
_config_loader_instance: Optional[ConfigLoader] = None


def get_config_loader() -> ConfigLoader:
    """
    Obtiene la instancia singleton del config loader.

    Returns:
        ConfigLoader global

    Examples:
        >>> loader = get_config_loader()
        >>> abilities = loader.load_abilities()
    """
    global _config_loader_instance
    if _config_loader_instance is None:
        _config_loader_instance = ConfigLoader()
    return _config_loader_instance
