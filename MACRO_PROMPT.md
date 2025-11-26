# BATTLERPG AI - Sistema Agentivo de Desarrollo

## 📌 CONTEXTO DEL PROYECTO

Estás trabajando en BattleRPG AI, un juego de combate 1v1 estilo Pokémon con IA 
adaptativa basada en Reinforcement Learning. Cada jugador tiene un equipo de 3 
personajes y debe derrotar al equipo rival. El objetivo es crear agentes que 
aprendan del comportamiento del oponente y adapten sus estrategias dinámicamente.

### Documentos de Referencia
- Propuesta de proyecto en Google Docs
- Estándares de código definidos
- Arquitectura técnica a desarrollar

---

## 🎯 OBJETIVOS PRINCIPALES

1. **Sistema de Combate Robusto**: Personajes, equipos, turnos y victoria
2. **Mecánicas Pokémon-like**: Cambios, ventajas de tipo, habilidades
3. **IA Adaptativa**: Agentes que observan y aprenden de patrones adversariales
4. **Reinforcement Learning**: Implementación de Q-Learning/DQN para aprendizaje
5. **Modularidad**: Componentes intercambiables y extensibles

---

## 💻 ESTÁNDARES DE CÓDIGO

### Nomenclatura
- **Código**: Inglés (variables, funciones, clases)
- **Comentarios**: Español (docstrings, inline, docs)
- **Convenciones**: PEP 8 estricto

### Arquitectura
- **Paradigma**: Programación Orientada a Objetos
- **Type Hints**: Obligatorios en todas las funciones/métodos
- **Docstrings**: Formato Google/NumPy en español

### Ejemplo de Estructura
```python
from typing import List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

class CharacterClass(Enum):
    """Clases de personajes disponibles en el juego."""
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    TANK = "tank"
    SUPPORT = "support"

class StatusEffect(Enum):
    """Efectos de estado que pueden afectar a los personajes."""
    BURN = "burn"       # Daño por turno
    POISON = "poison"   # Daño creciente
    STUN = "stun"       # Pierde turno
    SHIELD = "shield"   # Reduce daño
    BUFF = "buff"       # Aumenta stats

@dataclass
class Stats:
    """
    Estadísticas base de un personaje.
    
    Attributes:
        hp: Puntos de vida máximos
        attack: Poder de ataque base
        defense: Reducción de daño
        speed: Determina orden de turno
    """
    hp: int
    attack: int
    defense: int
    speed: int

class Character:
    """
    Representa un personaje del juego con sus atributos, habilidades y estado.
    
    Similar a un Pokémon, cada personaje tiene una clase (tipo), estadísticas,
    y puede aprender habilidades especiales.
    
    Attributes:
        name: Nombre del personaje
        char_class: Clase del personaje (determina ventajas de tipo)
        stats: Estadísticas base (HP, ATK, DEF, SPD)
        current_hp: HP actual del personaje
        abilities: Lista de habilidades disponibles
        status_effects: Efectos de estado activos
        is_active: Si es el personaje activo en combate
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
            ValueError: Si stats tiene valores inválidos o abilities > 4
        """
        if stats.hp <= 0:
            raise ValueError("HP debe ser positivo")
        if stats.attack < 0 or stats.defense < 0 or stats.speed < 0:
            raise ValueError("Las stats no pueden ser negativas")
        if abilities and len(abilities) > 4:
            raise ValueError("Un personaje puede tener máximo 4 habilidades")
            
        self.name = name
        self.char_class = char_class
        self.stats = stats
        self.current_hp = stats.hp
        self.abilities = abilities or []
        self.status_effects: List[StatusEffect] = []
        self.is_active = False
    
    def take_damage(self, damage: int) -> int:
        """
        Aplica daño al personaje considerando defensa.
        
        La fórmula de daño es similar a Pokémon:
        damage_taken = max(1, damage - defense)
        
        Args:
            damage: Cantidad de daño base a aplicar
            
        Returns:
            Cantidad real de daño recibido después de defensa
        """
        # Calcular daño efectivo
        actual_damage = max(1, damage - self.stats.defense)
        
        # Aplicar daño
        self.current_hp = max(0, self.current_hp - actual_damage)
        
        return actual_damage
    
    def is_alive(self) -> bool:
        """Verifica si el personaje sigue en combate."""
        return self.current_hp > 0
    
    def heal(self, amount: int) -> int:
        """
        Restaura HP al personaje.
        
        Args:
            amount: Cantidad de HP a restaurar
            
        Returns:
            Cantidad real de HP restaurado (no puede exceder max HP)
        """
        old_hp = self.current_hp
        self.current_hp = min(self.stats.hp, self.current_hp + amount)
        return self.current_hp - old_hp
    
    def apply_status_effect(self, effect: StatusEffect) -> bool:
        """
        Aplica un efecto de estado al personaje.
        
        Args:
            effect: Efecto a aplicar
            
        Returns:
            True si se aplicó exitosamente, False si ya lo tenía
        """
        if effect not in self.status_effects:
            self.status_effects.append(effect)
            return True
        return False
    
    def __repr__(self) -> str:
        return (f"Character({self.name}, {self.char_class.value}, "
                f"HP: {self.current_hp}/{self.stats.hp})")

class Team:
    """
    Representa un equipo de 3 personajes.
    
    Similar al sistema de Pokémon, solo un personaje puede estar activo
    a la vez, pero el jugador puede cambiar entre ellos.
    
    Attributes:
        characters: Lista de 3 personajes
        active_index: Índice del personaje activo (0-2)
    """
    
    def __init__(self, characters: List[Character]) -> None:
        """
        Inicializa un equipo.
        
        Args:
            characters: Lista de exactamente 3 personajes
            
        Raises:
            ValueError: Si no hay exactamente 3 personajes
        """
        if len(characters) != 3:
            raise ValueError("Un equipo debe tener exactamente 3 personajes")
            
        self.characters = characters
        self.active_index = 0
        self.characters[0].is_active = True
    
    @property
    def active_character(self) -> Character:
        """Retorna el personaje activo actual."""
        return self.characters[self.active_index]
    
    def switch_character(self, new_index: int) -> bool:
        """
        Cambia el personaje activo.
        
        Args:
            new_index: Índice del nuevo personaje activo (0-2)
            
        Returns:
            True si el cambio fue exitoso, False si no es válido
        """
        if new_index < 0 or new_index >= 3:
            return False
        if new_index == self.active_index:
            return False  # Ya es el activo
        if not self.characters[new_index].is_alive():
            return False  # No puede cambiar a personaje derrotado
            
        # Realizar cambio
        self.characters[self.active_index].is_active = False
        self.active_index = new_index
        self.characters[self.active_index].is_active = True
        return True
    
    def is_defeated(self) -> bool:
        """Verifica si el equipo ha sido completamente derrotado."""
        return all(not char.is_alive() for char in self.characters)
    
    def get_alive_characters(self) -> List[Character]:
        """Retorna lista de personajes vivos."""
        return [char for char in self.characters if char.is_alive()]
    
    def __repr__(self) -> str:
        return f"Team([{', '.join(str(c) for c in self.characters)}])"
```

