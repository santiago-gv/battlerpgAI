"""
Módulo de sistema de tipos para BattleRPG AI.

Implementa el sistema de ventajas de tipo similar a Pokémon, donde ciertas
clases tienen ventaja sobre otras (rock-paper-scissors extendido).
"""

from typing import Dict, Tuple
from enum import Enum

from src.core.stats import CharacterClass


class TypeEffectiveness(Enum):
    """
    Niveles de efectividad de tipo.

    Define los multiplicadores de daño según ventaja de tipo.
    """
    SUPER_EFFECTIVE = 1.5   # Súper efectivo
    NORMAL = 1.0            # Efectividad normal
    NOT_VERY_EFFECTIVE = 0.5  # No muy efectivo
    IMMUNE = 0.0            # Inmune (no implementado en MVP)

    def __str__(self) -> str:
        """Retorna descripción legible."""
        return self.name.replace("_", " ").title()


class TypeSystem:
    """
    Sistema de ventajas de tipo para el combate.

    Implementa la tabla de efectividad entre clases:
    - WARRIOR > ROGUE (Warriors son fuertes contra Rogues)
    - ROGUE > MAGE (Rogues son fuertes contra Mages)
    - MAGE > WARRIOR (Mages son fuertes contra Warriors)
    - TANK: Resistente a WARRIOR y ROGUE
    - SUPPORT: Neutral contra todos

    Attributes:
        effectiveness_table: Tabla con multiplicadores de daño

    Examples:
        >>> type_sys = TypeSystem()
        >>> multiplier = type_sys.get_multiplier(CharacterClass.WARRIOR, CharacterClass.ROGUE)
        >>> multiplier
        1.5
        >>> type_sys.get_advantage(CharacterClass.WARRIOR, CharacterClass.ROGUE)
        <TypeEffectiveness.SUPER_EFFECTIVE: 1.5>
    """

    def __init__(self) -> None:
        """
        Inicializa el sistema de tipos con la tabla de efectividad.

        La tabla está organizada como:
        effectiveness_table[(atacante, defensor)] = multiplicador
        """
        self.effectiveness_table: Dict[Tuple[CharacterClass, CharacterClass], float] = {}
        self._initialize_effectiveness_table()

    def _initialize_effectiveness_table(self) -> None:
        """
        Inicializa la tabla de efectividad de tipos.

        Establece todas las relaciones de ventaja/desventaja entre clases.
        """
        # Valores por defecto (neutral)
        for attacker in CharacterClass:
            for defender in CharacterClass:
                self.effectiveness_table[(attacker, defender)] = TypeEffectiveness.NORMAL.value

        # Ciclo básico: WARRIOR > ROGUE > MAGE > WARRIOR

        # WARRIOR vs otros
        self.effectiveness_table[(CharacterClass.WARRIOR, CharacterClass.ROGUE)] = \
            TypeEffectiveness.SUPER_EFFECTIVE.value
        self.effectiveness_table[(CharacterClass.WARRIOR, CharacterClass.MAGE)] = \
            TypeEffectiveness.NOT_VERY_EFFECTIVE.value

        # ROGUE vs otros
        self.effectiveness_table[(CharacterClass.ROGUE, CharacterClass.MAGE)] = \
            TypeEffectiveness.SUPER_EFFECTIVE.value
        self.effectiveness_table[(CharacterClass.ROGUE, CharacterClass.WARRIOR)] = \
            TypeEffectiveness.NOT_VERY_EFFECTIVE.value

        # MAGE vs otros
        self.effectiveness_table[(CharacterClass.MAGE, CharacterClass.WARRIOR)] = \
            TypeEffectiveness.SUPER_EFFECTIVE.value
        self.effectiveness_table[(CharacterClass.MAGE, CharacterClass.ROGUE)] = \
            TypeEffectiveness.NOT_VERY_EFFECTIVE.value

        # TANK: Resistente a WARRIOR y ROGUE
        self.effectiveness_table[(CharacterClass.WARRIOR, CharacterClass.TANK)] = \
            TypeEffectiveness.NOT_VERY_EFFECTIVE.value
        self.effectiveness_table[(CharacterClass.ROGUE, CharacterClass.TANK)] = \
            TypeEffectiveness.NOT_VERY_EFFECTIVE.value
        # TANK hace daño normal a todos (neutral)

        # MAGE es efectivo contra TANK (para balance)
        self.effectiveness_table[(CharacterClass.MAGE, CharacterClass.TANK)] = \
            TypeEffectiveness.SUPER_EFFECTIVE.value

        # SUPPORT: Neutral contra todos (ya está inicializado en neutral)
        # Todos son neutrales contra SUPPORT

    def get_multiplier(
        self,
        attacker_class: CharacterClass,
        defender_class: CharacterClass
    ) -> float:
        """
        Obtiene el multiplicador de daño según las clases.

        Args:
            attacker_class: Clase del atacante
            defender_class: Clase del defensor

        Returns:
            Multiplicador de daño (0.5, 1.0, o 1.5)

        Examples:
            >>> type_sys = TypeSystem()
            >>> type_sys.get_multiplier(CharacterClass.WARRIOR, CharacterClass.ROGUE)
            1.5
            >>> type_sys.get_multiplier(CharacterClass.WARRIOR, CharacterClass.MAGE)
            0.5
            >>> type_sys.get_multiplier(CharacterClass.SUPPORT, CharacterClass.TANK)
            1.0
        """
        return self.effectiveness_table.get(
            (attacker_class, defender_class),
            TypeEffectiveness.NORMAL.value
        )

    def get_advantage(
        self,
        attacker_class: CharacterClass,
        defender_class: CharacterClass
    ) -> TypeEffectiveness:
        """
        Obtiene el tipo de ventaja entre dos clases.

        Args:
            attacker_class: Clase del atacante
            defender_class: Clase del defensor

        Returns:
            Enum TypeEffectiveness indicando la ventaja

        Examples:
            >>> type_sys = TypeSystem()
            >>> advantage = type_sys.get_advantage(CharacterClass.WARRIOR, CharacterClass.ROGUE)
            >>> advantage == TypeEffectiveness.SUPER_EFFECTIVE
            True
        """
        multiplier = self.get_multiplier(attacker_class, defender_class)

        if multiplier >= TypeEffectiveness.SUPER_EFFECTIVE.value:
            return TypeEffectiveness.SUPER_EFFECTIVE
        elif multiplier <= TypeEffectiveness.NOT_VERY_EFFECTIVE.value:
            return TypeEffectiveness.NOT_VERY_EFFECTIVE
        else:
            return TypeEffectiveness.NORMAL

    def has_advantage(
        self,
        attacker_class: CharacterClass,
        defender_class: CharacterClass
    ) -> bool:
        """
        Verifica si el atacante tiene ventaja de tipo.

        Args:
            attacker_class: Clase del atacante
            defender_class: Clase del defensor

        Returns:
            True si tiene ventaja (multiplicador > 1.0)

        Examples:
            >>> type_sys = TypeSystem()
            >>> type_sys.has_advantage(CharacterClass.WARRIOR, CharacterClass.ROGUE)
            True
            >>> type_sys.has_advantage(CharacterClass.WARRIOR, CharacterClass.MAGE)
            False
        """
        return self.get_multiplier(attacker_class, defender_class) > TypeEffectiveness.NORMAL.value

    def has_disadvantage(
        self,
        attacker_class: CharacterClass,
        defender_class: CharacterClass
    ) -> bool:
        """
        Verifica si el atacante tiene desventaja de tipo.

        Args:
            attacker_class: Clase del atacante
            defender_class: Clase del defensor

        Returns:
            True si tiene desventaja (multiplicador < 1.0)

        Examples:
            >>> type_sys = TypeSystem()
            >>> type_sys.has_disadvantage(CharacterClass.WARRIOR, CharacterClass.MAGE)
            True
            >>> type_sys.has_disadvantage(CharacterClass.WARRIOR, CharacterClass.ROGUE)
            False
        """
        return self.get_multiplier(attacker_class, defender_class) < TypeEffectiveness.NORMAL.value

    def is_neutral(
        self,
        attacker_class: CharacterClass,
        defender_class: CharacterClass
    ) -> bool:
        """
        Verifica si la interacción es neutral (sin ventaja).

        Args:
            attacker_class: Clase del atacante
            defender_class: Clase del defensor

        Returns:
            True si es neutral (multiplicador == 1.0)

        Examples:
            >>> type_sys = TypeSystem()
            >>> type_sys.is_neutral(CharacterClass.SUPPORT, CharacterClass.MAGE)
            True
        """
        return self.get_multiplier(attacker_class, defender_class) == TypeEffectiveness.NORMAL.value

    def get_advantage_score(
        self,
        attacker_class: CharacterClass,
        defender_class: CharacterClass
    ) -> int:
        """
        Obtiene un score numérico de la ventaja de tipo.

        Útil para agentes de IA que necesitan evaluar ventajas.

        Args:
            attacker_class: Clase del atacante
            defender_class: Clase del defensor

        Returns:
            +1 para ventaja, 0 para neutral, -1 para desventaja

        Examples:
            >>> type_sys = TypeSystem()
            >>> type_sys.get_advantage_score(CharacterClass.WARRIOR, CharacterClass.ROGUE)
            1
            >>> type_sys.get_advantage_score(CharacterClass.WARRIOR, CharacterClass.MAGE)
            -1
            >>> type_sys.get_advantage_score(CharacterClass.SUPPORT, CharacterClass.TANK)
            0
        """
        multiplier = self.get_multiplier(attacker_class, defender_class)

        if multiplier > TypeEffectiveness.NORMAL.value:
            return 1
        elif multiplier < TypeEffectiveness.NORMAL.value:
            return -1
        else:
            return 0

    def get_best_matchup(
        self,
        attacker_class: CharacterClass
    ) -> CharacterClass:
        """
        Encuentra la clase contra la que el atacante tiene mayor ventaja.

        Args:
            attacker_class: Clase del atacante

        Returns:
            Clase contra la que tiene mayor ventaja

        Examples:
            >>> type_sys = TypeSystem()
            >>> best = type_sys.get_best_matchup(CharacterClass.WARRIOR)
            >>> best == CharacterClass.ROGUE
            True
        """
        best_class = CharacterClass.WARRIOR
        best_multiplier = 0.0

        for defender_class in CharacterClass:
            multiplier = self.get_multiplier(attacker_class, defender_class)
            if multiplier > best_multiplier:
                best_multiplier = multiplier
                best_class = defender_class

        return best_class

    def get_worst_matchup(
        self,
        attacker_class: CharacterClass
    ) -> CharacterClass:
        """
        Encuentra la clase contra la que el atacante tiene mayor desventaja.

        Args:
            attacker_class: Clase del atacante

        Returns:
            Clase contra la que tiene mayor desventaja

        Examples:
            >>> type_sys = TypeSystem()
            >>> worst = type_sys.get_worst_matchup(CharacterClass.WARRIOR)
            >>> worst == CharacterClass.MAGE
            True
        """
        worst_class = CharacterClass.WARRIOR
        worst_multiplier = float('inf')

        for defender_class in CharacterClass:
            multiplier = self.get_multiplier(attacker_class, defender_class)
            if multiplier < worst_multiplier:
                worst_multiplier = multiplier
                worst_class = defender_class

        return worst_class

    def print_effectiveness_table(self) -> str:
        """
        Genera una representación de la tabla de efectividad.

        Returns:
            String con la tabla formateada

        Examples:
            >>> type_sys = TypeSystem()
            >>> print(type_sys.print_effectiveness_table())
            Type Effectiveness Table:
            ...
        """
        lines = ["Type Effectiveness Table:", "=" * 60]

        for attacker in CharacterClass:
            lines.append(f"\n{attacker.value.upper()} attacking:")
            for defender in CharacterClass:
                multiplier = self.get_multiplier(attacker, defender)
                advantage = self.get_advantage(attacker, defender)
                lines.append(
                    f"  vs {defender.value:8} -> {multiplier:.1f}x ({advantage.name})"
                )

        return "\n".join(lines)


# Instancia global del sistema de tipos (singleton)
_type_system_instance: TypeSystem = None


def get_type_system() -> TypeSystem:
    """
    Obtiene la instancia singleton del sistema de tipos.

    Returns:
        Instancia global de TypeSystem

    Examples:
        >>> type_sys = get_type_system()
        >>> type_sys.get_multiplier(CharacterClass.WARRIOR, CharacterClass.ROGUE)
        1.5
    """
    global _type_system_instance
    if _type_system_instance is None:
        _type_system_instance = TypeSystem()
    return _type_system_instance
