"""
Cortex CLI - Command-line interface for Cortex intelligent system.

This module provides the main command-line interface for interacting with Cortex,
including commands for learning, querying, memory management, and sandbox execution.

Usage:
    cortex --help
    cortex learn "python script.py"
    cortex ask "what should I do next?"
    cortex status
"""
import click
import json
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import sys

# Import Cortex components
from cortex.core.brain import Brain
from cortex.learning.engine import LearningEngine
from cortex.sandbox.runner import Sandbox


# Global context for click
@click.group()
@click.pass_context
def cortex(ctx):
    """Cortex - Intelligent learning and task automation system.
    
    Cortex learns from your commands and workflows to help you work more
    efficiently and effectively.
    """
    # Initialize context object for sharing state
    if ctx.obj is None:
        ctx.obj = {}
    
    # Initialize Brain and LearningEngine
    db_path = Path.home() / ".cortex" / "cortex.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    ctx.obj["brain"] = Brain(str(db_path))
    ctx.obj["learning_engine"] = LearningEngine(ctx.obj["brain"])
    ctx.obj["sandbox"] = Sandbox(timeout=30, shell=True)


@cortex.command()
@click.argument("command", type=str)
@click.option("--context", "-c", help="Optional context for the learning observation")
@click.option("--timeout", "-t", type=int, help="Execution timeout in seconds")
@click.option("--session", "-s", help="Session ID to associate this learning with")
@click.option("--topic", is_flag=True, help="Learn about the topic through research instead of executing")
@click.pass_context
def learn(ctx, command: str, context: Optional[str], timeout: Optional[int], session: Optional[str], topic: bool):
    """Learn from executing a command or research a topic.
    
    By default, executes a command in the sandbox and records the execution.
    With --topic flag, researches the topic instead of executing it.
    
    Example:
        cortex learn "npm run build"
        cortex learn "git status" --context "checking repository"
        cortex learn "python" --topic
        cortex learn "John Doe" --topic
    """
    # List of commands that typically start interactive sessions
    INTERACTIVE_COMMANDS = [
        'python', 'python3', 'node', 'irb', 'ruby', 'php', 'perl',
        'bash', 'sh', 'zsh', 'fish', 'ipython', 'julia', 'R',
        'psql', 'mysql', 'mongo', 'redis-cli', 'sqlite3'
    ]
    
    # Check if command looks like a topic/name rather than a command
    def looks_like_topic(text: str) -> bool:
        """Detect if input is likely a topic/name rather than a command."""
        parts = text.strip().split()
        
        if not parts:
            return False
        
        first_word = parts[0]
        
        # Check for file paths or script execution patterns
        if any(char in first_word for char in ['/', '.sh', '.py', '.js', '.rb']):
            return False
        
        # Known command starts
        common_cmd_patterns = ['sudo', 'npm', 'git', 'docker', 'python', 'node', 'go', 'cargo', 'make']
        if first_word.lower() in common_cmd_patterns:
            return False
        
        # Common shell commands
        common_commands = ['ls', 'cd', 'cat', 'grep', 'find', 'echo', 'mkdir', 'rm', 'cp', 'mv', 'chmod', 'chown']
        if first_word.lower() in common_commands:
            return False
        
        # Multiple capitalized words (likely a name or title)
        if len(parts) > 1 and all(p[0].isupper() for p in parts if p and p[0].isalpha()):
            return True
        
        # Contains punctuation that suggests a question or sentence
        if any(char in text for char in ['?', '!', ';', ':']):
            return True
        
        # If it has spaces and first word isn't recognized as command
        if len(parts) > 1:
            # Check for common command patterns
            if not any(text.startswith(pattern) for pattern in ['-', '--']):
                return True
        
        return False
    
    # Check if command might be interactive or a topic
    cmd_parts = command.strip().split()
    base_cmd = cmd_parts[0] if cmd_parts else ""
    is_likely_interactive = base_cmd in INTERACTIVE_COMMANDS and len(cmd_parts) == 1
    is_likely_topic = looks_like_topic(command)
    
    # If --topic flag is set or command is interactive/topic-like, do research
    if topic or is_likely_interactive or is_likely_topic:
        if is_likely_topic and not topic and not is_likely_interactive:
            click.echo(f"💡 '{command}' appears to be a topic rather than a command.")
            click.echo(f"    Switching to research mode...")
            click.echo()
        elif is_likely_interactive and not topic:
            click.echo(f"⚠️  '{command}' starts an interactive session.")
            click.echo(f"💡 Tip: Use 'cortex learn \"{command}\" --topic' to research this topic")
            click.echo(f"    or provide arguments: 'cortex learn \"{command} --version\"'")
            click.echo()
            if not click.confirm("Do you want to research this topic instead?"):
                click.echo("Cancelled.")
                return
        
        # Research mode
        try:
            from cortex.learning.internet import InternetLearner
        except ImportError:
            click.echo("⚠️  Internet learning module not available.")
            click.echo("💡 Alternatively, use: cortex research \"<query>\" <topic>")
            click.echo()
            click.echo("For now, storing as a semantic fact...")
            brain = ctx.obj["brain"]
            topic_name = base_cmd if is_likely_interactive else command
            brain.learn_fact(
                topic=topic_name,
                fact=f"User wants to learn about {topic_name}",
                source_type="user_request",
                confidence=0.5
            )
            click.echo(f"✓ Noted interest in learning about '{topic_name}'")
            return
        
        topic_name = base_cmd if is_likely_interactive else command
        click.echo(f"🔍 Researching topic: {topic_name}")
        click.echo()
        
        brain = ctx.obj["brain"]
        learner = InternetLearner(brain)
        
        try:
            knowledge = learner.search_and_learn(
                query=f"what is {topic_name}",
                topic=topic_name
            )
            
            click.echo(f"✓ Research completed!")
            click.echo()
            click.echo(f"📊 Results:")
            click.echo(f"  • Sources found: {len(knowledge['sources'])}")
            click.echo(f"  • Facts learned: {len(knowledge['facts'])}")
            click.echo(f"  • Steps extracted: {len(knowledge['steps'])}")
            click.echo(f"  • Reliability: {knowledge['reliability']:.2f}")
            click.echo()
            
            if knowledge['facts']:
                click.echo("📝 Key facts learned:")
                for i, fact in enumerate(knowledge['facts'][:3], 1):
                    click.echo(f"  {i}. {fact[:100]}...")
                click.echo()
            
            click.echo(f"💡 Use 'cortex ask \"tell me about {topic_name}\"' to recall this knowledge")
            
        except Exception as e:
            click.echo(f"✗ Research failed: {e}", err=True)
            sys.exit(1)
        
        return
    
    # Normal execution mode
    try:
        brain = ctx.obj["brain"]
        learning_engine = ctx.obj["learning_engine"]
        sandbox = ctx.obj["sandbox"]
        
        # Start session if provided
        if session:
            brain.current_session_id = session
        elif not brain.current_session_id:
            brain.start_session(context)
        
        click.echo(f"📚 Learning: {command}")
        
        # Execute command with specified or default timeout
        if timeout:
            result = sandbox.run(command, timeout=timeout)
        else:
            result = sandbox.run(command)
        
        # Record in learning engine
        learning_engine.observe_command(
            command=command,
            success=result.success(),
            duration_ms=result.duration_ms,
            output=result.stdout,
            context=context
        )
        
        # Display result
        click.echo(f"✓ {result}")
        
        if result.stdout:
            click.echo(f"\nOutput:\n{result.stdout}")
        
        if result.stderr:
            click.echo(f"\nErrors:\n{result.stderr}", err=True)
        
        click.echo(f"\n⏱️  Duration: {result.duration_ms:.2f}ms")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)
    finally:
        if ctx.obj["brain"].current_session_id and not session:
            ctx.obj["brain"].end_session()


