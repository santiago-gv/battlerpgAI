"""
Módulo de habilidades para BattleRPG AI.

Define el sistema de habilidades especiales que los personajes pueden usar en combate.
Similar a los movimientos de Pokémon, cada habilidad tiene efectos únicos.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from src.core.stats import StatusEffect, CharacterClass


class AbilityType(Enum):
    """
    Tipos de habilidades disponibles.

    Define la categoría principal del efecto de la habilidad.
    """
    DAMAGE = "damage"           # Inflige daño al oponente
    HEAL = "heal"               # Restaura HP propio o aliado
    STATUS = "status"           # Aplica efecto de estado
    BUFF = "buff"               # Mejora stats propias o aliadas
    DEBUFF = "debuff"           # Reduce stats del oponente
    MIXED = "mixed"             # Combina múltiples efectos

    def __str__(self) -> str:
        return self.value.capitalize()


class AbilityTarget(Enum):
    """
    Objetivos posibles de una habilidad.

    Define a quién afecta la habilidad.
    """
    OPPONENT = "opponent"       # Afecta al oponente activo
    SELF = "self"              # Afecta al usuario
    ALLY = "ally"              # Afecta a un aliado (no usado en 1v1)
    ALL_OPPONENTS = "all_opponents"  # Afecta a todos los oponentes
    ALL_ALLIES = "all_allies"  # Afecta a todos los aliados

    def __str__(self) -> str:
        return self.value.replace("_", " ").capitalize()


@dataclass
class AbilityEffect:
    """
    Representa un efecto específico de una habilidad.

    Una habilidad puede tener múltiples efectos (ej: daño + aplicar burn).

    Attributes:
        effect_type: Tipo de efecto (damage, heal, status, etc.)
        value: Valor del efecto (daño, curación, etc.)
        status_effect: Efecto de estado a aplicar (si aplica)
        probability: Probabilidad de aplicar el efecto (0.0-1.0)
        target: Objetivo del efecto
    """
    effect_type: AbilityType
    value: int = 0
    status_effect: Optional[StatusEffect] = None
    probability: float = 1.0
    target: AbilityTarget = AbilityTarget.OPPONENT

    def __post_init__(self) -> None:
        """Valida el efecto después de la inicialización."""
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError(
                f"Probability debe estar entre 0.0 y 1.0, recibido: {self.probability}"
            )


class Ability:
    """
    Representa una habilidad especial que un personaje puede usar en combate.

    Similar a los movimientos de Pokémon, cada habilidad tiene:
    - Efectos (daño, status, etc.)
    - Cooldown (turnos antes de poder usar de nuevo)
    - Prioridad (determina orden en el turno)

    Attributes:
        name: Nombre de la habilidad
        description: Descripción del efecto
        ability_type: Tipo principal de la habilidad
        effects: Lista de efectos que aplica
        cooldown: Turnos que deben pasar antes de usar de nuevo
        current_cooldown: Turnos restantes hasta poder usar
        priority: Prioridad de ejecución (mayor = primero)
        required_class: Clase requerida para usar (None = cualquiera)

    Examples:
        >>> fireball = Ability(
        ...     name="Fireball",
        ...     description="Lanza una bola de fuego que causa daño y puede quemar",
        ...     ability_type=AbilityType.MIXED,
        ...     effects=[
        ...         AbilityEffect(AbilityType.DAMAGE, value=40),
        ...         AbilityEffect(AbilityType.STATUS, status_effect=StatusEffect.BURN, probability=0.3)
        ...     ],
        ...     cooldown=2
        ... )
    """

    def __init__(
        self,
        name: str,
        description: str,
        ability_type: AbilityType,
        effects: List[AbilityEffect],
        cooldown: int = 0,
        priority: int = 0,
        required_class: Optional[CharacterClass] = None
    ) -> None:
        """
        Inicializa una nueva habilidad.

        Args:
            name: Nombre único de la habilidad
            description: Descripción del efecto
            ability_type: Tipo principal de la habilidad
            effects: Lista de efectos que aplica
            cooldown: Turnos de espera entre usos (0 = sin cooldown)
            priority: Prioridad de ejecución (0 = normal, mayor = antes)
            required_class: Clase requerida (None = cualquier clase)

        Raises:
            ValueError: Si cooldown o priority son negativos
            ValueError: Si la lista de efectos está vacía
        """
        if cooldown < 0:
            raise ValueError(f"Cooldown no puede ser negativo: {cooldown}")
        if priority < 0:
            raise ValueError(f"Priority no puede ser negativo: {priority}")
        if not effects:
            raise ValueError("La habilidad debe tener al menos un efecto")

        self.name = name
        self.description = description
        self.ability_type = ability_type
        self.effects = effects
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.priority = priority
        self.required_class = required_class

    def is_available(self) -> bool:
        """
        Verifica si la habilidad está disponible para usar.

        Returns:
            True si current_cooldown == 0, False en caso contrario
        """
        return self.current_cooldown == 0

    def use(self) -> bool:
        """
        Marca la habilidad como usada y activa su cooldown.

        Returns:
            True si se usó exitosamente, False si estaba en cooldown

        Examples:
            >>> ability.use()
            True
            >>> ability.is_available()
            False
        """
        if not self.is_available():
            return False

        self.current_cooldown = self.cooldown
        return True

    def reduce_cooldown(self, amount: int = 1) -> None:
        """
        Reduce el cooldown actual.

        Generalmente se llama al inicio de cada turno del personaje.

        Args:
            amount: Cantidad a reducir (por defecto 1)
        """
        self.current_cooldown = max(0, self.current_cooldown - amount)

    def reset_cooldown(self) -> None:
        """Resetea el cooldown a 0, haciendo la habilidad disponible."""
        self.current_cooldown = 0

    def can_be_used_by(self, char_class: CharacterClass) -> bool:
        """
        Verifica si una clase puede usar esta habilidad.

        Args:
            char_class: Clase del personaje

        Returns:
            True si puede usarla, False en caso contrario
        """
        if self.required_class is None:
            return True
        return self.required_class == char_class

    def get_damage_value(self) -> int:
        """
        Obtiene el valor de daño total de la habilidad.

        Returns:
            Suma de todos los efectos de daño
        """
        total_damage = 0
        for effect in self.effects:
            if effect.effect_type == AbilityType.DAMAGE:
                total_damage += effect.value
        return total_damage

    def get_heal_value(self) -> int:
        """
        Obtiene el valor de curación total de la habilidad.

        Returns:
            Suma de todos los efectos de curación
        """
        total_heal = 0
        for effect in self.effects:
            if effect.effect_type == AbilityType.HEAL:
                total_heal += effect.value
        return total_heal

    def get_status_effects(self) -> List[StatusEffect]:
        """
        Obtiene todos los efectos de estado que puede aplicar.

        Returns:
            Lista de efectos de estado
        """
        status_effects = []
        for effect in self.effects:
            if effect.effect_type == AbilityType.STATUS and effect.status_effect:
                status_effects.append(effect.status_effect)
        return status_effects

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la habilidad a un diccionario.

        Returns:
            Diccionario con todos los atributos de la habilidad
        """
        return {
            "name": self.name,
            "description": self.description,
            "ability_type": self.ability_type.value,
            "cooldown": self.cooldown,
            "priority": self.priority,
            "required_class": self.required_class.value if self.required_class else None,
            "effects": [
                {
                    "effect_type": eff.effect_type.value,
                    "value": eff.value,
                    "status_effect": eff.status_effect.value if eff.status_effect else None,
                    "probability": eff.probability,
                    "target": eff.target.value
                }
                for eff in self.effects
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ability':
        """
        Crea una habilidad desde un diccionario.

        Args:
            data: Diccionario con los atributos de la habilidad

        Returns:
            Nueva instancia de Ability
        """
        effects = []
        for eff_data in data["effects"]:
            effect = AbilityEffect(
                effect_type=AbilityType(eff_data["effect_type"]),
                value=eff_data.get("value", 0),
                status_effect=StatusEffect(eff_data["status_effect"]) if eff_data.get("status_effect") else None,
                probability=eff_data.get("probability", 1.0),
                target=AbilityTarget(eff_data.get("target", "opponent"))
            )
            effects.append(effect)

        return cls(
            name=data["name"],
            description=data["description"],
            ability_type=AbilityType(data["ability_type"]),
            effects=effects,
            cooldown=data.get("cooldown", 0),
            priority=data.get("priority", 0),
            required_class=CharacterClass(data["required_class"]) if data.get("required_class") else None
        )

    def __repr__(self) -> str:
        """Representación para debugging."""
        cd_str = f", CD: {self.current_cooldown}/{self.cooldown}" if self.cooldown > 0 else ""
        return f"Ability({self.name}, {self.ability_type.value}{cd_str})"

    def __str__(self) -> str:
        """Representación legible."""
        status = "Ready" if self.is_available() else f"Cooldown: {self.current_cooldown}"
        return f"{self.name} ({status})"


# Habilidades predefinidas comunes
def create_basic_abilities() -> Dict[str, Ability]:
    """
    Crea un conjunto de habilidades básicas predefinidas.

    Returns:
        Diccionario con habilidades comunes del juego

    Examples:
        >>> abilities = create_basic_abilities()
        >>> fireball = abilities["fireball"]
        >>> fireball.get_damage_value()
        40
    """
    abilities = {
        # Habilidades de daño puro
        "power_strike": Ability(
            name="Power Strike",
            description="Un golpe poderoso que causa gran daño",
            ability_type=AbilityType.DAMAGE,
            effects=[AbilityEffect(AbilityType.DAMAGE, value=50)],
            cooldown=1,
            priority=0
        ),

        "quick_attack": Ability(
            name="Quick Attack",
            description="Ataque rápido con prioridad alta",
            ability_type=AbilityType.DAMAGE,
            effects=[AbilityEffect(AbilityType.DAMAGE, value=30)],
            cooldown=0,
            priority=1
        ),

        # Habilidades con efectos de estado
        "fireball": Ability(
            name="Fireball",
            description="Bola de fuego que causa daño y puede quemar",
            ability_type=AbilityType.MIXED,
            effects=[
                AbilityEffect(AbilityType.DAMAGE, value=40),
                AbilityEffect(
                    AbilityType.STATUS,
                    status_effect=StatusEffect.BURN,
                    probability=0.3,
                    target=AbilityTarget.OPPONENT
                )
            ],
            cooldown=2,
            required_class=CharacterClass.MAGE
        ),

        "poison_strike": Ability(
            name="Poison Strike",
            description="Ataque envenenado que aplica poison",
            ability_type=AbilityType.MIXED,
            effects=[
                AbilityEffect(AbilityType.DAMAGE, value=30),
                AbilityEffect(
                    AbilityType.STATUS,
                    status_effect=StatusEffect.POISON,
                    probability=0.5,
                    target=AbilityTarget.OPPONENT
                )
            ],
            cooldown=2,
            required_class=CharacterClass.ROGUE
        ),

        "shield_bash": Ability(
            name="Shield Bash",
            description="Golpe con escudo que puede aturdir",
            ability_type=AbilityType.MIXED,
            effects=[
                AbilityEffect(AbilityType.DAMAGE, value=35),
                AbilityEffect(
                    AbilityType.STATUS,
                    status_effect=StatusEffect.STUN,
                    probability=0.2,
                    target=AbilityTarget.OPPONENT
                )
            ],
            cooldown=3,
            required_class=CharacterClass.TANK
        ),

        # Habilidades de curación
        "heal": Ability(
            name="Heal",
            description="Restaura HP del usuario",
            ability_type=AbilityType.HEAL,
            effects=[
                AbilityEffect(
                    AbilityType.HEAL,
                    value=40,
                    target=AbilityTarget.SELF
                )
            ],
            cooldown=3,
            required_class=CharacterClass.SUPPORT
        ),

        # Habilidades de buff
        "battle_cry": Ability(
            name="Battle Cry",
            description="Aumenta el ataque del usuario",
            ability_type=AbilityType.BUFF,
            effects=[
                AbilityEffect(
                    AbilityType.STATUS,
                    status_effect=StatusEffect.BUFF,
                    target=AbilityTarget.SELF
                )
            ],
            cooldown=4
        ),

        "iron_defense": Ability(
            name="Iron Defense",
            description="Crea un escudo protector",
            ability_type=AbilityType.BUFF,
            effects=[
                AbilityEffect(
                    AbilityType.STATUS,
                    status_effect=StatusEffect.SHIELD,
                    target=AbilityTarget.SELF
                )
            ],
            cooldown=3,
            required_class=CharacterClass.TANK
        ),

        # Habilidades de debuff
        "intimidate": Ability(
            name="Intimidate",
            description="Reduce el ataque del oponente",
            ability_type=AbilityType.DEBUFF,
            effects=[
                AbilityEffect(
                    AbilityType.STATUS,
                    status_effect=StatusEffect.DEBUFF,
                    target=AbilityTarget.OPPONENT
                )
            ],
            cooldown=3
        ),
    }

    return abilities
