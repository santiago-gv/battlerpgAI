#!/usr/bin/env python3
"""
Script de demostración de batalla completa.

Ejecuta una batalla 1v1 entre dos equipos usando el sistema completo.
"""

import random
import time
from typing import Optional

from src.core.player import RandomPlayer, PlayerAction
from src.core.stats import ActionType, StatusEffect
from src.engine.battle_state import BattleState
from src.engine.damage_calculator import DamageCalculator
from src.engine.turn_manager import TurnManager
from src.engine.action_validator import ActionValidator
from src.engine.victory_checker import VictoryChecker
from src.utils.config import get_config_loader


class BattleEngine:
    """
    Motor de batalla completo que orquesta el combate.

    Coordina todos los componentes del sistema para ejecutar una batalla.
    """

    def __init__(self, verbose: bool = True, delay: float = 0.5):
        """
        Inicializa el motor de batalla.

        Args:
            verbose: Si imprimir detalles de la batalla
            delay: Delay entre acciones en segundos
        """
        self.verbose = verbose
        self.delay = delay
        self.damage_calculator = DamageCalculator()
        self.turn_manager = TurnManager()
        self.action_validator = ActionValidator()
        self.victory_checker = VictoryChecker()

    def print_verbose(self, message: str) -> None:
        """Imprime mensaje si verbose está activado."""
        if self.verbose:
            print(message)
            if self.delay > 0:
                time.sleep(self.delay)

    def print_turn_header(self, battle: BattleState) -> None:
        """Imprime encabezado del turno."""
        self.print_verbose("\n" + "=" * 60)
        self.print_verbose(f"TURN {battle.current_turn}")
        self.print_verbose("=" * 60)

    def print_team_status(self, battle: BattleState) -> None:
        """Imprime estado de los equipos."""
        self.print_verbose("\nTeam Status:")
        self.print_verbose(f"  Team 1: {battle.team1}")
        self.print_verbose(f"  Team 2: {battle.team2}")

    def process_player_action(
        self,
        battle: BattleState,
        player: RandomPlayer,
        opponent_player: RandomPlayer,
        action: PlayerAction
    ) -> None:
        """
        Procesa la acción de un jugador.

        Args:
            battle: Estado de batalla
            player: Jugador que actúa
            opponent_player: Jugador oponente
            action: Acción a realizar
        """
        character = player.get_active_character()
        opponent_char = opponent_player.get_active_character()

        # Verificar si está aturdido
        if character.is_stunned():
            self.print_verbose(f"\n{character.name} está aturdido y no puede actuar!")
            battle.record_action(
                player_id=player.player_id,
                character=character,
                action_type=ActionType.ATTACK,
                result_description="Stunned - cannot act"
            )
            return

        # Procesar efectos de estado al inicio del turno
        damage_by_effect = character.process_status_effects()
        if damage_by_effect:
            for effect, damage in damage_by_effect.items():
                self.print_verbose(
                    f"\n{character.name} sufre {damage} de daño por {effect.value}!"
                )
                if not character.is_alive():
                    self.print_verbose(f"{character.name} ha sido derrotado por efectos de estado!")
                    return

        # Ejecutar acción
        if action.action_type == ActionType.ATTACK:
            self._execute_attack(battle, player, opponent_player, character, opponent_char)

        elif action.action_type == ActionType.USE_ABILITY:
            self._execute_ability(
                battle, player, opponent_player, character, opponent_char, action
            )

        elif action.action_type == ActionType.SWITCH:
            self._execute_switch(battle, player, action)

    def _execute_attack(
        self,
        battle: BattleState,
        player: RandomPlayer,
        opponent_player: RandomPlayer,
        character,
        opponent_char
    ) -> None:
        """Ejecuta un ataque básico."""
        self.print_verbose(f"\n{character.name} ataca a {opponent_char.name}!")

        result = self.damage_calculator.calculate_and_apply_damage(
            character, opponent_char
        )

        self.print_verbose(
            f"  Daño: {result.final_damage} ({result.effectiveness})"
        )
        self.print_verbose(
            f"  {opponent_char.name}: {opponent_char.current_hp}/{opponent_char.stats.hp} HP"
        )

        battle.record_action(
            player_id=player.player_id,
            character=character,
            action_type=ActionType.ATTACK,
            target=opponent_char,
            damage_dealt=result.final_damage,
            result_description=result.effectiveness
        )

        # Verificar si el oponente cayó
        if not opponent_char.is_alive():
            self.print_verbose(f"\n{opponent_char.name} ha sido derrotado!")
            new_char = opponent_player.team.auto_switch_on_faint()
            if new_char:
                self.print_verbose(f"  {opponent_player.name} envía a {new_char.name}!")

    def _execute_ability(
        self,
        battle: BattleState,
        player: RandomPlayer,
        opponent_player: RandomPlayer,
        character,
        opponent_char,
        action: PlayerAction
    ) -> None:
        """Ejecuta una habilidad."""
        ability = action.ability
        if not ability:
            return

        can_use, reason = self.action_validator.can_use_ability(character, ability)
        if not can_use:
            self.print_verbose(f"\n{character.name} no puede usar {ability.name}: {reason}")
            return

        self.print_verbose(f"\n{character.name} usa {ability.name}!")
        ability.use()

        # Aplicar efectos de daño
        if ability.get_damage_value() > 0:
            result = self.damage_calculator.calculate_and_apply_damage(
                character, opponent_char, ability
            )
            self.print_verbose(
                f"  Daño: {result.final_damage} ({result.effectiveness})"
            )
            self.print_verbose(
                f"  {opponent_char.name}: {opponent_char.current_hp}/{opponent_char.stats.hp} HP"
            )

        # Aplicar efectos de curación
        heal_value = ability.get_heal_value()
        if heal_value > 0:
            healed = character.heal(heal_value)
            self.print_verbose(f"  {character.name} se cura {healed} HP!")

        # Aplicar efectos de estado
        status_effects = ability.get_status_effects()
        for effect in status_effects:
            # Determinar target
            target = character  # Por defecto self
            for ability_effect in ability.effects:
                if ability_effect.status_effect == effect:
                    if ability_effect.target.value == "opponent":
                        target = opponent_char
                    # Chequear probabilidad
                    if random.random() <= ability_effect.probability:
                        target.apply_status_effect(effect)
                        self.print_verbose(f"  {target.name} ahora tiene {effect.value}!")

        battle.record_action(
            player_id=player.player_id,
            character=character,
            action_type=ActionType.USE_ABILITY,
            target=opponent_char,
            ability_used=ability.name
        )

        # Verificar si el oponente cayó
        if not opponent_char.is_alive():
            self.print_verbose(f"\n{opponent_char.name} ha sido derrotado!")
            new_char = opponent_player.team.auto_switch_on_faint()
            if new_char:
                self.print_verbose(f"  {opponent_player.name} envía a {new_char.name}!")

    def _execute_switch(
        self,
        battle: BattleState,
        player: RandomPlayer,
        action: PlayerAction
    ) -> None:
        """Ejecuta un cambio de personaje."""
        target_index = action.switch_target
        if target_index is None:
            return

        can_switch, reason = self.action_validator.can_switch(player.team, target_index)
        if not can_switch:
            self.print_verbose(f"\n{player.name} no puede cambiar: {reason}")
            return

        old_char = player.get_active_character()
        player.team.switch_character(target_index)
        new_char = player.get_active_character()

        self.print_verbose(f"\n{player.name} cambia {old_char.name} por {new_char.name}!")

        battle.record_action(
            player_id=player.player_id,
            character=old_char,
            action_type=ActionType.SWITCH,
            result_description=f"Switched to {new_char.name}"
        )

    def run_battle(
        self,
        player1: RandomPlayer,
        player2: RandomPlayer
    ) -> int:
        """
        Ejecuta una batalla completa.

        Args:
            player1: Primer jugador
            player2: Segundo jugador

        Returns:
            ID del ganador (1 o 2)
        """
        battle = BattleState(player1.team, player2.team)

        self.print_verbose("\n" + "=" * 60)
        self.print_verbose("BATTLE START!")
        self.print_verbose("=" * 60)
        self.print_verbose(f"\n{player1.name} vs {player2.name}")
        self.print_team_status(battle)

        battle.start_battle()

        while battle.is_in_progress():
            self.print_turn_header(battle)
            self.print_team_status(battle)

            # Obtener acciones de ambos jugadores
            action1 = player1.decide_action(player2.team, battle)
            action2 = player2.decide_action(player1.team, battle)

            # Determinar orden (por simplicidad, por velocidad)
            char1 = player1.get_active_character()
            char2 = player2.get_active_character()

            first_player = self.turn_manager.get_first_striker(char1, char2)

            if first_player == 1:
                self.process_player_action(battle, player1, player2, action1)
                if battle.is_in_progress():  # Verificar si la batalla continúa
                    self.process_player_action(battle, player2, player1, action2)
            else:
                self.process_player_action(battle, player2, player1, action2)
                if battle.is_in_progress():
                    self.process_player_action(battle, player1, player2, action1)

            # Reducir cooldowns
            for char in player1.team.characters:
                for ability in char.abilities:
                    ability.reduce_cooldown()
            for char in player2.team.characters:
                for ability in char.abilities:
                    ability.reduce_cooldown()

            # Verificar victoria
            winner = self.victory_checker.check_victory(player1.team, player2.team)
            if winner:
                battle.end_battle(winner)
                break

            battle.advance_turn()

        # Mostrar resultado
        self.print_verbose("\n" + "=" * 60)
        self.print_verbose("BATTLE END!")
        self.print_verbose("=" * 60)

        winner_name = player1.name if battle.winner_id == 1 else player2.name
        self.print_verbose(f"\nGanador: {winner_name}")

        summary = battle.get_battle_summary()
        self.print_verbose(f"\nResumen:")
        self.print_verbose(f"  Turnos totales: {summary['total_turns']}")
        self.print_verbose(f"  Team 1 HP final: {summary['team1_final_hp']}")
        self.print_verbose(f"  Team 2 HP final: {summary['team2_final_hp']}")
        self.print_verbose(f"  Team 1 vivos: {summary['team1_alive']}")
        self.print_verbose(f"  Team 2 vivos: {summary['team2_alive']}")

        return battle.winner_id


