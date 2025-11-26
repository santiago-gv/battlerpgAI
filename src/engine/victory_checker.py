"""
Módulo de verificación de victoria para BattleRPG AI.

Determina las condiciones de victoria y finalización de batalla.
"""

from typing import Optional

from src.core.team import Team


class VictoryChecker:
    """
    Verifica las condiciones de victoria en una batalla.

    Un equipo gana cuando todos los personajes del equipo oponente
    son derrotados (HP = 0).

    Examples:
        >>> checker = VictoryChecker()
        >>> team1 = Team([char1, char2, char3])
        >>> team2 = Team([char4, char5, char6])
        >>> winner = checker.check_victory(team1, team2)
        >>> winner is None  # Nadie ha ganado aún
        True
    """

    def check_victory(
        self,
        team1: Team,
        team2: Team
    ) -> Optional[int]:
        """
        Verifica si algún equipo ha ganado.

        Args:
            team1: Primer equipo (jugador 1)
            team2: Segundo equipo (jugador 2)

        Returns:
            1 si gana team1, 2 si gana team2, None si la batalla continúa

        Examples:
            >>> checker = VictoryChecker()
            >>> char1 = Character("A", CharacterClass.WARRIOR, Stats(100, 50, 20, 30))
            >>> char2 = Character("B", CharacterClass.MAGE, Stats(80, 60, 10, 40))
            >>> char3 = Character("C", CharacterClass.ROGUE, Stats(90, 55, 15, 45))
            >>> team1 = Team([char1, char2, char3])
            >>> team2 = Team([char1, char2, char3])
            >>> checker.check_victory(team1, team2) is None
            True
        """
        team1_defeated = team1.is_defeated()
        team2_defeated = team2.is_defeated()

        if team1_defeated and team2_defeated:
            # Empate (raro pero posible con daño simultáneo)
            # Gana quien tenga más HP
            if team1.get_total_hp() >= team2.get_total_hp():
                return 1
            else:
                return 2

        if team2_defeated:
            return 1

        if team1_defeated:
            return 2

        return None

    def is_battle_over(
        self,
        team1: Team,
        team2: Team
    ) -> bool:
        """
        Verifica si la batalla ha terminado.

        Args:
            team1: Primer equipo
            team2: Segundo equipo

        Returns:
            True si la batalla terminó, False en caso contrario

        Examples:
            >>> checker = VictoryChecker()
            >>> team1 = Team([char1, char2, char3])
            >>> team2 = Team([char4, char5, char6])
            >>> checker.is_battle_over(team1, team2)
            False
        """
        return self.check_victory(team1, team2) is not None

    def get_battle_result(
        self,
        team1: Team,
        team2: Team
    ) -> dict:
        """
        Obtiene un resultado detallado de la batalla.

        Args:
            team1: Primer equipo
            team2: Segundo equipo

        Returns:
            Diccionario con información del resultado

        Examples:
            >>> checker = VictoryChecker()
            >>> team1 = Team([char1, char2, char3])
            >>> team2 = Team([char4, char5, char6])
            >>> result = checker.get_battle_result(team1, team2)
            >>> 'winner' in result
            True
        """
        winner = self.check_victory(team1, team2)

        return {
            "winner": winner,
            "is_over": winner is not None,
            "team1_alive": team1.get_alive_count(),
            "team2_alive": team2.get_alive_count(),
            "team1_total_hp": team1.get_total_hp(),
            "team2_total_hp": team2.get_total_hp(),
            "team1_defeated": team1.is_defeated(),
            "team2_defeated": team2.is_defeated()
        }