---

## 🧩 ARQUITECTURA DEL PROYECTO

```
battlerpg_ai/
├── src/
│   ├── core/              # Lógica fundamental del juego
│   │   ├── character.py   # Sistema de personajes
│   │   ├── team.py        # Gestión de equipos
│   │   ├── ability.py     # Habilidades especiales
│   │   ├── stats.py       # Estadísticas y tipos
│   │   └── player.py      # Jugadores base
│   ├── engine/            # Motor del juego
│   │   ├── battle_state.py      # Estado del combate
│   │   ├── turn_manager.py      # Gestión de turnos
│   │   ├── action_validator.py  # Validación de acciones
│   │   ├── damage_calculator.py # Cálculo de daño
│   │   ├── type_system.py       # Ventajas de tipo
│   │   └── victory_checker.py   # Condiciones de victoria
│   ├── ai/                # Agentes de IA
│   │   ├── heuristic/     # IA basada en heurísticas
│   │   │   ├── basic_player.py
│   │   │   ├── type_advantage_player.py
│   │   │   └── aggressive_player.py
│   │   ├── reinforcement/ # Agentes RL
│   │   │   ├── q_learning_agent.py
│   │   │   ├── dqn_agent.py
│   │   │   └── state_encoder.py
│   │   └── behavior/      # Observación de comportamiento
│   │       ├── behavior_tracker.py
│   │       ├── opponent_profile.py
│   │       └── pattern_detector.py
│   ├── training/          # Sistema de entrenamiento
│   │   ├── trainer.py
│   │   ├── metrics.py
│   │   ├── data_collector.py
│   │   └── replay_buffer.py
│   └── utils/             # Utilidades
│       ├── config.py
│       ├── logger.py
│       └── visualizer.py
├── tests/                 # Tests unitarios
│   ├── test_character.py
│   ├── test_team.py
│   ├── test_battle.py
│   └── test_ai/
├── notebooks/             # Análisis y visualizaciones
├── configs/               # Archivos de configuración
│   ├── characters.json    # Definiciones de personajes
│   ├── abilities.json     # Definiciones de habilidades
│   └── training_config.yaml
└── docs/                  # Documentación adicional
```

