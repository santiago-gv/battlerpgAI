"""
Tests unitarios para el módulo Character.

Verifica el funcionamiento de personajes, stats y efectos de estado.
"""

import pytest
from src.core.character import Character
from src.core.stats import CharacterClass, StatusEffect, Stats


class TestStats:
    """Tests para la clase Stats."""

    def test_stats_creation_valid(self):
        """Test de creación válida de stats."""
        stats = Stats(hp=100, attack=50, defense=20, speed=30)
        assert stats.hp == 100
        assert stats.attack == 50
        assert stats.defense == 20
        assert stats.speed == 30

    def test_stats_invalid_hp(self):
        """Test de validación de HP inválido."""
        with pytest.raises(ValueError, match="HP debe ser positivo"):
            Stats(hp=0, attack=50, defense=20, speed=30)

    def test_stats_negative_attack(self):
        """Test de validación de ataque negativo."""
        with pytest.raises(ValueError, match="Attack no puede ser negativo"):
            Stats(hp=100, attack=-10, defense=20, speed=30)

    def test_stats_to_dict(self):
        """Test de conversión a diccionario."""
        stats = Stats(hp=100, attack=50, defense=20, speed=30)
        stats_dict = stats.to_dict()
        assert stats_dict == {
            "hp": 100,
            "attack": 50,
            "defense": 20,
            "speed": 30
        }

    def test_stats_from_dict(self):
        """Test de creación desde diccionario."""
        data = {"hp": 100, "attack": 50, "defense": 20, "speed": 30}
        stats = Stats.from_dict(data)
        assert stats.hp == 100
        assert stats.attack == 50


class TestCharacter:
    """Tests para la clase Character."""

    @pytest.fixture
    def basic_stats(self):
        """Fixture con stats básicas."""
        return Stats(hp=100, attack=50, defense=20, speed=30)

    @pytest.fixture
    def warrior(self, basic_stats):
        """Fixture con un personaje warrior básico."""
        return Character("Warrior1", CharacterClass.WARRIOR, basic_stats)

    def test_character_creation(self, warrior, basic_stats):
        """Test de creación de personaje."""
        assert warrior.name == "Warrior1"
        assert warrior.char_class == CharacterClass.WARRIOR
        assert warrior.current_hp == basic_stats.hp
        assert warrior.is_alive()
        assert not warrior.is_active

    def test_character_invalid_class(self, basic_stats):
        """Test de validación de clase inválida."""
        with pytest.raises(TypeError):
            Character("Test", "invalid_class", basic_stats)

    def test_character_too_many_abilities(self, basic_stats):
        """Test de validación de máximo 4 habilidades."""
        from src.core.ability import create_basic_abilities
        abilities = list(create_basic_abilities().values())[:5]
        with pytest.raises(ValueError, match="máximo 4 habilidades"):
            Character("Test", CharacterClass.WARRIOR, basic_stats, abilities)

    def test_take_damage(self, warrior):
        """Test de recibir daño."""
        initial_hp = warrior.current_hp
        damage_dealt = warrior.take_damage(30)
        # 30 - 20 defense = 10 damage
        assert damage_dealt == 10
        assert warrior.current_hp == initial_hp - 10
        assert warrior.is_alive()

    def test_take_damage_minimum(self, warrior):
        """Test de daño mínimo de 1."""
        warrior.stats.defense = 100
        damage_dealt = warrior.take_damage(10)
        assert damage_dealt == 1
        assert warrior.current_hp == 99

    def test_take_damage_kills_character(self, warrior):
        """Test de daño letal."""
        warrior.take_damage(200)
        assert warrior.current_hp == 0
        assert not warrior.is_alive()

    def test_take_damage_with_shield(self, warrior):
        """Test de daño reducido por shield."""
        warrior.apply_status_effect(StatusEffect.SHIELD)
        damage_dealt = warrior.take_damage(50)
        # (50 - 20 defense) * 0.5 shield = 15
        assert damage_dealt == 15

    def test_heal(self, warrior):
        """Test de curación."""
        warrior.current_hp = 50
        healed = warrior.heal(30)
        assert healed == 30
        assert warrior.current_hp == 80

    def test_heal_exceeds_max(self, warrior):
        """Test de curación que excede HP máximo."""
        warrior.current_hp = 90
        healed = warrior.heal(50)
        assert healed == 10
        assert warrior.current_hp == warrior.stats.hp

    def test_heal_dead_character(self, warrior):
        """Test de curación en personaje muerto."""
        warrior.current_hp = 0
        healed = warrior.heal(50)
        assert healed == 0
        assert warrior.current_hp == 0

    def test_apply_status_effect(self, warrior):
        """Test de aplicar efecto de estado."""
        result = warrior.apply_status_effect(StatusEffect.BURN)
        assert result is True
        assert warrior.has_status_effect(StatusEffect.BURN)

    def test_apply_duplicate_status_effect(self, warrior):
        """Test de aplicar efecto duplicado resetea duración."""
        warrior.apply_status_effect(StatusEffect.BURN)
        # Reducir duración artificialmente
        warrior.active_effects[0].duration = 1
        # Aplicar de nuevo
        warrior.apply_status_effect(StatusEffect.BURN)
        assert warrior.active_effects[0].duration == 3  # Duración reseteada

    def test_remove_status_effect(self, warrior):
        """Test de remover efecto de estado."""
        warrior.apply_status_effect(StatusEffect.BURN)
        result = warrior.remove_status_effect(StatusEffect.BURN)
        assert result is True
        assert not warrior.has_status_effect(StatusEffect.BURN)

    def test_process_burn_effect(self, warrior):
        """Test de procesamiento de efecto burn."""
        warrior.apply_status_effect(StatusEffect.BURN)
        damage_dict = warrior.process_status_effects()
        # Burn causa 5% de HP máximo
        expected_damage = int(warrior.stats.hp * 0.05)
        assert damage_dict[StatusEffect.BURN] == expected_damage
        assert warrior.current_hp == warrior.stats.hp - expected_damage

    def test_process_poison_effect(self, warrior):
        """Test de procesamiento de efecto poison."""
        warrior.apply_status_effect(StatusEffect.POISON)
        # Primer turno: 5% damage
        damage_dict = warrior.process_status_effects()
        expected_damage = int(warrior.stats.hp * 0.05)
        assert damage_dict[StatusEffect.POISON] == expected_damage

    def test_status_effect_expiration(self, warrior):
        """Test de expiración de efectos de estado."""
        warrior.apply_status_effect(StatusEffect.STUN)
        warrior.process_status_effects()
        # Stun dura 1 turno, debería expirar
        assert not warrior.has_status_effect(StatusEffect.STUN)

    def test_is_stunned(self, warrior):
        """Test de verificación de stun."""
        assert not warrior.is_stunned()
        warrior.apply_status_effect(StatusEffect.STUN)
        assert warrior.is_stunned()

    def test_get_effective_attack_with_buff(self, warrior):
        """Test de ataque efectivo con buff."""
        base_attack = warrior.get_effective_attack()
        assert base_attack == 50

        warrior.apply_status_effect(StatusEffect.BUFF)
        buffed_attack = warrior.get_effective_attack()
        assert buffed_attack == 65  # 50 * 1.3

    def test_get_effective_attack_with_debuff(self, warrior):
        """Test de ataque efectivo con debuff."""
        warrior.apply_status_effect(StatusEffect.DEBUFF)
        debuffed_attack = warrior.get_effective_attack()
        assert debuffed_attack == 35  # 50 * 0.7

    def test_get_hp_ratio(self, warrior):
        """Test de ratio de HP."""
        assert warrior.get_hp_ratio() == 1.0
        warrior.current_hp = 50
        assert warrior.get_hp_ratio() == 0.5
        warrior.current_hp = 0
        assert warrior.get_hp_ratio() == 0.0

    def test_reset_combat_stats(self, warrior):
        """Test de reseteo de stats de combate."""
        warrior.apply_status_effect(StatusEffect.BURN)
        warrior.is_active = True
        warrior.total_damage_dealt = 100
        warrior.total_damage_received = 50

        warrior.reset_combat_stats()

        assert len(warrior.active_effects) == 0
        assert not warrior.is_active
        assert warrior.total_damage_dealt == 0
        assert warrior.total_damage_received == 0

    def test_character_repr(self, warrior):
        """Test de representación del personaje."""
        repr_str = repr(warrior)
        assert "Warrior1" in repr_str
        assert "warrior" in repr_str

    def test_character_str(self, warrior):
        """Test de string del personaje."""
        str_rep = str(warrior)
        assert "Warrior1" in str_rep
        assert "100/100" in str_rep


