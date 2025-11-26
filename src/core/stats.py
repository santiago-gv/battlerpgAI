"""
Módulo de estadísticas y tipos para BattleRPG AI.

Define las clases de personajes, efectos de estado y estructura de estadísticas base.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict


class CharacterClass(Enum):
    """
    Clases de personajes disponibles en el juego.

    El sistema funciona como rock-paper-scissors extendido:
    - WARRIOR > ROGUE > MAGE > WARRIOR (ciclo básico)
    - TANK: Resistente a WARRIOR y ROGUE
    - SUPPORT: Neutral contra todos, provee buffs a aliados
    """
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    TANK = "tank"
    SUPPORT = "support"

    def __str__(self) -> str:
        """Retorna una representación legible de la clase."""
        return self.value.capitalize()


class StatusEffect(Enum):
    """
    Efectos de estado que pueden afectar a los personajes durante el combate.

    Cada efecto tiene mecánicas específicas que afectan el comportamiento
    del personaje en batalla.
    """
    BURN = "burn"         # Daño por turno (5% del HP máximo)
    POISON = "poison"     # Daño creciente (comienza en 5%, aumenta 5% por turno)
    STUN = "stun"         # El personaje pierde su siguiente turno
    SHIELD = "shield"     # Reduce el daño recibido en un 50%
    BUFF = "buff"         # Aumenta el ataque en un 30%
    DEBUFF = "debuff"     # Reduce el ataque en un 30%

    def __str__(self) -> str:
        """Retorna una representación legible del efecto."""
        return self.value.capitalize()


class ActionType(Enum):
    """
    Tipos de acciones disponibles durante un combate.

    Define las acciones que un jugador puede realizar en su turno.
    """
    ATTACK = "attack"           # Ataque básico
    USE_ABILITY = "use_ability" # Usar una habilidad especial
    SWITCH = "switch"           # Cambiar de personaje activo
    ITEM = "item"               # Usar un objeto (implementación futura)

    def __str__(self) -> str:
        """Retorna una representación legible de la acción."""
        return self.value.replace("_", " ").capitalize()


@dataclass
class Stats:
    """
    Estadísticas base de un personaje.

    Estas estadísticas determinan el poder y características del personaje
    en combate. Todas las estadísticas deben ser valores positivos.

    Attributes:
        hp: Puntos de vida máximos. Cuando llegan a 0, el personaje es derrotado.
        attack: Poder de ataque base. Determina el daño infligido.
        defense: Reducción de daño. Se resta del daño recibido.
        speed: Determina el orden de turno. El personaje más rápido ataca primero.

    Raises:
        ValueError: Si alguna estadística tiene un valor inválido.

    Examples:
        >>> stats = Stats(hp=100, attack=50, defense=20, speed=30)
        >>> print(stats)
        Stats(HP=100, ATK=50, DEF=20, SPD=30)
    """
    hp: int
    attack: int
    defense: int
    speed: int

    def __post_init__(self) -> None:
        """
        Valida las estadísticas después de la inicialización.

        Raises:
            ValueError: Si alguna estadística no cumple con los requisitos.
        """
        if self.hp <= 0:
            raise ValueError(f"HP debe ser positivo, recibido: {self.hp}")
        if self.attack < 0:
            raise ValueError(f"Attack no puede ser negativo, recibido: {self.attack}")
        if self.defense < 0:
            raise ValueError(f"Defense no puede ser negativo, recibido: {self.defense}")
        if self.speed < 0:
            raise ValueError(f"Speed no puede ser negativo, recibido: {self.speed}")

    def __str__(self) -> str:
        """Retorna una representación legible de las estadísticas."""
        return f"Stats(HP={self.hp}, ATK={self.attack}, DEF={self.defense}, SPD={self.speed})"

    def to_dict(self) -> Dict[str, int]:
        """
        Convierte las estadísticas a un diccionario.

        Returns:
            Diccionario con las estadísticas como claves y valores.
        """
        return {
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'Stats':
        """
        Crea un objeto Stats desde un diccionario.

        Args:
            data: Diccionario con las claves 'hp', 'attack', 'defense', 'speed'.

        Returns:
            Nueva instancia de Stats.

        Raises:
            KeyError: Si falta alguna clave requerida.
        """
        return cls(
            hp=data["hp"],
            attack=data["attack"],
            defense=data["defense"],
            speed=data["speed"]
        )


# Constantes de configuración de efectos de estado
STATUS_EFFECT_CONFIG = {
    StatusEffect.BURN: {
        "damage_percent": 0.05,  # 5% del HP máximo por turno
        "duration": 3,           # Duración en turnos
    },
    StatusEffect.POISON: {
        "initial_damage_percent": 0.05,  # 5% inicial
        "increment_percent": 0.05,       # Incremento por turno
        "duration": 4,                   # Duración en turnos
    },
    StatusEffect.STUN: {
        "duration": 1,  # Pierde 1 turno
    },
    StatusEffect.SHIELD: {
        "damage_reduction": 0.5,  # Reduce daño en 50%
        "duration": 2,            # Duración en turnos
    },
    StatusEffect.BUFF: {
        "attack_multiplier": 1.3,  # Aumenta ataque en 30%
        "duration": 3,             # Duración en turnos
    },
    StatusEffect.DEBUFF: {
        "attack_multiplier": 0.7,  # Reduce ataque en 30%
        "duration": 3,             # Duración en turnos
    },
}
