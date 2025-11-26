# 🚀 BattleRPG AI - Quick Start Guide

## Instalación Rápida

```bash
# 1. Clonar o navegar al directorio del proyecto
cd battlerpgAI

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Instalar el proyecto
pip install -e .
```

## Ejecutar tu Primera Batalla

```bash
# Opción 1: Demo rápido (recomendado para empezar)
python demo_quick.py

# Opción 2: Demo completo con detalles
python demo_battle.py
```

## Ejemplo de Salida

```
Loading configuration...
  Loaded 9 abilities
  Loaded 10 characters

Creating teams...
  Team 1: Balanced Team
  Team 2: Aggro Team

==================================================
BATTLE START!
==================================================

==================================================
BATTLE END!
==================================================

Winner: Player 1
Total Turns: 14
Team 1: 1/3 alive, 10 HP
Team 2: 0/3 alive, 0 HP

MVP VALIDATION: SUCCESS!
```

## Ejecutar Tests

```bash
# Todos los tests
pytest

# Con reporte de cobertura
pytest --cov=src --cov-report=html

# Abrir reporte HTML
open htmlcov/index.html
```

## Crear tu Propia Batalla

```python
from src.utils.config import get_config_loader
from src.core.player import RandomPlayer
from src.engine.battle_state import BattleState
from src.engine.victory_checker import VictoryChecker

# 1. Cargar configuración
loader = get_config_loader()
loader.load_abilities()
loader.load_characters()

# 2. Ver personajes disponibles
print(loader.list_available_characters())
# ['Goliath', 'Blade', 'Pyro', 'Arcane', 'Shadow', 'Viper',
#  'Fortress', 'Guardian', 'Healer', 'Mystic']

# 3. Ver equipos predefinidos
print(loader.list_available_teams())
# ['Balanced Team', 'Physical Team', 'Speed Team', 'Tank Team', 'Aggro Team']

# 4. Crear tu equipo personalizado
my_team = loader.create_custom_team(
    ["Goliath", "Pyro", "Shadow"],
    team_name="My Awesome Team"
)

# 5. Crear equipo rival
rival_team = loader.create_preset_team("Tank Team")

# 6. Crear jugadores
player1 = RandomPlayer(my_team, player_id=1, name="You")
player2 = RandomPlayer(rival_team, player_id=2, name="Rival")

# 7. Ejecutar batalla (simplificado)
battle = BattleState(player1.team, player2.team)
battle.start_battle()
# ... (implementar loop de batalla)
```

## Personajes Disponibles

### Warriors (Guerreros)
- **Goliath**: HP 120, ATK 55, DEF 25, SPD 25
- **Blade**: HP 110, ATK 60, DEF 20, SPD 30

### Mages (Magos)
- **Pyro**: HP 85, ATK 70, DEF 10, SPD 40
- **Arcane**: HP 80, ATK 65, DEF 15, SPD 45

### Rogues (Pícaros)
- **Shadow**: HP 95, ATK 58, DEF 18, SPD 50
- **Viper**: HP 90, ATK 60, DEF 15, SPD 55

### Tanks (Tanques)
- **Fortress**: HP 140, ATK 45, DEF 35, SPD 20
- **Guardian**: HP 130, ATK 50, DEF 30, SPD 25

### Support (Apoyo)
- **Healer**: HP 100, ATK 40, DEF 20, SPD 35
- **Mystic**: HP 95, ATK 45, DEF 15, SPD 40

## Habilidades Disponibles

### Daño
- **Power Strike**: 50 damage, 1 turn cooldown
- **Quick Attack**: 30 damage, priority +1, no cooldown
- **Fireball** (Mage): 40 damage, 30% burn, 2 turns cooldown

### Estado
- **Poison Strike** (Rogue): 30 damage, 50% poison, 2 turns cooldown
- **Shield Bash** (Tank): 35 damage, 20% stun, 3 turns cooldown

### Curación
- **Heal** (Support): Restaura 40 HP, 3 turns cooldown

### Buffs
- **Battle Cry**: +30% ataque, 4 turns cooldown
- **Iron Defense** (Tank): Shield (50% reducción), 3 turns cooldown

### Debuffs
- **Intimidate**: -30% ataque enemigo, 3 turns cooldown

## Equipos Predefinidos

1. **Balanced Team**: Blade + Pyro + Shadow
   - Balanceado con variedad de clases

2. **Physical Team**: Goliath + Shadow + Fortress
   - Alto daño físico y defensa

3. **Speed Team**: Shadow + Arcane + Mystic
   - Velocidad extrema

4. **Tank Team**: Fortress + Guardian + Healer
   - Máxima resistencia

5. **Aggro Team**: Blade + Pyro + Viper
   - Máximo daño ofensivo

## Ventajas de Tipo

```
SUPER EFECTIVO (1.5x damage):
  WARRIOR > ROGUE
  ROGUE > MAGE
  MAGE > WARRIOR
  MAGE > TANK

NO MUY EFECTIVO (0.5x damage):
  WARRIOR < MAGE
  ROGUE < WARRIOR
  MAGE < ROGUE
  WARRIOR/ROGUE < TANK

NEUTRAL (1.0x damage):
  SUPPORT vs todos
  Todos vs SUPPORT
```

## Estructura del Proyecto

```
battlerpgAI/
├── src/
│   ├── core/         # Lógica fundamental
│   ├── engine/       # Motor de combate
│   ├── ai/           # Agentes de IA (futuro)
│   └── utils/        # Utilidades
├── tests/            # Tests unitarios
├── configs/          # Personajes y habilidades
├── demo_quick.py     # Demo rápido
├── demo_battle.py    # Demo completo
└── MACRO_PROMPT.md   # Especificaciones técnicas
```

## Solución de Problemas

### ImportError
```bash
# Asegúrate de instalar el proyecto
pip install -e .
```

### Tests Fallan
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### FileNotFoundError (configs/)
```bash
# Verificar que estás en el directorio correcto
pwd
# Debe mostrar: .../battlerpgAI
```

## Próximos Pasos

1. ✅ Ejecuta `demo_quick.py` para ver el sistema en acción
2. ✅ Ejecuta `pytest` para verificar que todo funciona
3. ✅ Lee [MVP_SUMMARY.md](MVP_SUMMARY.md) para detalles técnicos
4. ✅ Lee [MACRO_PROMPT.md](MACRO_PROMPT.md) para la especificación completa
5. 🔜 Implementa tu propio Player con estrategias personalizadas
6. 🔜 Crea nuevos personajes y habilidades en los configs/
7. 🔜 Empieza con Reinforcement Learning (Fase 2)

## Ayuda

Para más información, consulta:
- [README.md](README.md) - Información general
- [MVP_SUMMARY.md](MVP_SUMMARY.md) - Resumen técnico completo
- [MACRO_PROMPT.md](MACRO_PROMPT.md) - Especificaciones detalladas

¡Diviértete experimentando con BattleRPG AI! 🎮⚔️
