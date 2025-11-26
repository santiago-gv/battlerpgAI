"""
Módulo de personajes para BattleRPG AI.

Define la clase Character que representa un personaje jugable en el combate.
Similar al sistema de Pokémon, cada personaje tiene clase, estadísticas y habilidades.
"""

from typing import List, Optional, Dict, TYPE_CHECKING
from dataclasses import dataclass

from src.core.stats import CharacterClass, StatusEffect, Stats, STATUS_EFFECT_CONFIG

if TYPE_CHECKING:
    from src.core.ability import Ability


@dataclass
class ActiveStatusEffect:
    """
    Representa un efecto de estado activo con duración.

    Attributes:
        effect: El tipo de efecto de estado
        duration: Turnos restantes del efecto
        stack_count: Contador para efectos apilables (ej: poison)
    """
    effect: StatusEffect
    duration: int
    stack_count: int = 0


class Character:
    """
    Representa un personaje del juego con sus atributos, habilidades y estado.

    Similar a un Pokémon, cada personaje tiene una clase (tipo), estadísticas,
    y puede aprender hasta 4 habilidades especiales.

    Attributes:
        name: Nombre único del personaje
        char_class: Clase del personaje (determina ventajas de tipo)
        stats: Estadísticas base (HP, ATK, DEF, SPD)
        current_hp: HP actual del personaje
        abilities: Lista de habilidades disponibles (máximo 4)
        active_effects: Efectos de estado activos con duración
        is_active: Si es el personaje activo en combate
        total_damage_dealt: Daño total infligido durante el combate
        total_damage_received: Daño total recibido durante el combate

    Examples:
        >>> stats = Stats(hp=100, attack=50, defense=20, speed=30)
        >>> char = Character("Warrior1", CharacterClass.WARRIOR, stats)
        >>> char.take_damage(30)
        10
        >>> char.current_hp
        90
    """

    def __init__(
        self,
        name: str,
        char_class: CharacterClass,
        stats: Stats,
        abilities: Optional[List['Ability']] = None
    ) -> None:
        """
        Inicializa un nuevo personaje.

        Args:
            name: Nombre único del personaje
            char_class: Clase del enum CharacterClass
            stats: Objeto Stats con estadísticas base
            abilities: Habilidades especiales (máx 4, como en Pokémon)

        Raises:
            ValueError: Si abilities contiene más de 4 habilidades
            TypeError: Si char_class no es una instancia de CharacterClass
        """
        if not isinstance(char_class, CharacterClass):
            raise TypeError(f"char_class debe ser CharacterClass, recibido: {type(char_class)}")

        if abilities and len(abilities) > 4:
            raise ValueError(f"Un personaje puede tener máximo 4 habilidades, recibido: {len(abilities)}")

        self.name = name
        self.char_class = char_class
        self.stats = stats
        self.current_hp = stats.hp
        self.abilities = abilities or []
        self.active_effects: List[ActiveStatusEffect] = []
        self.is_active = False

        # Estadísticas de combate
        self.total_damage_dealt = 0
        self.total_damage_received = 0

    def take_damage(self, damage: int) -> int:
        """
        Aplica daño al personaje considerando defensa y efectos de estado.

        La fórmula de daño es:
        - damage_after_defense = max(1, damage - defense)
        - Si tiene SHIELD: damage_final = damage_after_defense * 0.5
        - Actualiza current_hp y estadísticas

        Args:
            damage: Cantidad de daño base a aplicar

        Returns:
            Cantidad real de daño recibido después de defensa y efectos

        Examples:
            >>> char = Character("Test", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> char.take_damage(30)  # 30 - 20 defense = 10 damage
            10
            >>> char.current_hp
            90
        """
        # Calcular daño efectivo después de defensa
        damage_after_defense = max(1, damage - self.stats.defense)

        # Aplicar reducción de SHIELD si está activo
        if self.has_status_effect(StatusEffect.SHIELD):
            reduction = STATUS_EFFECT_CONFIG[StatusEffect.SHIELD]["damage_reduction"]
            damage_after_defense = int(damage_after_defense * (1 - reduction))
            damage_after_defense = max(1, damage_after_defense)

        # Aplicar daño
        actual_damage = min(damage_after_defense, self.current_hp)
        self.current_hp -= actual_damage
        self.total_damage_received += actual_damage

        return actual_damage

    def is_alive(self) -> bool:
        """
        Verifica si el personaje sigue en combate.

        Returns:
            True si current_hp > 0, False en caso contrario
        """
        return self.current_hp > 0

    def heal(self, amount: int) -> int:
        """
        Restaura HP al personaje.

        Args:
            amount: Cantidad de HP a restaurar

        Returns:
            Cantidad real de HP restaurado (no puede exceder max HP)

        Examples:
            >>> char = Character("Test", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> char.current_hp = 50
            >>> char.heal(30)
            30
            >>> char.current_hp
            80
            >>> char.heal(30)  # Solo puede curar hasta max_hp
            20
        """
        if not self.is_alive():
            return 0

        old_hp = self.current_hp
        self.current_hp = min(self.stats.hp, self.current_hp + amount)
        healed_amount = self.current_hp - old_hp

        return healed_amount

    def apply_status_effect(self, effect: StatusEffect) -> bool:
        """
        Aplica un efecto de estado al personaje.

        Si el efecto ya está activo, resetea su duración.
        Si es POISON, incrementa el stack_count.

        Args:
            effect: Efecto a aplicar

        Returns:
            True si se aplicó o actualizó exitosamente

        Examples:
            >>> char = Character("Test", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> char.apply_status_effect(StatusEffect.BURN)
            True
            >>> char.has_status_effect(StatusEffect.BURN)
            True
        """
        # Verificar si ya tiene el efecto
        for active_effect in self.active_effects:
            if active_effect.effect == effect:
                # Resetear duración
                active_effect.duration = STATUS_EFFECT_CONFIG[effect]["duration"]
                # Incrementar stack para poison
                if effect == StatusEffect.POISON:
                    active_effect.stack_count += 1
                return True

        # Agregar nuevo efecto
        duration = STATUS_EFFECT_CONFIG[effect]["duration"]
        new_effect = ActiveStatusEffect(
            effect=effect,
            duration=duration,
            stack_count=0
        )
        self.active_effects.append(new_effect)
        return True

    def has_status_effect(self, effect: StatusEffect) -> bool:
        """
        Verifica si el personaje tiene un efecto de estado activo.

        Args:
            effect: Efecto a verificar

        Returns:
            True si el efecto está activo, False en caso contrario
        """
        return any(active.effect == effect for active in self.active_effects)

    def remove_status_effect(self, effect: StatusEffect) -> bool:
        """
        Remueve un efecto de estado del personaje.

        Args:
            effect: Efecto a remover

        Returns:
            True si se removió el efecto, False si no lo tenía
        """
        for i, active_effect in enumerate(self.active_effects):
            if active_effect.effect == effect:
                self.active_effects.pop(i)
                return True
        return False

    def process_status_effects(self) -> Dict[StatusEffect, int]:
        """
        Procesa todos los efectos de estado activos al inicio del turno.

        Aplica daño de BURN y POISON, decrementa duraciones y remueve efectos expirados.

        Returns:
            Diccionario con el daño causado por cada efecto

        Examples:
            >>> char = Character("Test", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> char.apply_status_effect(StatusEffect.BURN)
            True
            >>> damage_dealt = char.process_status_effects()
            >>> damage_dealt[StatusEffect.BURN]
            5
        """
        damage_by_effect: Dict[StatusEffect, int] = {}
        effects_to_remove: List[StatusEffect] = []

        for active_effect in self.active_effects:
            effect_type = active_effect.effect

            # Aplicar daño de BURN
            if effect_type == StatusEffect.BURN:
                damage_percent = STATUS_EFFECT_CONFIG[StatusEffect.BURN]["damage_percent"]
                damage = int(self.stats.hp * damage_percent)
                actual_damage = min(damage, self.current_hp)
                self.current_hp -= actual_damage
                damage_by_effect[effect_type] = actual_damage

            # Aplicar daño de POISON (aumenta con el tiempo)
            elif effect_type == StatusEffect.POISON:
                config = STATUS_EFFECT_CONFIG[StatusEffect.POISON]
                initial_percent = config["initial_damage_percent"]
                increment = config["increment_percent"]
                damage_percent = initial_percent + (increment * active_effect.stack_count)
                damage = int(self.stats.hp * damage_percent)
                actual_damage = min(damage, self.current_hp)
                self.current_hp -= actual_damage
                damage_by_effect[effect_type] = actual_damage
                active_effect.stack_count += 1

            # Decrementar duración
            active_effect.duration -= 1

            # Marcar para remover si expiró
            if active_effect.duration <= 0:
                effects_to_remove.append(effect_type)

        # Remover efectos expirados
        for effect in effects_to_remove:
            self.remove_status_effect(effect)

        return damage_by_effect

    def get_effective_attack(self) -> int:
        """
        Calcula el ataque efectivo considerando efectos de estado.

        Returns:
            Ataque modificado por BUFF/DEBUFF

        Examples:
            >>> char = Character("Test", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> char.get_effective_attack()
            50
            >>> char.apply_status_effect(StatusEffect.BUFF)
            True
            >>> char.get_effective_attack()
            65
        """
        attack = self.stats.attack

        if self.has_status_effect(StatusEffect.BUFF):
            multiplier = STATUS_EFFECT_CONFIG[StatusEffect.BUFF]["attack_multiplier"]
            attack = int(attack * multiplier)

        if self.has_status_effect(StatusEffect.DEBUFF):
            multiplier = STATUS_EFFECT_CONFIG[StatusEffect.DEBUFF]["attack_multiplier"]
            attack = int(attack * multiplier)

        return attack

    def is_stunned(self) -> bool:
        """
        Verifica si el personaje está aturdido y no puede actuar.

        Returns:
            True si tiene el efecto STUN activo
        """
        return self.has_status_effect(StatusEffect.STUN)

    def get_hp_ratio(self) -> float:
        """
        Obtiene el ratio de HP actual respecto al máximo.

        Returns:
            Valor entre 0.0 y 1.0 representando el porcentaje de HP

        Examples:
            >>> char = Character("Test", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> char.current_hp = 50
            >>> char.get_hp_ratio()
            0.5
        """
        return self.current_hp / self.stats.hp if self.stats.hp > 0 else 0.0

    def reset_combat_stats(self) -> None:
        """
        Resetea las estadísticas de combate al finalizar una batalla.

        Limpia efectos de estado y restablece contadores.
        """
        self.active_effects.clear()
        self.is_active = False
        self.total_damage_dealt = 0
        self.total_damage_received = 0

    def __repr__(self) -> str:
        """Representación del personaje para debugging."""
        status = "Active" if self.is_active else "Bench"
        effects = f", Effects: {[e.effect.value for e in self.active_effects]}" if self.active_effects else ""
        return (f"Character({self.name}, {self.char_class.value}, "
                f"HP: {self.current_hp}/{self.stats.hp}, {status}{effects})")

    def __str__(self) -> str:
        """Representación legible del personaje."""
        return f"{self.name} ({self.char_class}) - {self.current_hp}/{self.stats.hp} HP"
