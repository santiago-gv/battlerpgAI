"""
Tests unitarios para el módulo Team.

Verifica el funcionamiento de equipos y cambios de personajes.
"""

import pytest
from src.core.character import Character
from src.core.team import Team
from src.core.stats import CharacterClass, Stats


class TestTeam:
    """Tests para la clase Team."""

    @pytest.fixture
    def three_characters(self):
        """Fixture con tres personajes."""
        char1 = Character("Warrior", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
        char2 = Character("Mage", CharacterClass.MAGE, Stats(80, 60, 10, 40))
        char3 = Character("Rogue", CharacterClass.ROGUE, Stats(90, 55, 15, 45))
        return [char1, char2, char3]

    @pytest.fixture
    def basic_team(self, three_characters):
        """Fixture con un equipo básico."""
        return Team(three_characters)

    def test_team_creation(self, three_characters):
        """Test de creación de equipo."""
        team = Team(three_characters, team_name="TestTeam")
        assert len(team) == 3
        assert team.team_name == "TestTeam"
        assert team.active_index == 0
        assert team.characters[0].is_active
        assert not team.characters[1].is_active

    def test_team_wrong_size(self):
        """Test de validación de tamaño de equipo."""
        char1 = Character("A", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
        char2 = Character("B", CharacterClass.MAGE, Stats(80, 60, 10, 40))

        with pytest.raises(ValueError, match="exactamente 3 personajes"):
            Team([char1, char2])

        with pytest.raises(ValueError, match="exactamente 3 personajes"):
            Team([char1])

    def test_team_invalid_character(self, three_characters):
        """Test de validación de tipo de personaje."""
        three_characters[1] = "not a character"
        with pytest.raises(TypeError, match="no es un Character"):
            Team(three_characters)

    def test_active_character_property(self, basic_team):
        """Test de propiedad active_character."""
        active = basic_team.active_character
        assert active.name == "Warrior"
        assert active.is_active

    def test_switch_character(self, basic_team):
        """Test de cambio de personaje."""
        result = basic_team.switch_character(1)
        assert result is True
        assert basic_team.active_index == 1
        assert basic_team.active_character.name == "Mage"
        assert not basic_team.characters[0].is_active
        assert basic_team.characters[1].is_active

    def test_switch_to_same_character(self, basic_team):
        """Test de cambio al mismo personaje (no permitido)."""
        result = basic_team.switch_character(0)
        assert result is False
        assert basic_team.active_index == 0

    def test_switch_out_of_bounds(self, basic_team):
        """Test de cambio con índice fuera de rango."""
        assert basic_team.switch_character(-1) is False
        assert basic_team.switch_character(3) is False
        assert basic_team.switch_character(10) is False

    def test_switch_to_fainted_character(self, basic_team):
        """Test de cambio a personaje derrotado."""
        basic_team.characters[1].current_hp = 0
        result = basic_team.switch_character(1)
        assert result is False
        assert basic_team.active_index == 0

    def test_switch_to_character_by_name(self, basic_team):
        """Test de cambio por nombre."""
        result = basic_team.switch_to_character("Rogue")
        assert result is True
        assert basic_team.active_character.name == "Rogue"

    def test_switch_to_nonexistent_name(self, basic_team):
        """Test de cambio a nombre inexistente."""
        result = basic_team.switch_to_character("Nonexistent")
        assert result is False

    def test_auto_switch_on_faint(self, basic_team):
        """Test de cambio automático cuando el activo cae."""
        basic_team.characters[0].current_hp = 0
        new_active = basic_team.auto_switch_on_faint()
        assert new_active is not None
        assert new_active.name == "Mage"
        assert basic_team.active_index == 1

    def test_auto_switch_when_active_alive(self, basic_team):
        """Test de auto-switch cuando el activo está vivo."""
        active = basic_team.auto_switch_on_faint()
        assert active.name == "Warrior"
        assert basic_team.active_index == 0

    def test_auto_switch_all_fainted(self, basic_team):
        """Test de auto-switch cuando todos están derrotados."""
        for char in basic_team.characters:
            char.current_hp = 0
        result = basic_team.auto_switch_on_faint()
        assert result is None

    def test_is_defeated(self, basic_team):
        """Test de verificación de equipo derrotado."""
        assert not basic_team.is_defeated()

        basic_team.characters[0].current_hp = 0
        assert not basic_team.is_defeated()

        basic_team.characters[1].current_hp = 0
        assert not basic_team.is_defeated()

        basic_team.characters[2].current_hp = 0
        assert basic_team.is_defeated()

    def test_get_alive_characters(self, basic_team):
        """Test de obtener personajes vivos."""
        alive = basic_team.get_alive_characters()
        assert len(alive) == 3

        basic_team.characters[0].current_hp = 0
        alive = basic_team.get_alive_characters()
        assert len(alive) == 2
        assert "Warrior" not in [c.name for c in alive]

    def test_get_alive_count(self, basic_team):
        """Test de contar personajes vivos."""
        assert basic_team.get_alive_count() == 3

        basic_team.characters[0].current_hp = 0
        assert basic_team.get_alive_count() == 2

        basic_team.characters[1].current_hp = 0
        basic_team.characters[2].current_hp = 0
        assert basic_team.get_alive_count() == 0

    def test_get_defeated_characters(self, basic_team):
        """Test de obtener personajes derrotados."""
        defeated = basic_team.get_defeated_characters()
        assert len(defeated) == 0

        basic_team.characters[0].current_hp = 0
        defeated = basic_team.get_defeated_characters()
        assert len(defeated) == 1
        assert defeated[0].name == "Warrior"

    def test_get_character_by_name(self, basic_team):
        """Test de buscar personaje por nombre."""
        char = basic_team.get_character_by_name("Mage")
        assert char is not None
        assert char.name == "Mage"

        char = basic_team.get_character_by_name("Nonexistent")
        assert char is None

    def test_get_character_index(self, basic_team):
        """Test de obtener índice de personaje."""
        char = basic_team.characters[1]
        index = basic_team.get_character_index(char)
        assert index == 1

    def test_get_character_index_not_in_team(self, basic_team):
        """Test de índice de personaje no perteneciente."""
        other_char = Character("Other", CharacterClass.TANK, Stats(120, 40, 30, 20))
        index = basic_team.get_character_index(other_char)
        assert index is None

    def test_get_total_hp(self, basic_team):
        """Test de calcular HP total."""
        total = basic_team.get_total_hp()
        expected = 100 + 80 + 90
        assert total == expected

        basic_team.characters[0].current_hp = 50
        total = basic_team.get_total_hp()
        expected = 50 + 80 + 90
        assert total == expected

    def test_get_total_hp_ratio(self, basic_team):
        """Test de ratio de HP total."""
        ratio = basic_team.get_total_hp_ratio()
        assert ratio == 1.0

        basic_team.characters[0].current_hp = 50
        ratio = basic_team.get_total_hp_ratio()
        # Total: 50 + 80 + 90 = 220 / 270
        assert 0.8 < ratio < 0.82

    def test_reset_all_combat_stats(self, basic_team):
        """Test de reseteo de stats de combate."""
        for char in basic_team.characters:
            char.total_damage_dealt = 100
            char.is_active = True

        basic_team.reset_all_combat_stats()

        for char in basic_team.characters:
            assert char.total_damage_dealt == 0
            assert not char.is_active

    def test_heal_all(self, basic_team):
        """Test de curación de todo el equipo."""
        for char in basic_team.characters:
            char.current_hp = char.stats.hp // 2

        total_healed = basic_team.heal_all(30)
        assert total_healed == 90  # 30 * 3 personajes

    def test_revive_all(self, basic_team):
        """Test de revivir todo el equipo."""
        for char in basic_team.characters:
            char.current_hp = 0

        basic_team.revive_all()

        for char in basic_team.characters:
            assert char.is_alive()
            assert char.current_hp == char.stats.hp // 2

    def test_getitem(self, basic_team):
        """Test de acceso por índice."""
        assert basic_team[0].name == "Warrior"
        assert basic_team[1].name == "Mage"
        assert basic_team[2].name == "Rogue"

    def test_len(self, basic_team):
        """Test de longitud del equipo."""
        assert len(basic_team) == 3

    def test_repr(self, basic_team):
        """Test de representación del equipo."""
        repr_str = repr(basic_team)
        assert "Team" in repr_str
        assert "3/3 alive" in repr_str

    def test_str(self, basic_team):
        """Test de string del equipo."""
        str_rep = str(basic_team)
        assert "Team" in str_rep
        assert "Warrior" in str_rep


class TestTeamIntegration:
    """Tests de integración para Team."""

    @pytest.fixture
    def team(self):
        """Fixture con equipo de prueba."""
        chars = [
            Character("A", CharacterClass.WARRIOR, Stats(100, 50, 20, 30)),
            Character("B", CharacterClass.MAGE, Stats(80, 60, 10, 40)),
            Character("C", CharacterClass.ROGUE, Stats(90, 55, 15, 45))
        ]
        return Team(chars, team_name="TestTeam")

    def test_battle_scenario(self, team):
        """Test de escenario de batalla."""
        # Personaje activo recibe daño
        team.active_character.take_damage(60)
        assert team.active_character.current_hp < 100

        # Cambiar a otro personaje
        team.switch_character(1)
        assert team.active_character.name == "B"

        # Personaje activo cae
        team.active_character.current_hp = 0
        team.auto_switch_on_faint()
        assert team.active_character.name == "C"

        # Verificar estado del equipo
        assert team.get_alive_count() == 2
        assert not team.is_defeated()

    def test_complete_defeat_scenario(self, team):
        """Test de derrota completa."""
        for char in team.characters:
            char.current_hp = 0

        assert team.is_defeated()
        assert team.get_alive_count() == 0
        assert team.auto_switch_on_faint() is None

    def test_switching_chain(self, team):
        """Test de cadena de cambios."""
        # Cambiar múltiples veces
        team.switch_character(1)
        assert team.active_index == 1

        team.switch_character(2)
        assert team.active_index == 2

        team.switch_character(0)
        assert team.active_index == 0

    def test_partial_team_defeat(self, team):
        """Test de derrota parcial."""
        team.characters[0].current_hp = 0
        team.characters[1].current_hp = 0

        assert not team.is_defeated()
        assert team.get_alive_count() == 1

        # Auto-switch debería ir al último vivo
        team.auto_switch_on_faint()
        assert team.active_character.name == "C"