@cortex.command()
@click.argument("query", type=str)
@click.option("--limit", "-l", type=int, default=5, help="Number of results to return")
@click.pass_context
def ask(ctx, query: str, limit: int):
    """Ask Cortex a question about learned knowledge.
    
    Query the brain for relevant knowledge, patterns, and recommendations
    based on observations and learning.
    
    Example:
        cortex ask "what are common workflows?"
        cortex ask "how to improve build times?"
    """
    try:
        learning_engine = ctx.obj["learning_engine"]
        brain = ctx.obj["brain"]
        
        click.echo(f"🧠 Query: {query}\n")
        
        # Get insights
        insights = learning_engine.get_insights()
        
        # Check query type and respond
        if any(word in query.lower() for word in ["pattern", "common", "frequent"]):
            patterns = learning_engine.detect_patterns()
            if patterns:
                click.echo("📊 Common patterns detected:")
                for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:limit]:
                    click.echo(f"  • {pattern} (seen {count} times)")
            else:
                click.echo("No patterns detected yet.")
        
        elif any(word in query.lower() for word in ["workflow", "sequence", "chain"]):
            sequences = learning_engine.detect_sequences()
            if sequences:
                click.echo("🔄 Recommended command sequences:")
                for seq, count in sequences[:limit]:
                    click.echo(f"  • {' → '.join(seq)} (used {count} times)")
            else:
                click.echo("No sequences detected yet.")
        
        elif any(word in query.lower() for word in ["improve", "optimize", "problem", "issue"]):
            click.echo("💡 Insights and recommendations:")
            
            if insights.get("problematic_commands"):
                click.echo("\n⚠️  Commands with low success rates:")
                for cmd in insights["problematic_commands"][:limit]:
                    stats = learning_engine.get_command_stats(cmd)
                    click.echo(f"  • {cmd} ({stats['success_rate']:.1f}% success rate)")
            
            if insights.get("reliable_commands"):
                click.echo("\n✅ Most reliable commands:")
                for cmd in insights["reliable_commands"][:limit]:
                    stats = learning_engine.get_command_stats(cmd)
                    click.echo(f"  • {cmd} ({stats['success_rate']:.1f}% success rate)")
        
        elif any(word in query.lower() for word in ["about", "what is", "tell me", "explain"]):
            # Search for semantic knowledge
            # Extract topic from query
            topic_words = query.lower().replace("about", "").replace("what is", "").replace("tell me", "").replace("explain", "").strip().split()
            
            if topic_words:
                # Try each potential topic word
                found_facts = False
                for topic in topic_words:
                    facts = brain.recall_facts(topic=topic, min_confidence=0.0)
                    if facts:
                        found_facts = True
                        click.echo(f"📚 Knowledge about '{topic}':")
                        click.echo()
                        for fact in facts[:limit]:
                            click.echo(f"  • {fact['fact']}")
                            click.echo(f"    Source: {fact.get('source_type', 'unknown')} | Confidence: {fact['confidence']:.2f}")
                            click.echo()
                        break
                
                if not found_facts:
                    click.echo(f"No knowledge found about these topics yet.")
                    click.echo(f"💡 Try: cortex learn \"{' '.join(topic_words)}\" --topic")
            else:
                click.echo("Please specify what you want to know about.")
        
        else:
            # Default: show general insights
            click.echo("📈 Learning Statistics:")
            click.echo(f"  • Total observations: {insights['total_observations']}")
            click.echo(f"  • Unique commands: {insights['unique_commands']}")
            click.echo(f"  • Learned workflows: {insights['learned_workflows']}")
            click.echo(f"  • Detected patterns: {insights['detected_patterns']}")
            click.echo(f"  • Detected sequences: {insights['detected_sequences']}")
            
            if insights.get("most_common_commands"):
                click.echo("\n🎯 Most common commands:")
                for cmd, count in insights["most_common_commands"][:limit]:
                    click.echo(f"  • {cmd} (used {count} times)")
        
        click.echo()
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cortex.command()
@click.pass_context
def status(ctx):
    """Show current system status and statistics.
    
    Displays comprehensive information about Cortex's current state,
    including memory usage, learning progress, and system statistics.
    """
    try:
        brain = ctx.obj["brain"]
        learning_engine = ctx.obj["learning_engine"]
        sandbox = ctx.obj["sandbox"]
        
        click.echo("=" * 60)
        click.echo("🧠 CORTEX STATUS")
        click.echo("=" * 60)
        
        # Memory stats
        click.echo("\n📊 Memory Statistics:")
        mem_stats = brain.get_stats()
        for key, value in mem_stats.items():
            # Format numbers nicely
            if isinstance(value, int):
                click.echo(f"  • {key}: {value}")
            elif isinstance(value, float):
                click.echo(f"  • {key}: {value:.2f}")
            else:
                click.echo(f"  • {key}: {value}")
        
        # Learning progress
        insights = learning_engine.get_insights()
        click.echo("\n🎓 Learning Progress:")
        click.echo(f"  • Total observations: {insights['total_observations']}")
        click.echo(f"  • Unique commands learned: {insights['unique_commands']}")
        click.echo(f"  • Workflows created: {insights['learned_workflows']}")
        click.echo(f"  • Patterns detected: {insights['detected_patterns']}")
        click.echo(f"  • Sequences detected: {insights['detected_sequences']}")
        
        # Sandbox statistics
        click.echo("\n🔒 Sandbox Execution Statistics:")
        sandbox_stats = sandbox.get_stats()
        for key, value in sandbox_stats.items():
            if isinstance(value, float):
                click.echo(f"  • {key}: {value:.2f}")
            else:
                click.echo(f"  • {key}: {value}")
        
        # Session info
        click.echo("\n⏱️  Session Information:")
        if brain.current_session_id:
            click.echo(f"  • Active session: {brain.current_session_id}")
        else:
            click.echo("  • No active session")
        
        click.echo("\n" + "=" * 60)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cortex.group()