class TestCharacterIntegration:
    """Tests de integración para Character."""

    @pytest.fixture
    def warrior(self):
        """Fixture con warrior."""
        return Character(
            "Warrior",
            CharacterClass.WARRIOR,
            Stats(hp=100, attack=50, defense=20, speed=30)
        )

    @pytest.fixture
    def mage(self):
        """Fixture con mage."""
        return Character(
            "Mage",
            CharacterClass.MAGE,
            Stats(hp=80, attack=60, defense=10, speed=40)
        )

    def test_combat_scenario(self, warrior, mage):
        """Test de escenario de combate completo."""
        # Warrior ataca a Mage
        damage = 50 - 10  # attack - defense
        actual_damage = mage.take_damage(50)
        assert actual_damage == max(1, damage)
        assert mage.is_alive()

        # Mage aplica burn a Warrior
        warrior.apply_status_effect(StatusEffect.BURN)
        warrior.process_status_effects()
        assert warrior.current_hp < 100

        # Warrior se cura
        healed = warrior.heal(20)
        assert healed > 0

    def test_status_effect_stacking(self, warrior):
        """Test de múltiples efectos de estado."""
        warrior.apply_status_effect(StatusEffect.BURN)
        warrior.apply_status_effect(StatusEffect.DEBUFF)
        warrior.apply_status_effect(StatusEffect.SHIELD)

        assert warrior.has_status_effect(StatusEffect.BURN)
        assert warrior.has_status_effect(StatusEffect.DEBUFF)
        assert warrior.has_status_effect(StatusEffect.SHIELD)

        # Procesar efectos
        warrior.process_status_effects()

        # Shield debería estar activo (dura 2 turnos)
        assert warrior.has_status_effect(StatusEffect.SHIELD)
