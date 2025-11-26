"""
Tests de integración para el sistema de combate completo.

Verifica que todos los componentes funcionen juntos correctamente.
"""

import pytest
from src.core.character import Character
from src.core.team import Team
from src.core.stats import CharacterClass, Stats, ActionType
from src.engine.battle_state import BattleState, BattlePhase
from src.engine.damage_calculator import DamageCalculator
from src.engine.type_system import get_type_system
from src.engine.turn_manager import TurnManager
from src.engine.action_validator import ActionValidator
from src.engine.victory_checker import VictoryChecker


class TestTypeSystem:
    """Tests para el sistema de tipos."""

    @pytest.fixture
    def type_system(self):
        """Fixture con sistema de tipos."""
        return get_type_system()

    def test_warrior_vs_rogue(self, type_system):
        """Test de ventaja Warrior vs Rogue."""
        multiplier = type_system.get_multiplier(
            CharacterClass.WARRIOR,
            CharacterClass.ROGUE
        )
        assert multiplier == 1.5
        assert type_system.has_advantage(CharacterClass.WARRIOR, CharacterClass.ROGUE)

    def test_rogue_vs_mage(self, type_system):
        """Test de ventaja Rogue vs Mage."""
        multiplier = type_system.get_multiplier(
            CharacterClass.ROGUE,
            CharacterClass.MAGE
        )
        assert multiplier == 1.5

    def test_mage_vs_warrior(self, type_system):
        """Test de ventaja Mage vs Warrior."""
        multiplier = type_system.get_multiplier(
            CharacterClass.MAGE,
            CharacterClass.WARRIOR
        )
        assert multiplier == 1.5

    def test_support_neutral(self, type_system):
        """Test de Support neutral."""
        for defender in CharacterClass:
            multiplier = type_system.get_multiplier(
                CharacterClass.SUPPORT,
                defender
            )
            assert multiplier == 1.0


class TestDamageCalculator:
    """Tests para el calculador de daño."""

    @pytest.fixture
    def calculator(self):
        """Fixture con calculador sin variación aleatoria."""
        return DamageCalculator(use_random_variance=False)

    @pytest.fixture
    def warrior(self):
        """Fixture con warrior."""
        return Character("Warrior", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))

    @pytest.fixture
    def rogue(self):
        """Fixture con rogue."""
        return Character("Rogue", CharacterClass.ROGUE, Stats(90, 45, 15, 35))

    def test_basic_attack_with_advantage(self, calculator, warrior, rogue):
        """Test de ataque básico con ventaja de tipo."""
        result = calculator.calculate_basic_attack_damage(warrior, rogue)
        # 50 attack * 1.5 type = 75 - 15 defense = 60
        assert result.final_damage == 60
        assert result.type_multiplier == 1.5
        assert result.effectiveness == "Super effective!"

    def test_basic_attack_with_disadvantage(self, calculator, rogue, warrior):
        """Test de ataque con desventaja."""
        result = calculator.calculate_basic_attack_damage(rogue, warrior)
        # 45 attack * 0.5 type = 22 - 20 defense = 2
        assert result.final_damage == 2
        assert result.type_multiplier == 0.5

    def test_minimum_damage(self, calculator):
        """Test de daño mínimo de 1."""
        attacker = Character("Weak", CharacterClass.SUPPORT, Stats(100, 10, 10, 30))
        defender = Character("Tank", CharacterClass.TANK, Stats(120, 40, 50, 20))

        result = calculator.calculate_basic_attack_damage(attacker, defender)
        assert result.final_damage >= 1

    def test_apply_damage(self, calculator, warrior, rogue):
        """Test de aplicación de daño."""
        result = calculator.calculate_basic_attack_damage(warrior, rogue)
        initial_hp = rogue.current_hp

        actual_damage = calculator.apply_damage(warrior, rogue, result)

        assert rogue.current_hp == initial_hp - actual_damage
        assert warrior.total_damage_dealt == actual_damage

    def test_estimate_damage(self, calculator, warrior, rogue):
        """Test de estimación de daño."""
        min_dmg, max_dmg = calculator.estimate_damage(warrior, rogue)
        assert min_dmg > 0
        assert max_dmg >= min_dmg