def memory():
    """Manage Cortex memory systems.
    
    Commands for viewing, managing, and optimizing memory systems.
    """
    pass


@memory.command("stats")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text",
              help="Output format")
@click.pass_context
def memory_stats(ctx, format: str):
    """Display detailed memory statistics.
    
    Shows comprehensive breakdown of memory usage across different
    memory systems (episodic, semantic, procedural).
    """
    try:
        brain = ctx.obj["brain"]
        learning_engine = ctx.obj["learning_engine"]
        
        stats = {
            "timestamp": datetime.now().isoformat(),
            "brain_stats": brain.get_stats(),
            "learning_insights": learning_engine.get_insights(),
            "command_statistics": learning_engine.get_command_stats()
        }
        
        if format == "json":
            click.echo(json.dumps(stats, indent=2, default=str))
        else:
            click.echo("=" * 60)
            click.echo("💾 DETAILED MEMORY STATISTICS")
            click.echo("=" * 60)
            
            click.echo("\n🧠 Brain Statistics:")
            for key, value in stats["brain_stats"].items():
                click.echo(f"  {key}: {value}")
            
            click.echo("\n📚 Learning Insights:")
            insights = stats["learning_insights"]
            click.echo(f"  Total observations: {insights['total_observations']}")
            click.echo(f"  Unique commands: {insights['unique_commands']}")
            click.echo(f"  Workflows: {insights['learned_workflows']}")
            click.echo(f"  Patterns: {insights['detected_patterns']}")
            click.echo(f"  Sequences: {insights['detected_sequences']}")
            
            if insights.get("most_common_commands"):
                click.echo("\n  Top commands:")
                for cmd, count in insights["most_common_commands"][:5]:
                    click.echo(f"    • {cmd}: {count} times")
            
            click.echo("\n" + "=" * 60)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cortex.group()
