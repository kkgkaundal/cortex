#!/usr/bin/env python3
"""
Cortex Demo Script

This script demonstrates the key features of Cortex.
"""
import tempfile
import os
from cortex.core.brain import Brain
from cortex.learning.engine import LearningEngine
from cortex.sandbox.runner import Sandbox


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def demo_basic_learning():
    """Demonstrate basic learning capabilities."""
    print_header("1. Basic Learning & Memory")
    
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    brain = Brain(temp_db.name)
    
    # Learn some facts
    print("📚 Learning facts about Python...")
    brain.learn_fact(
        topic="python",
        fact="Python is a high-level programming language",
        confidence=0.9,
        source_type="system"
    )
    brain.learn_fact(
        topic="python",
        fact="Python supports multiple programming paradigms",
        confidence=0.85,
        source_type="system"
    )
    
    # Recall facts
    facts = brain.recall_facts(topic="python")
    print(f"✓ Learned {len(facts)} facts about Python")
    for fact in facts:
        print(f"  • {fact['fact']} (confidence: {fact['confidence']:.2f})")
    
    brain.close()
    os.remove(temp_db.name)


def demo_skill_learning():
    """Demonstrate skill learning and reinforcement."""
    print_header("2. Skill Learning & Reinforcement")
    
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    brain = Brain(temp_db.name)
    
    # Learn a skill
    print("🎯 Learning a deployment skill...")
    brain.learn_skill(
        skill_name="deploy_app",
        description="Deploy application to production",
        steps=["npm run build", "npm test", "npm run deploy"],
        confidence=0.5
    )
    
    print("Initial confidence: 0.50")
    
    # Simulate executions
    print("\n🔄 Executing skill multiple times...")
    successes = 0
    failures = 0
    
    for i in range(10):
        # Simulate: 8 successes, 2 failures
        success = i not in [3, 7]
        brain.reinforce_skill("deploy_app", success=success, duration_ms=5000)
        if success:
            successes += 1
        else:
            failures += 1
    
    # Check improved confidence
    skill = brain.recall_skill("deploy_app")
    print(f"✓ After {successes} successes and {failures} failures:")
    print(f"  • Confidence: {skill['confidence']:.2f}")
    print(f"  • Success rate: {successes}/{successes + failures}")
    
    brain.close()
    os.remove(temp_db.name)


def demo_pattern_detection():
    """Demonstrate pattern detection in commands."""
    print_header("3. Pattern Detection")
    
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    brain = Brain(temp_db.name)
    learning_engine = LearningEngine(brain)
    
    # Observe a repeated pattern
    print("🔍 Observing command patterns...")
    pattern = ["git add .", "git commit -m 'update'", "git push"]
    
    for iteration in range(3):
        print(f"  Iteration {iteration + 1}...")
        for cmd in pattern:
            learning_engine.observe_command(cmd, True, 100)
    
    # Detect patterns
    patterns = learning_engine.detect_patterns()
    print(f"\n✓ Detected {len(patterns)} unique commands")
    for cmd, count in list(patterns.items())[:3]:
        print(f"  • '{cmd}': {count} times")
    
    # Get insights
    insights = learning_engine.get_insights()
    print(f"\n✓ Generated insights:")
    print(f"  • Total observations: {insights.get('total_observations', 0)}")
    print(f"  • Unique commands: {insights.get('unique_commands', 0)}")
    
    brain.close()
    os.remove(temp_db.name)


def demo_sandbox():
    """Demonstrate sandbox execution."""
    print_header("4. Sandbox Execution")
    
    sandbox = Sandbox(timeout=5)
    
    # Test safe command
    print("🔒 Testing commands in sandbox...")
    result = sandbox.run("echo 'Hello from sandbox'")
    
    print(f"✓ Command executed:")
    print(f"  • Return code: {result.return_code}")
    print(f"  • Duration: {result.duration_ms}ms")
    print(f"  • Output: {result.stdout.strip()}")
    
    # Test command sequence
    print("\n🔒 Testing command sequence...")
    commands = ["echo 'Step 1'", "echo 'Step 2'", "echo 'Step 3'"]
    results = sandbox.run_sequence(commands)
    
    print(f"✓ Executed {len(results)} commands:")
    for i, res in enumerate(results, 1):
        status = "✓" if res.return_code == 0 else "✗"
        print(f"  {status} Step {i}: {res.duration_ms}ms")
    
    # Get stats
    stats = sandbox.get_stats()
    success_rate = stats['successful'] / stats['total_commands'] if stats['total_commands'] > 0 else 0
    print(f"\n📊 Sandbox statistics:")
    print(f"  • Total commands: {stats['total_commands']}")
    print(f"  • Successful: {stats['successful']}")
    print(f"  • Success rate: {success_rate:.1%}")


def demo_session_tracking():
    """Demonstrate session tracking."""
    print_header("5. Session Tracking")
    
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    brain = Brain(temp_db.name)
    
    # Start session
    print("📝 Starting learning session...")
    session_id = brain.start_session("demo session")
    print(f"✓ Session created: {session_id[:8]}...")
    
    # Record some events
    print("\n📊 Recording events...")
    brain.observe(
        event_type="command",
        command="npm install",
        result="success",
        duration_ms=5000
    )
    brain.observe(
        event_type="command",
        command="npm test",
        result="success",
        duration_ms=10000
    )
    
    print("✓ Recorded 2 events")
    
    # End session
    brain.end_session("completed successfully")
    print("✓ Session ended")
    
    # Get stats
    stats = brain.get_stats()
    print(f"\n📊 Brain statistics:")
    print(f"  • Episodic memories: {stats['episodic_count']}")
    print(f"  • Sessions: {stats['session_count']}")
    print(f"  • Database size: {stats['db_size_bytes']} bytes")
    
    brain.close()
    os.remove(temp_db.name)


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("  CORTEX SYSTEM DEMONSTRATION")
    print("  Event-Driven, Self-Learning System Agent")
    print("=" * 60)
    
    try:
        demo_basic_learning()
        demo_skill_learning()
        demo_pattern_detection()
        demo_sandbox()
        demo_session_tracking()
        
        print_header("Demo Complete!")
        print("✓ All features demonstrated successfully")
        print("\nNext steps:")
        print("  • Run 'python -m cortex.cli.main --help' for CLI usage")
        print("  • Read USAGE_GUIDE.md for detailed examples")
        print("  • Check ARCHITECTURE.md for system design")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
