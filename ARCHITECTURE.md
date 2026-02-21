# Cortex Architecture

## Overview

Cortex is an intelligent, self-learning system agent that continuously learns from system activity, internet sources, documents, and sandbox experimentation. It implements a three-tier memory system (HOT/WARM/COLD) and uses LLMs only for interpretation and reasoning, not as permanent memory.

## Core Components

### 1. Memory System (`cortex/memory/`)

**Three-Tier Architecture:**

- **HOT Memory**: RAM-based cache for frequently accessed items (sub-millisecond lookup)
- **WARM Memory**: Main SQLite database for current knowledge
- **COLD Memory**: Archived historical data (compressed)

**Memory Types:**

- **Episodic Memory**: Stores experiences and events
- **Semantic Memory**: Stores structured facts with confidence scores
- **Skill Memory**: Stores validated workflows with success rates

**Files:**
- `schema.py`: Database schema definitions
- `database.py`: Database operations and CRUD methods

### 2. Brain Core (`cortex/core/`)

Central intelligence coordinator that manages:
- Memory operations
- Learning from observations
- Skill recall and reinforcement
- Session management

**Key Methods:**
- `observe()`: Record system events
- `learn_fact()`: Store semantic knowledge
- `learn_skill()`: Store validated workflows
- `recall_skill()`: Retrieve learned workflows
- `reinforce_skill()`: Update confidence based on execution results

### 3. Learning Engine (`cortex/learning/`)

Implements continuous learning through:
- Pattern detection in command sequences
- Workflow extraction
- Confidence scoring
- Success rate tracking

**Components:**
- `PatternDetector`: Identifies recurring patterns
- `Workflow`: Manages command sequences
- `LearningEngine`: Main learning orchestrator

### 4. Sandbox System (`cortex/sandbox/`)

Safe execution environment for testing:
- Isolated command execution
- Timeout protection
- Error capture and logging
- Success/failure evaluation

**Components:**
- `Sandbox`: Execution environment
- `SandboxResult`: Execution result container

### 5. CLI Interface (`cortex/cli/`)

User-facing command-line interface:

```bash
cortex learn "command"      # Learn from command execution
cortex ask "query"          # Query learned knowledge
cortex status               # System status
cortex memory stats         # Memory statistics
cortex sandbox run "cmd"    # Safe execution
cortex version              # Version info
```

## Learning Flow

```
Event/Task → Observe → Detect Pattern → Test in Sandbox 
    → Evaluate → Store Knowledge → Update Skills → Answer
```

### Learning Pipeline

1. **Observation**: Events and commands are recorded
2. **Pattern Detection**: Recurring sequences identified
3. **Sandbox Testing**: New workflows tested safely
4. **Evaluation**: Results analyzed
5. **Knowledge Storage**: Facts and skills stored with confidence
6. **Reinforcement**: Skills updated based on success/failure

## Reinforcement Learning

Confidence calculation:
```
confidence = (success_count + 1) / (success_count + failure_count + 2)
```

This formula:
- Starts neutral (0.5 with no data)
- Increases with successes
- Decreases with failures
- Gradually converges to actual success rate

## Database Schema

### Main Tables

1. **episodic_memory**: Event records
   - timestamp, event_type, command, result, duration, context

2. **semantic_memory**: Facts and knowledge
   - topic, fact, confidence, source, reliability

3. **skill_memory**: Learned workflows
   - skill_name, steps, confidence, success_count, failure_count

4. **sandbox_experiments**: Test execution records
   - experiment_type, plan, status, duration, logs

5. **sessions**: Grouped events
   - session_id, start_time, end_time, summary

## Memory Consolidation

Periodic maintenance process:
1. Summarize old sessions
2. Extract persistent knowledge
3. Archive raw data
4. Move to cold storage

Prevents database bloat while preserving insights.

## Portable Performance

For pendrive usage:
1. Copy `cortex.db` to RAM temp directory
2. Run using RAM database
3. Periodically sync back to persistent storage

Benefits:
- SSD-like speed on slow media
- Reduced wear on portable storage
- Faster queries

## Extension Points

### Adding New Learning Sources

Implement in `cortex/learning/`:
- Internet learning (hot learning)
- Document parsing (PDF, markdown)
- Repository analysis
- API documentation extraction

### Custom Workflows

Skills can be:
- Detected automatically from patterns
- Manually defined via API
- Imported from external sources
- Shared across Cortex instances

## Configuration

Environment variables:
- `CORTEX_HOME`: Base directory (default: `~/.cortex`)
- `CORTEX_SANDBOX_TIMEOUT`: Sandbox timeout in seconds
- `CORTEX_PATTERN_MIN`: Minimum pattern occurrences
- `CORTEX_CONFIDENCE_MIN`: Minimum confidence threshold

## Security Considerations

1. **Sandbox Isolation**: Commands run in isolated environment
2. **Permission Flow**: Risky operations require confirmation
3. **Source Validation**: Knowledge sources tracked with reliability
4. **Confidence Thresholds**: Low-confidence operations flagged

## Future Enhancements

### Stage 4: Research Intelligence
- Internet fetch for hot learning
- Document parsing (PDF, markdown)
- Knowledge provenance storage
- Source reliability scoring

### Stage 5: Lifelong Brain
- Background consolidation
- Hot/warm/cold lifecycle automation
- Proactive learning suggestions
- Multi-instance knowledge sharing

## Testing

Run tests:
```bash
python -m unittest discover tests
```

Run specific test:
```bash
python -m unittest tests.test_brain
```

## Performance Metrics

- Memory operations: < 10ms (WARM tier)
- Cache lookups: < 1ms (HOT tier)
- Pattern detection: O(n log n) for n events
- Database size: ~100KB per 1000 events (before consolidation)