---

## 🔧 FLUJO DE TRABAJO

### Para Cada Nueva Feature:

1. **Análisis**
   - Revisar documentos del proyecto relevantes
   - Verificar código existente en `/src`
   - Identificar dependencias y conflictos potenciales

2. **Diseño**
   - Proponer arquitectura de clases (UML si es complejo)
   - Justificar decisiones de diseño
   - Listar trade-offs y alternativas consideradas

3. **Implementación**
   - Código modular con responsabilidades claras
   - Type hints completos
   - Docstrings detallados en español
   - Validación de inputs defensiva
   - Manejo de errores con try-except

4. **Testing**
   - Tests unitarios con pytest para lógica crítica
   - Casos edge incluidos
   - Coverage > 80% para módulos core

5. **Documentación**
   - README actualizado si aplica
   - Comentarios inline en lógica compleja
   - Diagramas para flujos no triviales

### Pregunta Antes de Asumir
- Si la especificación es ambigua
- Si hay múltiples formas razonables de implementar algo
- Si necesitas más contexto sobre decisiones previas

---

## 🎓 CONCEPTOS TÉCNICOS CLAVE

### Mecánicas de Combate (Inspirado en Pokémon)

#### Sistema de Turnos
- **Velocidad determina orden**: Personaje más rápido ataca primero
- **Cambios son prioritarios**: Cambiar personaje ocurre antes que ataques
- **Prioridad de habilidades**: Algunas habilidades tienen prioridad alta

#### Ventajas de Tipo (Sistema Rock-Paper-Scissors Extendido)
```
WARRIOR > ROGUE > MAGE > WARRIOR (ciclo básico)
TANK: Resistente a WARRIOR y ROGUE
SUPPORT: Neutral contra todos, buffs aliados

Multiplicadores:
- Súper efectivo: 1.5x daño
- Normal: 1.0x daño
- No muy efectivo: 0.5x daño
```

#### Acciones Disponibles
1. **ATTACK**: Ataque básico con daño base del personaje
2. **USE_ABILITY**: Usa una habilidad especial (daño, buff, debuff, heal)
3. **SWITCH**: Cambia al siguiente personaje del equipo
4. **ITEM** (opcional para MVP): Usa objeto (poción, revivir)

#### Fórmula de Daño Básica
```python
# Daño base
base_damage = attacker.attack

# Modificador de tipo
type_multiplier = get_type_effectiveness(attacker.char_class, defender.char_class)

# Daño con tipo
typed_damage = base_damage * type_multiplier

# Aplicar defensa
final_damage = max(1, typed_damage - defender.defense)

# Factor aleatorio (±10% variación)
actual_damage = final_damage * random.uniform(0.9, 1.1)
```

### Reinforcement Learning

#### Espacio de Estado (State Space)
Representación vectorial del combate:
```python
state = [
    # Jugador 1
    char1_hp_ratio,      # HP actual / HP máximo
    char2_hp_ratio,
    char3_hp_ratio,
    active_char_index,   # 0, 1, o 2
    
    # Jugador 2 (oponente)
    opp_char1_hp_ratio,
    opp_char2_hp_ratio,
    opp_char3_hp_ratio,
    opp_active_char_index,
    
    # Ventaja de tipo
    type_advantage,      # -1, 0, +1
    
    # Efectos de estado (one-hot)
    has_burn, has_poison, has_stun, has_shield, has_buff
]
```

#### Espacio de Acción (Action Space)
```python
actions = [
    0: ATTACK,
    1: USE_ABILITY_1,
    2: USE_ABILITY_2,
    3: USE_ABILITY_3,
    4: USE_ABILITY_4,
    5: SWITCH_TO_CHAR_1,
    6: SWITCH_TO_CHAR_2,
    7: SWITCH_TO_CHAR_3
]
```

#### Función de Recompensa
```python
reward = 0

# Recompensas inmediatas
reward += damage_dealt * 0.01        # Pequeña recompensa por daño
reward -= damage_received * 0.01     # Penalización por recibir daño

# Recompensas por knockout
if enemy_character_fainted:
    reward += 1.0
if own_character_fainted:
    reward -= 1.0

# Recompensa por victoria/derrota
if battle_won:
    reward += 10.0
elif battle_lost:
    reward -= 10.0

# Recompensa por eficiencia (bonus por ganar rápido)
if battle_won:
    reward += max(0, (50 - num_turns) * 0.1)
```