def sandbox():
    """Manage sandbox execution environment.
    
    Commands for executing commands safely in an isolated environment.
    """
    pass


@sandbox.command("run")
@click.argument("command", type=str)
@click.option("--timeout", "-t", type=int, default=30, help="Execution timeout in seconds")
@click.option("--env", "-e", multiple=True, help="Environment variables (KEY=VALUE)")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text",
              help="Output format")
@click.pass_context
def sandbox_run(ctx, command: str, timeout: int, env: tuple, format: str):
    """Execute a command in the sandbox.
    
    Safely executes a command in an isolated environment with timeout
    and resource controls.
    
    Example:
        cortex sandbox run "ls -la"
        cortex sandbox run "npm test" --timeout 60
        cortex sandbox run "echo test" -e KEY=value
    """
    try:
        sandbox_obj = ctx.obj["sandbox"]
        
        # Parse environment variables
        env_dict = {}
        for env_var in env:
            if "=" in env_var:
                key, value = env_var.split("=", 1)
                env_dict[key] = value
        
        click.echo(f"🔒 Executing in sandbox: {command}")
        
        # Run command
        result = sandbox_obj.run(command, timeout=timeout, env=env_dict or None)
        
        if format == "json":
            output = {
                "command": result.command,
                "success": result.success(),
                "return_code": result.return_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_ms": result.duration_ms,
                "timeout": result.timeout,
                "timestamp": result.timestamp.isoformat()
            }
            click.echo(json.dumps(output, indent=2))
        else:
            click.echo(f"\n{result}")
            
            if result.stdout:
                click.echo(f"\n📤 Output:\n{result.stdout}")
            
            if result.stderr:
                click.echo(f"\n⚠️  Errors:\n{result.stderr}")
            
            click.echo(f"\n⏱️  Duration: {result.duration_ms:.2f}ms")
        
        # Return non-zero exit code if command failed
        if not result.success():
            sys.exit(result.return_code or 1)
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cortex.command()
@click.pass_context
def version(ctx):
    """Show Cortex version information."""
    click.echo("Cortex v0.1.0")
    click.echo("Intelligent Learning and Task Automation System")



