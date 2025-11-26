"""
Módulo de cálculo de daño para BattleRPG AI.

Implementa las fórmulas de daño considerando ataque, defensa, ventajas de tipo,
efectos de estado y variación aleatoria.
"""

import random
from typing import Optional
from dataclasses import dataclass

from src.core.character import Character
from src.core.ability import Ability, AbilityType, AbilityEffect
from src.engine.type_system import get_type_system


@dataclass
class DamageResult:
    """
    Resultado de un cálculo de daño.

    Contiene información detallada sobre el daño calculado y aplicado.

    Attributes:
        base_damage: Daño base antes de modificadores
        type_multiplier: Multiplicador de ventaja de tipo
        final_damage: Daño final aplicado
        was_critical: Si fue golpe crítico (no implementado en MVP)
        effectiveness: Descripción de la efectividad ("Super effective!", "Normal", etc.)
    """
    base_damage: int
    type_multiplier: float
    final_damage: int
    was_critical: bool = False
    effectiveness: str = "Normal"


class DamageCalculator:
    """
    Calculadora de daño para el sistema de combate.

    Implementa las fórmulas de daño siguiendo el estándar de Pokémon:
    1. Calcular daño base (ataque + modificadores)
    2. Aplicar ventaja de tipo
    3. Aplicar defensa
    4. Agregar variación aleatoria

    Attributes:
        type_system: Sistema de ventajas de tipo
        random_variance: Rango de variación aleatoria (por defecto ±10%)
        use_random_variance: Si aplicar variación aleatoria (útil para tests)

    Examples:
        >>> calc = DamageCalculator()
        >>> attacker = Character("Warrior", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
        >>> defender = Character("Rogue", CharacterClass.ROGUE, Stats(90, 45, 15, 35))
        >>> result = calc.calculate_basic_attack_damage(attacker, defender)
        >>> result.final_damage > 0
        True
    """

    def __init__(
        self,
        random_variance: float = 0.1,
        use_random_variance: bool = True
    ) -> None:
        """
        Inicializa el calculador de daño.

        Args:
            random_variance: Rango de variación aleatoria (0.1 = ±10%)
            use_random_variance: Si aplicar variación aleatoria
        """
        self.type_system = get_type_system()
        self.random_variance = random_variance
        self.use_random_variance = use_random_variance

    def calculate_basic_attack_damage(
        self,
        attacker: Character,
        defender: Character
    ) -> DamageResult:
        """
        Calcula el daño de un ataque básico.

        Fórmula:
        1. base_damage = attacker.get_effective_attack()
        2. typed_damage = base_damage * type_multiplier
        3. final_damage = max(1, typed_damage - defender.defense)
        4. final_damage *= random.uniform(0.9, 1.1)

        Args:
            attacker: Personaje atacante
            defender: Personaje defensor

        Returns:
            DamageResult con información del daño calculado

        Examples:
            >>> calc = DamageCalculator(use_random_variance=False)
            >>> attacker = Character("Test1", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> defender = Character("Test2", CharacterClass.ROGUE, Stats(100, 40, 20, 25))
            >>> result = calc.calculate_basic_attack_damage(attacker, defender)
            >>> result.type_multiplier
            1.5
        """
        # Obtener ataque efectivo (considerando buffs/debuffs)
        base_damage = attacker.get_effective_attack()

        # Obtener multiplicador de tipo
        type_multiplier = self.type_system.get_multiplier(
            attacker.char_class,
            defender.char_class
        )

        # Aplicar ventaja de tipo
        typed_damage = int(base_damage * type_multiplier)

        # Aplicar defensa del defensor
        damage_after_defense = max(1, typed_damage - defender.stats.defense)

        # Aplicar variación aleatoria si está habilitado
        if self.use_random_variance:
            variance_min = 1.0 - self.random_variance
            variance_max = 1.0 + self.random_variance
            random_factor = random.uniform(variance_min, variance_max)
            final_damage = int(damage_after_defense * random_factor)
        else:
            final_damage = damage_after_defense

        # Asegurar que el daño mínimo es 1
        final_damage = max(1, final_damage)

        # Determinar efectividad
        effectiveness = self._get_effectiveness_text(type_multiplier)

        return DamageResult(
            base_damage=base_damage,
            type_multiplier=type_multiplier,
            final_damage=final_damage,
            was_critical=False,
            effectiveness=effectiveness
        )

    def calculate_ability_damage(
        self,
        attacker: Character,
        defender: Character,
        ability: Ability
    ) -> DamageResult:
        """
        Calcula el daño de una habilidad.

        Similar al ataque básico pero usa el daño base de la habilidad.

        Args:
            attacker: Personaje atacante
            defender: Personaje defensor
            ability: Habilidad usada

        Returns:
            DamageResult con información del daño calculado

        Examples:
            >>> calc = DamageCalculator(use_random_variance=False)
            >>> attacker = Character("Test1", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> defender = Character("Test2", CharacterClass.ROGUE, Stats(100, 40, 20, 25))
            >>> from src.core.ability import Ability, AbilityType, AbilityEffect
            >>> ability = Ability("Strike", "Test", AbilityType.DAMAGE,
            ...                   [AbilityEffect(AbilityType.DAMAGE, value=40)])
            >>> result = calc.calculate_ability_damage(attacker, defender, ability)
            >>> result.base_damage
            40
        """
        # Obtener daño base de la habilidad
        base_damage = ability.get_damage_value()

        # Obtener multiplicador de tipo
        type_multiplier = self.type_system.get_multiplier(
            attacker.char_class,
            defender.char_class
        )

        # Aplicar ventaja de tipo
        typed_damage = int(base_damage * type_multiplier)

        # Aplicar defensa del defensor
        damage_after_defense = max(1, typed_damage - defender.stats.defense)

        # Aplicar variación aleatoria si está habilitado
        if self.use_random_variance:
            variance_min = 1.0 - self.random_variance
            variance_max = 1.0 + self.random_variance
            random_factor = random.uniform(variance_min, variance_max)
            final_damage = int(damage_after_defense * random_factor)
        else:
            final_damage = damage_after_defense

        # Asegurar que el daño mínimo es 1
        final_damage = max(1, final_damage)

        # Determinar efectividad
        effectiveness = self._get_effectiveness_text(type_multiplier)

        return DamageResult(
            base_damage=base_damage,
            type_multiplier=type_multiplier,
            final_damage=final_damage,
            was_critical=False,
            effectiveness=effectiveness
        )

    def apply_damage(
        self,
        attacker: Character,
        defender: Character,
        damage_result: DamageResult
    ) -> int:
        """
        Aplica el daño calculado al defensor.

        Args:
            attacker: Personaje atacante
            defender: Personaje defensor
            damage_result: Resultado del cálculo de daño

        Returns:
            Cantidad real de daño aplicado

        Examples:
            >>> calc = DamageCalculator()
            >>> attacker = Character("Test1", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> defender = Character("Test2", CharacterClass.ROGUE, Stats(100, 40, 20, 25))
            >>> result = calc.calculate_basic_attack_damage(attacker, defender)
            >>> actual_damage = calc.apply_damage(attacker, defender, result)
            >>> actual_damage > 0
            True
        """
        actual_damage = defender.take_damage(damage_result.final_damage)
        attacker.total_damage_dealt += actual_damage
        return actual_damage

    def calculate_and_apply_damage(
        self,
        attacker: Character,
        defender: Character,
        ability: Optional[Ability] = None
    ) -> DamageResult:
        """
        Calcula y aplica daño en una sola operación.

        Método de conveniencia que combina cálculo y aplicación.

        Args:
            attacker: Personaje atacante
            defender: Personaje defensor
            ability: Habilidad usada (None para ataque básico)

        Returns:
            DamageResult con el daño calculado y aplicado

        Examples:
            >>> calc = DamageCalculator()
            >>> attacker = Character("Test1", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> defender = Character("Test2", CharacterClass.ROGUE, Stats(100, 40, 20, 25))
            >>> defender_hp = defender.current_hp
            >>> result = calc.calculate_and_apply_damage(attacker, defender)
            >>> defender.current_hp < defender_hp
            True
        """
        # Calcular daño
        if ability is None:
            damage_result = self.calculate_basic_attack_damage(attacker, defender)
        else:
            damage_result = self.calculate_ability_damage(attacker, defender, ability)

        # Aplicar daño
        actual_damage = self.apply_damage(attacker, defender, damage_result)

        # Actualizar con el daño real aplicado
        damage_result.final_damage = actual_damage

        return damage_result

    def calculate_heal(
        self,
        target: Character,
        heal_amount: int
    ) -> int:
        """
        Calcula y aplica curación a un personaje.

        Args:
            target: Personaje a curar
            heal_amount: Cantidad de HP a restaurar

        Returns:
            Cantidad real de HP restaurado

        Examples:
            >>> calc = DamageCalculator()
            >>> target = Character("Test", CharacterClass.SUPPORT, Stats(100, 40, 20, 30))
            >>> target.current_hp = 50
            >>> healed = calc.calculate_heal(target, 30)
            >>> healed
            30
            >>> target.current_hp
            80
        """
        return target.heal(heal_amount)

    def _get_effectiveness_text(self, type_multiplier: float) -> str:
        """
        Obtiene el texto descriptivo de la efectividad.

        Args:
            type_multiplier: Multiplicador de tipo

        Returns:
            Texto descriptivo ("Super effective!", "Not very effective...", "Normal")
        """
        if type_multiplier >= 1.5:
            return "Super effective!"
        elif type_multiplier <= 0.5:
            return "Not very effective..."
        else:
            return "Normal"

    def estimate_damage(
        self,
        attacker: Character,
        defender: Character,
        ability: Optional[Ability] = None
    ) -> tuple[int, int]:
        """
        Estima el rango de daño sin aplicarlo.

        Útil para que los agentes de IA evalúen opciones.

        Args:
            attacker: Personaje atacante
            defender: Personaje defensor
            ability: Habilidad a usar (None para ataque básico)

        Returns:
            Tupla (daño_mínimo, daño_máximo) considerando variación aleatoria

        Examples:
            >>> calc = DamageCalculator()
            >>> attacker = Character("Test1", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> defender = Character("Test2", CharacterClass.ROGUE, Stats(100, 40, 20, 25))
            >>> min_dmg, max_dmg = calc.estimate_damage(attacker, defender)
            >>> min_dmg <= max_dmg
            True
        """
        # Deshabilitar variación temporalmente
        original_variance = self.use_random_variance
        self.use_random_variance = False

        # Calcular daño base
        if ability is None:
            result = self.calculate_basic_attack_damage(attacker, defender)
        else:
            result = self.calculate_ability_damage(attacker, defender, ability)

        base_damage = result.final_damage

        # Restaurar configuración
        self.use_random_variance = original_variance

        # Calcular rango con variación
        if original_variance:
            min_damage = int(base_damage * (1.0 - self.random_variance))
            max_damage = int(base_damage * (1.0 + self.random_variance))
        else:
            min_damage = base_damage
            max_damage = base_damage

        # Asegurar mínimo de 1
        min_damage = max(1, min_damage)
        max_damage = max(1, max_damage)

        return (min_damage, max_damage)