### Algoritmos RL a Implementar

#### 1. Q-Learning (MVP)
- **Ventajas**: Simple, interpretable, bueno para espacios pequeños
- **Desventajas**: Requiere discretización del espacio de estado
- **Uso**: Primer agente RL básico

#### 2. Deep Q-Network (DQN) (Post-MVP)
- **Ventajas**: Maneja espacios continuos, más flexible
- **Desventajas**: Más complejo, requiere más entrenamiento
- **Uso**: Versión mejorada del agente

#### 3. Policy Gradient (Opcional)
- **Ventajas**: Aprende políticas estocásticas, mejor para exploración
- **Desventajas**: Alta varianza, convergencia lenta
- **Uso**: Experimentación avanzada

---

## 📊 MÉTRICAS DE COMPORTAMIENTO DEL OPONENTE

### Patrones a Detectar

#### 1. Agresividad
```python
aggression_score = (
    num_attacks / total_actions
)
# 0.0 = pasivo, 1.0 = muy agresivo
```

#### 2. Frecuencia de Cambio
```python
switch_frequency = (
    num_switches / total_actions
)
# > 0.3 = cambia mucho
# < 0.1 = casi nunca cambia
```

#### 3. Uso de Habilidades
```python
ability_usage_rate = (
    num_abilities_used / total_actions
)
# Por tipo de habilidad (damage, buff, debuff, heal)
```

#### 4. Respuesta a HP Bajo
```python
# ¿Cambia cuando HP < 30%?
low_hp_switch_tendency = (
    switches_when_hp_low / times_hp_was_low
)
```

#### 5. Aprovechamiento de Tipo
```python
# ¿Mantiene ventaja de tipo?
type_advantage_awareness = (
    attacks_with_advantage / total_attacks
)
```

### OpponentProfile
```python
@dataclass
class OpponentProfile:
    """
    Perfil de comportamiento del oponente.
    
    Se actualiza tras cada partida para detectar patrones.
    """
    aggression: float           # 0.0 - 1.0
    switch_frequency: float     # 0.0 - 1.0
    ability_preference: Dict[str, float]  # Por tipo de habilidad
    low_hp_behavior: str        # "aggressive", "defensive", "switch"
    type_awareness: float       # 0.0 - 1.0
    
    num_games_observed: int
    total_actions: int
```

---

## ⚠️ CONSIDERACIONES ESPECIALES

### Balance del Juego
- **Evitar estrategias dominantes**: Ninguna clase debe ganar siempre
- **Ventajas de tipo balanceadas**: Multiplicadores razonables (1.5x max)
- **Habilidades equilibradas**: Cooldowns o costos para habilidades potentes
- **Testing extensivo**: Simular 1000+ partidas entre diferentes estrategias

### Performance
- **Vectorización**: Usar NumPy para cálculos batch en entrenamiento
- **Replay Buffer**: Almacenar experiencias para training off-policy
- **Paralelización**: Múltiples batallas simultáneas durante entrenamiento
- **Early stopping**: Detener entrenamiento si converge

### Reproducibilidad
- **Seeds fijos**: `random.seed()`, `np.random.seed()`, `torch.manual_seed()`
- **Logging completo**: Hiperparámetros, arquitectura, resultados
- **Versionado de modelos**: Guardar checkpoints cada N episodios

### Debugging
- **Visualización de partidas**: Imprimir log detallado de cada turno
- **Métricas en tiempo real**: Winrate, avg reward, loss (si DQN)
- **Análisis de políticas**: ¿Qué acciones prefiere el agente?

---

## 🚀 CRITERIOS DE ÉXITO DEL MVP

### Funcionalidad Core
- ✅ Dos jugadores pueden completar una batalla con equipos de 3 personajes
- ✅ Sistema de turnos basado en velocidad funciona correctamente
- ✅ Ventajas de tipo se aplican correctamente
- ✅ Cambios de personaje funcionan como se espera
- ✅ Victoria se detecta cuando un equipo es eliminado

### IA Heurística
- ✅ HeuristicPlayer toma decisiones razonables:
  - Cambia si hay desventaja de tipo significativa
  - Ataca personajes con HP bajo
  - Usa habilidades en momentos apropiados
- ✅ RandomPlayer sirve como baseline funcional
- ✅ HeuristicPlayer gana >70% vs RandomPlayer

