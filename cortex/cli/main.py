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
    ctx.obj["sandbox"] = Sandbox(timeout=30)


@cortex.command()
@click.argument("command", type=str)
@click.option("--context", "-c", help="Optional context for the learning observation")
@click.option("--timeout", "-t", type=int, help="Execution timeout in seconds")
@click.option("--session", "-s", help="Session ID to associate this learning with")
@click.pass_context
def learn(ctx, command: str, context: Optional[str], timeout: Optional[int], session: Optional[str]):
    """Learn from executing a command.
    
    Executes a command in the sandbox and records the execution for pattern
    detection and workflow learning.
    
    Example:
        cortex learn "npm run build"
        cortex learn "git status" --context "checking repository"
    """
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


def main():
    """Entry point for the CLI."""
    cortex(obj={})


if __name__ == "__main__":
    main()