class TestBattleState:
    """Tests para el estado de batalla."""

    @pytest.fixture
    def teams(self):
        """Fixture con dos equipos."""
        team1_chars = [
            Character("W1", CharacterClass.WARRIOR, Stats(100, 50, 20, 30)),
            Character("M1", CharacterClass.MAGE, Stats(80, 60, 10, 40)),
            Character("R1", CharacterClass.ROGUE, Stats(90, 55, 15, 45))
        ]
        team2_chars = [
            Character("W2", CharacterClass.WARRIOR, Stats(100, 50, 20, 30)),
            Character("M2", CharacterClass.MAGE, Stats(80, 60, 10, 40)),
            Character("R2", CharacterClass.ROGUE, Stats(90, 55, 15, 45))
        ]
        return Team(team1_chars), Team(team2_chars)

    @pytest.fixture
    def battle(self, teams):
        """Fixture con estado de batalla."""
        return BattleState(teams[0], teams[1])

    def test_battle_initialization(self, battle):
        """Test de inicialización de batalla."""
        assert battle.phase == BattlePhase.NOT_STARTED
        assert battle.current_turn == 0
        assert battle.winner_id is None

    def test_start_battle(self, battle):
        """Test de inicio de batalla."""
        battle.start_battle()
        assert battle.phase == BattlePhase.IN_PROGRESS
        assert battle.current_turn == 1

    def test_start_battle_twice(self, battle):
        """Test de inicio de batalla duplicado."""
        battle.start_battle()
        with pytest.raises(RuntimeError):
            battle.start_battle()

    def test_end_battle(self, battle):
        """Test de fin de batalla."""
        battle.start_battle()
        battle.end_battle(winner_id=1)
        assert battle.phase == BattlePhase.FINISHED
        assert battle.winner_id == 1

    def test_advance_turn(self, battle):
        """Test de avance de turno."""
        battle.start_battle()
        initial_turn = battle.current_turn
        battle.advance_turn()
        assert battle.current_turn == initial_turn + 1

    def test_max_turns_reached(self, battle):
        """Test de límite de turnos."""
        battle.max_turns = 5
        battle.start_battle()

        for _ in range(5):
            battle.advance_turn()

        assert battle.is_finished()
        assert battle.winner_id is not None

    def test_get_team(self, battle):
        """Test de obtener equipo por ID."""
        team1 = battle.get_team(1)
        team2 = battle.get_team(2)
        assert team1 == battle.team1
        assert team2 == battle.team2

    def test_get_opponent_team(self, battle):
        """Test de obtener equipo oponente."""
        opponent1 = battle.get_opponent_team(1)
        opponent2 = battle.get_opponent_team(2)
        assert opponent1 == battle.team2
        assert opponent2 == battle.team1

    def test_record_action(self, battle):
        """Test de registro de acción."""
        battle.start_battle()
        char = battle.team1.active_character
        target = battle.team2.active_character

        battle.record_action(
            player_id=1,
            character=char,
            action_type=ActionType.ATTACK,
            target=target,
            damage_dealt=30
        )

        assert len(battle.action_history) == 1
        action = battle.action_history[0]
        assert action.player_id == 1
        assert action.damage_dealt == 30

    def test_get_battle_summary(self, battle):
        """Test de resumen de batalla."""
        battle.start_battle()
        summary = battle.get_battle_summary()

        assert "total_turns" in summary
        assert "winner_id" in summary
        assert "team1_alive" in summary
        assert "team2_alive" in summary


class TestActionValidator:
    """Tests para el validador de acciones."""

    @pytest.fixture
    def validator(self):
        """Fixture con validador."""
        return ActionValidator()

    @pytest.fixture
    def character(self):
        """Fixture con personaje."""
        return Character("Test", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))

    def test_can_attack_healthy(self, validator, character):
        """Test de ataque con personaje sano."""
        can, reason = validator.can_attack(character)
        assert can is True
        assert reason == ""

    def test_cannot_attack_fainted(self, validator, character):
        """Test de ataque con personaje derrotado."""
        character.current_hp = 0
        can, reason = validator.can_attack(character)
        assert can is False
        assert "fainted" in reason.lower()

    def test_cannot_attack_stunned(self, validator, character):
        """Test de ataque con personaje aturdido."""
        from src.core.stats import StatusEffect
        character.apply_status_effect(StatusEffect.STUN)
        can, reason = validator.can_attack(character)
        assert can is False
        assert "stunned" in reason.lower()


class TestVictoryChecker:
    """Tests para el verificador de victoria."""

    @pytest.fixture
    def checker(self):
        """Fixture con verificador."""
        return VictoryChecker()

    @pytest.fixture
    def teams(self):
        """Fixture con dos equipos."""
        team1_chars = [
            Character("A", CharacterClass.WARRIOR, Stats(100, 50, 20, 30)),
            Character("B", CharacterClass.MAGE, Stats(80, 60, 10, 40)),
            Character("C", CharacterClass.ROGUE, Stats(90, 55, 15, 45))
        ]
        team2_chars = [
            Character("X", CharacterClass.WARRIOR, Stats(100, 50, 20, 30)),
            Character("Y", CharacterClass.MAGE, Stats(80, 60, 10, 40)),
            Character("Z", CharacterClass.ROGUE, Stats(90, 55, 15, 45))
        ]
        return Team(team1_chars), Team(team2_chars)

    def test_no_winner_yet(self, checker, teams):
        """Test cuando no hay ganador aún."""
        winner = checker.check_victory(teams[0], teams[1])
        assert winner is None
        assert not checker.is_battle_over(teams[0], teams[1])

    def test_team1_wins(self, checker, teams):
        """Test cuando gana el equipo 1."""
        for char in teams[1].characters:
            char.current_hp = 0

        winner = checker.check_victory(teams[0], teams[1])
        assert winner == 1
        assert checker.is_battle_over(teams[0], teams[1])

    def test_team2_wins(self, checker, teams):
        """Test cuando gana el equipo 2."""
        for char in teams[0].characters:
            char.current_hp = 0

        winner = checker.check_victory(teams[0], teams[1])
        assert winner == 2

    def test_battle_result(self, checker, teams):
        """Test de resultado detallado."""
        result = checker.get_battle_result(teams[0], teams[1])

        assert "winner" in result
        assert "is_over" in result
        assert "team1_alive" in result
        assert "team2_alive" in result
        assert result["team1_alive"] == 3
        assert result["team2_alive"] == 3


