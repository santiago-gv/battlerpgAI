# BattleRPG AI

A 1v1 turn-based combat game inspired by Pokémon, featuring adaptive AI agents powered by Reinforcement Learning.

## Overview

BattleRPG AI is a strategic battle game where two players compete with teams of 3 characters. Each character has a class (type), unique stats, and special abilities. The core innovation lies in the adaptive AI agents that learn opponent behavior patterns and adjust their strategies dynamically using reinforcement learning techniques.

## Key Features

- **Pokémon-inspired Combat System**: Turn-based battles with type advantages, character switching, and special abilities
- **Adaptive AI Agents**: Learn from opponent patterns using Q-Learning and Deep Q-Networks (DQN)
- **Behavior Tracking**: Detailed analysis of opponent tendencies (aggression, switching frequency, type awareness)
- **Modular Architecture**: Clean, extensible codebase following OOP principles
- **Comprehensive Testing**: >80% code coverage with pytest

## Project Structure

```
battlerpgAI/
├── src/
│   ├── core/         # Game fundamentals (Character, Team, Abilities)
│   ├── engine/       # Battle engine (turns, damage, victory conditions)
│   ├── ai/           # AI agents (heuristic, RL, behavior tracking)
│   ├── training/     # Training system for RL agents
│   └── utils/        # Utilities (config, logging, visualization)
├── tests/            # Unit and integration tests
├── configs/          # Configuration files (characters, abilities)
├── notebooks/        # Analysis and visualizations
└── docs/             # Additional documentation
```

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/battlerpgAI.git
cd battlerpgAI

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Quick Start

```bash
# Run a demo battle (coming soon)
python demo_battle.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## Development Status

Currently in **MVP Phase**: Building core game mechanics and basic AI agents.

## Documentation

See [MACRO_PROMPT.md](MACRO_PROMPT.md) for detailed technical specifications, architecture decisions, and development guidelines.

## License

MIT License
