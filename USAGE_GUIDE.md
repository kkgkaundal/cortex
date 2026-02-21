# Cortex Usage Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/kkgkaundal/cortex.git
cd cortex

# Install dependencies
pip install -r requirements.txt

# Install Cortex
pip install -e .
```

## Quick Start

### 1. Check System Status

```bash
python -m cortex.cli.main status
```

This shows:
- Memory statistics (episodic, semantic, skill counts)
- Learning progress
- Sandbox execution statistics
- Session information

### 2. Learn from Commands

```bash
# Learn from a simple command
python -m cortex.cli.main learn "echo 'Hello Cortex'"

# Learn with context
python -m cortex.cli.main learn "npm install" --context "installing dependencies"
```

Cortex will:
- Execute the command
- Record the result
- Track duration
- Store in episodic memory

### 3. Use Sandbox for Safe Testing

```bash
# Test a command safely
python -m cortex.cli.main sandbox run "ls -la"

# Test with custom timeout
python -m cortex.cli.main sandbox run "long-command" --timeout 60
```

Sandbox provides:
- Isolated execution
- Timeout protection
- Detailed logs
- Error capture

### 4. Ask Questions

```bash
python -m cortex.cli.main ask "what commands have I run?"
```

Cortex will:
- Search episodic memory
- Find relevant patterns
- Provide insights based on learning

### 5. View Memory Statistics

```bash
# Human-readable format
python -m cortex.cli.main memory stats

# JSON format
python -m cortex.cli.main memory stats --json
```

### 6. Research Topics (Stage 4)

```bash
python -m cortex.cli.main research "deploy nextjs" deployment
```

This will:
- Search for information
- Extract knowledge
- Store facts in semantic memory
- Rate source reliability

### 7. Consolidate Memory (Stage 5)

```bash
# Regular consolidation
python -m cortex.cli.main consolidate --days 7

# Export knowledge base
python -m cortex.cli.main consolidate --export knowledge.json
```

Consolidation:
- Summarizes old sessions
- Archives old data
- Removes duplicates
- Updates memory tiers

## Advanced Usage

### Learning Workflows

Repeat a sequence of commands to teach Cortex a workflow:

```bash
# Repeat this pattern 3+ times
python -m cortex.cli.main learn "git add ."
python -m cortex.cli.main learn "git commit -m 'update'"
python -m cortex.cli.main learn "git push"
```

After repetition, Cortex will:
- Detect the pattern
- Create a workflow
- Calculate confidence
- Track success rate

### Programmatic Usage

```python
from cortex.core.brain import Brain
from cortex.learning.engine import LearningEngine
from cortex.sandbox.runner import Sandbox

# Initialize
brain = Brain("cortex.db")
learning_engine = LearningEngine(brain)
sandbox = Sandbox()

# Start a session
session_id = brain.start_session("my workflow")

# Observe commands
learning_engine.observe_command("npm install", True, 5000)
learning_engine.observe_command("npm test", True, 10000)

# Get insights
insights = learning_engine.get_insights()
print(insights)

# End session
brain.end_session("completed workflow")

# Close
brain.close()
```

### Working with Skills

```python
from cortex.core.brain import Brain

brain = Brain("cortex.db")

# Learn a skill
skill_id = brain.learn_skill(
    skill_name="deploy_app",
    description="Deploy application to production",
    steps=[
        "npm run build",
        "npm run test",
        "npm run deploy"
    ],
    prerequisites=["node", "npm"],
    confidence=0.7
)

# Execute and reinforce
success = True  # Did it work?
brain.reinforce_skill("deploy_app", success=success, duration_ms=30000)

# Recall skill
skill = brain.recall_skill("deploy_app")
print(f"Confidence: {skill['confidence']}")
print(f"Success rate: {skill['success_count']}/{skill['success_count'] + skill['failure_count']}")
```

### Memory Tiers

Cortex uses three memory tiers:

**HOT (RAM cache)**:
- Most frequently accessed
- Sub-millisecond lookup
- Automatically promoted

**WARM (Main database)**:
- Current active knowledge
- Fast SQLite queries
- Default tier for new data

**COLD (Archive)**:
- Old historical data
- Compressed storage
- Moved during consolidation

### Configuration

Set via environment variables:

```bash
export CORTEX_HOME=~/.cortex                    # Data directory
export CORTEX_SANDBOX_TIMEOUT=60                # Sandbox timeout (seconds)
export CORTEX_PATTERN_MIN=3                     # Min pattern occurrences
export CORTEX_CONFIDENCE_MIN=0.5                # Min confidence threshold
export CORTEX_CONSOLIDATION_DAYS=7              # Days before archival
```

## Common Workflows

### Daily Development Session

```bash
# Start your day
python -m cortex.cli.main status

# Work on your project (Cortex learns automatically)
python -m cortex.cli.main learn "npm run dev"

# Test something new safely
python -m cortex.cli.main sandbox run "npm run build"

# End of day - consolidate
python -m cortex.cli.main consolidate --days 7
```

### Learning a New Technology

```bash
# Research the topic
python -m cortex.cli.main research "react hooks tutorial" react

# Ask for advice
python -m cortex.cli.main ask "how do I use react hooks?"

# Test commands safely
python -m cortex.cli.main sandbox run "npx create-react-app test-app"
```

### Exporting Knowledge

```bash
# Export everything
python -m cortex.cli.main consolidate --export my-knowledge.json

# Share with team or backup
cp my-knowledge.json /backup/cortex-$(date +%Y%m%d).json
```

## Testing

```bash
# Run all tests
python -m unittest discover tests

# Run specific test module
python -m unittest tests.test_brain
python -m unittest tests.test_integration

# Run with verbose output
python -m unittest discover tests -v
```

## Troubleshooting

### Database locked error

If you see "database is locked":
```bash
# Close all Cortex instances
# Check for zombie processes
ps aux | grep cortex

# If needed, remove lock files
rm ~/.cortex/cortex.db-shm
rm ~/.cortex/cortex.db-wal
```

### Memory growing too large

Run consolidation more frequently:
```bash
# Consolidate data older than 3 days
python -m cortex.cli.main consolidate --days 3
```

### Slow queries

Check memory tier distribution:
```bash
python -m cortex.cli.main memory stats --json | grep tier
```

If too much data in HOT tier, restart Cortex to reload.

## Tips & Best Practices

1. **Regular Consolidation**: Run weekly to keep memory efficient
2. **Descriptive Contexts**: Use `--context` flag when learning
3. **Test Before Execute**: Use sandbox for risky commands
4. **Export Regularly**: Backup your knowledge base
5. **Monitor Confidence**: Check skill confidence before relying on them
6. **Session Management**: Group related work in sessions
7. **Semantic Learning**: Teach facts explicitly when needed

## Performance Optimization

### For Pendrive Usage

```bash
# Set temp directory on fast storage
export TMPDIR=/tmp

# Cortex will use it for temporary operations
python -m cortex.cli.main status
```

### For Large Datasets

```bash
# Aggressive consolidation
python -m cortex.cli.main consolidate --days 3

# Export and reset
python -m cortex.cli.main consolidate --export backup.json
# Then reset database if needed
rm ~/.cortex/cortex.db
```

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system details
- Check out the source code in `cortex/`
- Contribute improvements
- Share your knowledge exports with the community