class TestTurnManager:
    """Tests para el gestor de turnos."""

    @pytest.fixture
    def manager(self):
        """Fixture con gestor de turnos."""
        return TurnManager()

    def test_speed_determines_order(self, manager):
        """Test de orden por velocidad."""
        fast = Character("Fast", CharacterClass.ROGUE, Stats(100, 50, 20, 50))
        slow = Character("Slow", CharacterClass.TANK, Stats(120, 60, 30, 20))

        order = manager.determine_order([(fast, 1, 0), (slow, 2, 0)])

        assert order[0].character == fast
        assert order[1].character == slow

    def test_priority_overrides_speed(self, manager):
        """Test de prioridad sobre velocidad."""
        fast = Character("Fast", CharacterClass.ROGUE, Stats(100, 50, 20, 50))
        slow = Character("Slow", CharacterClass.TANK, Stats(120, 60, 30, 20))

        # Slow tiene prioridad alta
        order = manager.determine_order([(fast, 1, 0), (slow, 2, 2)])

        assert order[0].character == slow  # Va primero por prioridad
        assert order[1].character == fast

    def test_get_first_striker(self, manager):
        """Test de quién ataca primero."""
        fast = Character("Fast", CharacterClass.ROGUE, Stats(100, 50, 20, 50))
        slow = Character("Slow", CharacterClass.TANK, Stats(120, 60, 30, 20))

        first = manager.get_first_striker(fast, slow)
        assert first == 1  # Fast va primero


class TestBattleIntegration:
    """Tests de integración completa del sistema de combate."""

    @pytest.fixture
    def full_battle_setup(self):
        """Fixture con setup completo de batalla."""
        team1_chars = [
            Character("Warrior1", CharacterClass.WARRIOR, Stats(100, 50, 20, 30)),
            Character("Mage1", CharacterClass.MAGE, Stats(80, 60, 10, 40)),
            Character("Rogue1", CharacterClass.ROGUE, Stats(90, 55, 15, 45))
        ]
        team2_chars = [
            Character("Warrior2", CharacterClass.WARRIOR, Stats(100, 50, 20, 30)),
            Character("Mage2", CharacterClass.MAGE, Stats(80, 60, 10, 40)),
            Character("Rogue2", CharacterClass.ROGUE, Stats(90, 55, 15, 45))
        ]

        team1 = Team(team1_chars, "Team1")
        team2 = Team(team2_chars, "Team2")
        battle_state = BattleState(team1, team2)
        calculator = DamageCalculator(use_random_variance=False)
        validator = ActionValidator()
        victory_checker = VictoryChecker()

        return {
            "battle": battle_state,
            "calculator": calculator,
            "validator": validator,
            "victory_checker": victory_checker,
            "team1": team1,
            "team2": team2
        }

    def test_complete_battle_flow(self, full_battle_setup):
        """Test de flujo completo de batalla."""
        setup = full_battle_setup
        battle = setup["battle"]
        calculator = setup["calculator"]
        team1 = setup["team1"]
        team2 = setup["team2"]

        # Iniciar batalla
        battle.start_battle()
        assert battle.is_in_progress()

        # Turno 1: Warrior1 ataca Warrior2
        attacker = team1.active_character
        defender = team2.active_character

        result = calculator.calculate_and_apply_damage(attacker, defender)
        assert defender.current_hp < defender.stats.hp

        battle.record_action(
            player_id=1,
            character=attacker,
            action_type=ActionType.ATTACK,
            target=defender,
            damage_dealt=result.final_damage
        )

        # Avanzar turno
        battle.advance_turn()
        assert battle.current_turn == 2

        # Verificar historial
        assert len(battle.action_history) == 1

    def test_victory_scenario(self, full_battle_setup):
        """Test de escenario de victoria."""
        setup = full_battle_setup
        victory_checker = setup["victory_checker"]
        team1 = setup["team1"]
        team2 = setup["team2"]

        # Derrotar todos los personajes del team2
        for char in team2.characters:
            char.current_hp = 0

        winner = victory_checker.check_victory(team1, team2)
        assert winner == 1
        assert team2.is_defeated()
