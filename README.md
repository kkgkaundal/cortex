# Cortex

**Event-Driven, Self-Learning, Portable System Agent with Tiered Memory & Sandbox PoC**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Cortex is a local-first intelligent system agent that continuously learns from system activity, safely tests new workflows in a sandbox, and stores structured long-term memory. It uses LLMs only for interpretation and reasoning, not as permanent memory.

## Philosophy

> **Cortex is a living brain, not a chatbot**

```
Observe → Learn → Store → Practice → Improve → Answer
```

Memory is primary. LLM is only a helper.

## Features

✅ **Continuous Learning**: Learns from commands, workflows, and patterns  
✅ **Tiered Memory**: HOT (RAM) / WARM (SQLite) / COLD (Archive)  
✅ **Sandbox Safety**: Tests new workflows safely before execution  
✅ **Skill Memory**: Stores and improves workflows with reinforcement learning  
✅ **Explainable**: Shows learning sources, confidence, and reasoning  
✅ **Portable**: Optimized for pendrive usage  

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/kkgkaundal/cortex.git
cd cortex

# Install dependencies
pip install -r requirements.txt

# Install Cortex
pip install -e .
```

### Basic Usage

```bash
# Learn from a command
cortex learn "npm install"

# Ask for advice
cortex ask "how do I deploy this project?"

# Check system status
cortex status

# View memory statistics
cortex memory stats

# Test a command in sandbox
cortex sandbox run "git status"
```

## Core Concepts

### Memory Types

1. **Episodic Memory**: Records of events and commands
2. **Semantic Memory**: Structured facts with confidence scores
3. **Skill Memory**: Validated workflows with success rates

### Learning Sources

- 🖥️ **System Behavior**: Commands, apps, workflows
- 🌐 **Internet** (Hot Learning): Docs, tutorials, repos
- 📄 **Documents**: PDFs, markdown, code repositories
- 🧪 **Sandbox Experiments**: Validated through testing

### Reinforcement Learning

Cortex improves through experience:
- ✅ Success → Confidence increases
- ❌ Failure → Confidence decreases

```
confidence = (successes + 1) / (total_attempts + 2)
```

## CLI Commands

### Learn
```bash
# Learn from executing a command
cortex learn "python script.py"

# Learn with context
cortex learn "npm test" --context "testing React app"
```

### Ask
```bash
# Query learned knowledge
cortex ask "what's the best way to build this project?"
```

### Status
```bash
# Show system status and statistics
cortex status
```

### Memory
```bash
# Show memory statistics
cortex memory stats

# Export as JSON
cortex memory stats --json
```

### Sandbox
```bash
# Run command in sandbox
cortex sandbox run "npm run build"

# Sandbox with custom timeout
cortex sandbox run "long-command" --timeout 120
```

### Background Learning
```bash
# Start background learning (continuous improvement)
cortex background --action start

# Stop background learning
cortex background --action stop

# Check background learning status
cortex background --action status

# List active learning topics
cortex background --action topics --limit 50

# Boost priority of a specific topic
cortex background --action boost --topic python
```

**Background Learning Features:**
- Continuously improves knowledge about topics
- Handles 5,000,000+ topics with minimal overhead (~100 bytes per topic)
- Priority-based scheduling (low confidence = high priority)
- Automatic activation when you learn facts
- User queries automatically boost topic priority
- Can be started/stopped on demand
- Runs in background with 2-second cycles

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

### Components

- **Brain Core**: Central intelligence coordinator
- **Memory System**: Three-tier storage (HOT/WARM/COLD)
- **Learning Engine**: Pattern detection and workflow extraction
- **Sandbox**: Safe execution environment
- **CLI**: User interface

### Directory Structure

```
cortex/
├── core/           # Brain and central coordination
├── memory/         # Database and memory management
├── learning/       # Learning engine and pattern detection
├── sandbox/        # Safe execution environment
├── cli/            # Command-line interface
└── utils/          # Utilities and configuration
```

## Development

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test
python -m unittest tests.test_brain
```

### Configuration

Set via environment variables:

```bash
export CORTEX_HOME=~/.cortex                    # Data directory
export CORTEX_SANDBOX_TIMEOUT=60                # Sandbox timeout (seconds)
export CORTEX_PATTERN_MIN=3                     # Min pattern occurrences
export CORTEX_CONFIDENCE_MIN=0.5                # Min confidence threshold
```

## Implementation Stages

- ✅ **Stage 1 - Baby Brain**: SQLite schema, memory operations, CLI
- ✅ **Stage 2 - Learning Core**: Pattern detection, reinforcement learning
- ✅ **Stage 3 - Sandbox Safety**: Isolated execution, evaluation
- 🚧 **Stage 4 - Research Intelligence**: Internet learning, document parsing
- 🚧 **Stage 5 - Lifelong Brain**: Background consolidation, proactive learning

## Example Workflow

```bash
# Start learning session
cortex learn "npm install"
cortex learn "npm run build"
cortex learn "npm test"

# Pattern detected: "Build and Test"
# Cortex creates a skill automatically

# Later, ask for advice
cortex ask "how do I build this project?"

# Cortex responds with:
# - Learned workflow
# - Confidence score
# - Average duration
# - Success rate
```

## Success Metrics

Cortex succeeds when it:
- ✅ Learns automatically from usage
- ✅ Safely tests new workflows
- ✅ Explains how it learned something
- ✅ Keeps memory fast even after months
- ✅ Runs smoothly from portable storage

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Inspired by the need for local-first, explainable AI that learns continuously and safely.