def main():
    """Función principal del demo."""
    print("BattleRPG AI - Demo de Batalla")
    print("=" * 60)

    # Cargar configuración
    print("\nCargando configuración...")
    loader = get_config_loader()
    loader.load_abilities()
    loader.load_characters()

    print(f"  {len(loader.abilities)} habilidades cargadas")
    print(f"  {len(loader.characters)} personajes cargados")
    print(f"  {len(loader.preset_teams)} equipos predefinidos")

    # Mostrar equipos disponibles
    print("\nEquipos disponibles:")
    for i, team_name in enumerate(loader.list_available_teams(), 1):
        print(f"  {i}. {team_name}")

    # Crear equipos
    print("\nCreando equipos para la batalla...")
    team1 = loader.create_preset_team("Balanced Team")
    team2 = loader.create_preset_team("Aggro Team")

    if not team1 or not team2:
        print("Error al crear equipos!")
        return

    # Crear jugadores
    player1 = RandomPlayer(team1, player_id=1, name="Player 1")
    player2 = RandomPlayer(team2, player_id=2, name="Player 2")

    # Crear motor de batalla
    engine = BattleEngine(verbose=True, delay=0.3)

    # Ejecutar batalla
    winner = engine.run_battle(player1, player2)

    print(f"\n\nEl ganador es: Player {winner}!")


if __name__ == "__main__":
    main()