### Observación de Comportamiento
- ✅ BehaviorTracker registra todas las acciones correctamente
- ✅ Se calculan métricas básicas (agresividad, frecuencia de cambio)
- ✅ OpponentProfile se actualiza tras cada partida

### Reinforcement Learning Inicial
- ✅ Agente RL puede entrenarse contra HeuristicPlayer
- ✅ Performance mejora mediblemente tras 1000+ episodios
- ✅ Winrate aumenta de ~30% → ~50%+ durante entrenamiento
- ✅ Aprende al menos 1 patrón adversarial observable:
  - Ejemplo: Detecta que oponente es agresivo → juega más defensivo
  - Ejemplo: Detecta que oponente cambia poco → explota ventaja de tipo

---

## 📝 TEMPLATE DE RESPUESTA

Cuando implementes una feature, estructura tu respuesta así:

### 1. 🎯 Objetivo
[Qué vamos a implementar y por qué]

### 2. 🏗️ Diseño
[Arquitectura propuesta, clases, interacciones]
[Diagrama UML si es complejo]

### 3. 💡 Decisiones Clave
[Justificación de elecciones técnicas]
[Trade-offs considerados]

### 4. 💻 Implementación
[Código paso a paso con explicaciones]

### 5. 🧪 Testing
[Tests unitarios si es componente crítico]

### 6. 📊 Visualización (Opcional)
[Gráficos o diagramas si ayudan a entender]

### 7. 🔄 Próximos Pasos
[Qué falta o cómo extender esta feature]

---

## 🎯 COMANDOS ÚTILES PARA EL AGENTE

### Antes de Implementar
```
"Revisa los archivos en /src/core para ver la implementación actual"
"Explica brevemente cómo funciona el sistema de ventajas de tipo antes de codificar"
"¿Qué trade-offs hay entre usar una tabla de ventajas vs un sistema calculado?"
```

### Durante Implementación
```
"Implementa la clase Character con type hints y docstrings en español"
"Añade tests unitarios para el método take_damage()"
"Crea un diagrama de flujo para el sistema de turnos"
```

### Debugging y Optimización
```
"Analiza por qué el agente RL no está mejorando su winrate"
"Sugiere visualizaciones para las métricas de entrenamiento"
"Optimiza el StateEncoder para reducir dimensionalidad"
```

---

## 🎮 FASE ACTUAL: MVP - FUNDAMENTOS DEL JUEGO

**Prioridad CRÍTICA**: Implementar el sistema básico de personajes, equipos y combate.

**Orden de Implementación Sugerido**:
1. `core/character.py` - Sistema de personajes base
2. `core/team.py` - Gestión de equipos de 3 personajes
3. `core/ability.py` - Habilidades especiales
4. `engine/type_system.py` - Ventajas de tipo
5. `engine/damage_calculator.py` - Cálculo de daño
6. `engine/battle_state.py` - Estado del combate
7. `engine/turn_manager.py` - Gestión de turnos
8. `core/player.py` - Jugadores base (Random, Heuristic)

**Siguiente Tarea Específica**: 
Espera instrucciones del usuario sobre qué componente implementar primero.

---

## 🔥 RECORDATORIOS CRÍTICOS

1. **SIEMPRE código en inglés, comentarios en español**
2. **SIEMPRE incluir type hints completos**
3. **SIEMPRE docstrings en español con formato Google/NumPy**
4. **SIEMPRE validar inputs antes de procesarlos**
5. **SIEMPRE preguntar si algo no está claro**
6. **NUNCA asumir cuando hay ambigüedad**
7. **NUNCA omitir manejo de errores en código de producción**
8. **SIEMPRE tests para lógica crítica del juego**

---

## 📚 RECURSOS ADICIONALES

### Referencias de Pokémon (Inspiración)
- Sistema de tipos y ventajas
- Mecánica de cambio de personajes
- Fórmulas de daño balanceadas
- Prioridad de movimientos

### Referencias de RL
- Sutton & Barto - Reinforcement Learning: An Introduction
- OpenAI Gym - Entornos de entrenamiento
- Stable Baselines3 - Implementaciones de referencia

### Herramientas Recomendadas
- **Desarrollo**: VSCode con Python extension
- **Testing**: pytest, pytest-cov
- **RL**: NumPy, PyTorch (si DQN)
- **Visualización**: matplotlib, seaborn
- **Logging**: Python logging module, TensorBoard (opcional)

---

**¡Listo para comenzar el desarrollo! Espero tus instrucciones sobre qué implementar primero.**