@cortex.command()
@click.argument("query", type=str)
@click.argument("topic", type=str)
@click.pass_context
def research(ctx, query: str, topic: str):
    """Research a topic from internet sources.
    
    Example:
        cortex research "deploy nextjs" deployment
    """
    from cortex.learning.internet import InternetLearner
    
    click.echo(f"🔍 Researching: {query}")
    click.echo(f"📝 Topic: {topic}")
    click.echo()
    
    brain = ctx.obj["brain"]
    learner = InternetLearner(brain)
    
    try:
        knowledge = learner.search_and_learn(query, topic)
        
        click.echo(f"✓ Research completed!")
        click.echo()
        click.echo(f"📊 Results:")
        click.echo(f"  • Sources found: {len(knowledge['sources'])}")
        click.echo(f"  • Facts learned: {len(knowledge['facts'])}")
        click.echo(f"  • Steps extracted: {len(knowledge['steps'])}")
        click.echo(f"  • Reliability: {knowledge['reliability']:.2f}")
        click.echo()
        
        if knowledge['sources']:
            click.echo("📚 Sources:")
            for source in knowledge['sources']:
                click.echo(f"  • {source['title']}")
                click.echo(f"    {source['url']}")
        
    except Exception as e:
        click.echo(f"✗ Research failed: {e}", err=True)
        sys.exit(1)


@cortex.command()
@click.option("--days", default=7, help="Archive data older than this many days")
@click.option("--export", help="Export knowledge base to file")
@click.pass_context
def consolidate(ctx, days: int, export: Optional[str]):
    """Consolidate and maintain memory systems.
    
    Example:
        cortex consolidate --days 7
        cortex consolidate --export knowledge.json
    """
    from cortex.memory.consolidation import MemoryConsolidator
    from cortex.utils.config import config
    
    brain = ctx.obj["brain"]
    
    click.echo("🔧 Starting memory consolidation...")
    click.echo()
    
    consolidator = MemoryConsolidator(
        db_path=config.get_db_path(),
        archive_dir=config.get_archive_dir()
    )
    
    try:
        if export:
            # Export knowledge base
            click.echo(f"�� Exporting knowledge base to {export}...")
            result = consolidator.export_knowledge_base(export)
            
            click.echo(f"✓ Export completed!")
            click.echo()
            click.echo(f"📊 Exported:")
            click.echo(f"  • Semantic memories: {result['semantic_count']}")
            click.echo(f"  • Skills: {result['skill_count']}")
            click.echo(f"  • Sessions: {result['session_count']}")
            click.echo(f"  • Output file: {result['output_file']}")
        else:
            # Run consolidation
            report = consolidator.consolidate(days_threshold=days)
            
            click.echo(f"✓ Consolidation completed!")
            click.echo()
            click.echo(f"📊 Operations:")
            for op in report['operations']:
                click.echo(f"  • {op['operation']}: {op['count']} records")
            
            click.echo()
            click.echo(f"⏱️  Started: {report['started_at']}")
            click.echo(f"⏱️  Completed: {report.get('completed_at', 'N/A')}")
            
    except Exception as e:
        click.echo(f"✗ Consolidation failed: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cortex(obj={})


if __name__ == "__main__":
    main()

