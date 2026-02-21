"""
Learning Engine - Continuous learning and pattern detection for Cortex.

This module provides intelligent learning capabilities, including pattern
detection, workflow recognition, and knowledge consolidation through the
integration with the Brain class.
"""
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re


class PatternDetector:
    """Detects patterns in command sequences and workflows.
    
    This class analyzes execution history to identify recurring patterns,
    command sequences, and behavioral workflows.
    """
    
    def __init__(self, min_occurrences: int = 3):
        """Initialize the pattern detector.
        
        Args:
            min_occurrences: Minimum times a pattern must occur to be recognized
        """
        self.min_occurrences = min_occurrences
        self.patterns: Dict[str, int] = {}
        self.sequences: List[Tuple[str, ...]] = []
    
    def add_command(self, command: str):
        """Track a command for pattern detection.
        
        Args:
            command: The command executed
        """
        if command:
            self.sequences.append((command,))
    
    def add_sequence(self, commands: List[str]):
        """Track a sequence of commands.
        
        Args:
            commands: List of commands executed in sequence
        """
        if commands:
            self.sequences.append(tuple(commands))
    
    def detect_patterns(self) -> Dict[str, int]:
        """Detect recurring patterns in command sequences.
        
        Returns:
            Dictionary of patterns with their occurrence counts
        """
        patterns = defaultdict(int)
        
        # Detect individual command patterns
        for seq in self.sequences:
            for cmd in seq:
                patterns[cmd] += 1
        
        # Filter by minimum occurrences
        return {
            pattern: count 
            for pattern, count in patterns.items() 
            if count >= self.min_occurrences
        }
    
    def detect_sequences(self, length: int = 2) -> List[Tuple[str, int]]:
        """Detect recurring command sequences.
        
        Args:
            length: Length of sequences to detect
            
        Returns:
            List of (sequence, count) tuples, sorted by frequency
        """
        subsequences = defaultdict(int)
        
        for seq in self.sequences:
            for i in range(len(seq) - length + 1):
                subseq = seq[i:i + length]
                subsequences[subseq] += 1
        
        # Filter and sort
        detected = [
            (seq, count)
            for seq, count in subsequences.items()
            if count >= self.min_occurrences
        ]
        return sorted(detected, key=lambda x: x[1], reverse=True)
    
    def get_pattern_confidence(self, pattern: str) -> float:
        """Calculate confidence for a pattern based on frequency.
        
        Args:
            pattern: The pattern to evaluate
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        detected = self.detect_patterns()
        if not detected:
            return 0.0
        
        count = detected.get(pattern, 0)
        max_count = max(detected.values())
        return count / max_count if max_count > 0 else 0.0


class Workflow:
    """Represents a learned workflow of commands and actions.
    
    A workflow is a sequence of commands that achieve a specific goal
    and can be reused for efficiency and consistency.
    """
    
    def __init__(self, 
                 name: str,
                 description: str = "",
                 steps: Optional[List[Dict[str, Any]]] = None):
        """Initialize a workflow.
        
        Args:
            name: Workflow identifier
            description: Human-readable description
            steps: List of workflow steps
        """
        self.name = name
        self.description = description
        self.steps = steps or []
        self.created_at = datetime.now()
        self.last_used = None
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_duration_ms = 0.0
        self.tags: Set[str] = set()
    
    def add_step(self, 
                command: str,
                description: str = "",
                optional: bool = False,
                timeout: Optional[int] = None) -> 'Workflow':
        """Add a step to the workflow.
        
        Args:
            command: Command to execute
            description: Description of what this step does
            optional: Whether this step is optional
            timeout: Timeout for this step in seconds
            
        Returns:
            Self for method chaining
        """
        step = {
            "command": command,
            "description": description,
            "optional": optional,
            "timeout": timeout
        }
        self.steps.append(step)
        return self
    
    def record_execution(self, success: bool, duration_ms: float):
        """Record workflow execution statistics.
        
        Args:
            success: Whether execution was successful
            duration_ms: Execution duration in milliseconds
        """
        self.execution_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.total_duration_ms += duration_ms
        self.last_used = datetime.now()
    
    def get_success_rate(self) -> float:
        """Get workflow success rate.
        
        Returns:
            Success rate as a percentage (0-100)
        """
        if self.execution_count == 0:
            return 0.0
        return (self.success_count / self.execution_count) * 100
    
    def get_average_duration(self) -> float:
        """Get average execution duration.
        
        Returns:
            Average duration in milliseconds
        """
        if self.execution_count == 0:
            return 0.0
        return self.total_duration_ms / self.execution_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary.
        
        Returns:
            Dictionary representation of the workflow
        """
        return {
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": self.get_success_rate(),
            "average_duration_ms": self.get_average_duration(),
            "tags": list(self.tags)
        }


class LearningEngine:
    """Intelligent learning system for Cortex.
    
    The LearningEngine detects patterns, learns workflows, and helps the
    system improve through continuous observation and analysis.
    
    Example:
        >>> engine = LearningEngine(brain)
        >>> engine.observe_command("ls -la", success=True)
        >>> patterns = engine.detect_patterns()
    """
    
    def __init__(self, brain=None):
        """Initialize the learning engine.
        
        Args:
            brain: Optional reference to Brain instance for memory integration
        """
        self.brain = brain
        self.pattern_detector = PatternDetector(min_occurrences=3)
        self.workflows: Dict[str, Workflow] = {}
        self.observations: List[Dict[str, Any]] = []
        self.command_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"count": 0, "success": 0, "failure": 0, "total_duration_ms": 0.0}
        )
        self.learning_sessions: List[Dict[str, Any]] = []
    
    def observe_command(self, 
                       command: str,
                       success: bool,
                       duration_ms: float,
                       output: Optional[str] = None,
                       context: Optional[str] = None) -> None:
        """Observe and record a command execution.
        
        Args:
            command: The command executed
            success: Whether execution was successful
            duration_ms: Execution duration in milliseconds
            output: Command output
            context: Additional context about the execution
        """
        observation = {
            "timestamp": datetime.now(),
            "command": command,
            "success": success,
            "duration_ms": duration_ms,
            "output": output,
            "context": context
        }
        
        self.observations.append(observation)
        self.pattern_detector.add_command(command)
        
        # Update command statistics
        stats = self.command_stats[command]
        stats["count"] += 1
        if success:
            stats["success"] += 1
        else:
            stats["failure"] += 1
        stats["total_duration_ms"] += duration_ms
        
        # Optionally integrate with brain
        if self.brain:
            self.brain.observe(
                event_type="command",
                command=command,
                result="success" if success else "failure",
                duration_ms=int(duration_ms),
                context=context
            )
    
    def observe_sequence(self,
                        commands: List[str],
                        success: bool,
                        duration_ms: float) -> None:
        """Observe and record a sequence of commands.
        
        Args:
            commands: List of commands executed
            success: Whether the sequence was successful
            duration_ms: Total execution duration in milliseconds
        """
        self.pattern_detector.add_sequence(commands)
        
        for cmd in commands:
            self.observe_command(cmd, success, duration_ms / len(commands))
    
    def detect_patterns(self) -> Dict[str, int]:
        """Detect recurring patterns in observations.
        
        Returns:
            Dictionary of patterns with occurrence counts
        """
        return self.pattern_detector.detect_patterns()
    
    def detect_sequences(self, 
                        length: int = 2,
                        min_confidence: float = 0.5) -> List[Tuple[str, int]]:
        """Detect recurring command sequences.
        
        Args:
            length: Length of sequences to detect
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of (sequence, count) tuples
        """
        sequences = self.pattern_detector.detect_sequences(length)
        
        # Filter by confidence if needed
        if min_confidence > 0:
            return [
                (seq, count) 
                for seq, count in sequences
                if self._calculate_sequence_confidence(seq) >= min_confidence
            ]
        return sequences
    
    def create_workflow(self,
                       name: str,
                       description: str = "",
                       steps: Optional[List[str]] = None) -> Workflow:
        """Create a new workflow.
        
        Args:
            name: Workflow name
            description: Workflow description
            steps: Initial list of commands
            
        Returns:
            Workflow instance
        """
        workflow = Workflow(name, description)
        
        if steps:
            for step in steps:
                workflow.add_step(step)
        
        self.workflows[name] = workflow
        
        # Learn in brain if available
        if self.brain:
            self.brain.learn_skill(
                skill_name=name,
                description=description,
                steps=steps or []
            )
        
        return workflow
    
    def get_workflow(self, name: str) -> Optional[Workflow]:
        """Retrieve a learned workflow.
        
        Args:
            name: Workflow name
            
        Returns:
            Workflow instance or None if not found
        """
        return self.workflows.get(name)
    
    def list_workflows(self, 
                      min_success_rate: float = 0.0) -> List[Workflow]:
        """List all learned workflows.
        
        Args:
            min_success_rate: Minimum success rate filter (0-100)
            
        Returns:
            List of workflows matching criteria
        """
        return [
            w for w in self.workflows.values()
            if w.get_success_rate() >= min_success_rate
        ]
    
    def get_command_stats(self, command: Optional[str] = None) -> Dict[str, Any]:
        """Get command execution statistics.
        
        Args:
            command: Specific command to get stats for, or None for all
            
        Returns:
            Statistics dictionary
        """
        if command:
            stats = self.command_stats.get(command, {})
            if not stats:
                return {"error": "Command not found"}
            
            return {
                "command": command,
                "total_executions": stats["count"],
                "successful": stats["success"],
                "failed": stats["failure"],
                "success_rate": (stats["success"] / stats["count"] * 100) if stats["count"] > 0 else 0.0,
                "average_duration_ms": stats["total_duration_ms"] / stats["count"] if stats["count"] > 0 else 0.0
            }
        
        # Return stats for all commands
        result = {}
        for cmd, stats in self.command_stats.items():
            result[cmd] = {
                "total_executions": stats["count"],
                "successful": stats["success"],
                "failed": stats["failure"],
                "success_rate": (stats["success"] / stats["count"] * 100) if stats["count"] > 0 else 0.0,
                "average_duration_ms": stats["total_duration_ms"] / stats["count"] if stats["count"] > 0 else 0.0
            }
        return result
    
    def get_insights(self) -> Dict[str, Any]:
        """Get insights from learning data.
        
        Returns:
            Dictionary of insights and recommendations
        """
        patterns = self.detect_patterns()
        sequences = self.detect_sequences()
        
        # Find most reliable commands
        reliable_commands = [
            cmd for cmd, stats in self.command_stats.items()
            if stats["count"] >= 3 and stats["success"] / stats["count"] >= 0.8
        ]
        
        # Find problematic commands
        problematic_commands = [
            cmd for cmd, stats in self.command_stats.items()
            if stats["count"] >= 3 and stats["success"] / stats["count"] < 0.5
        ]
        
        return {
            "total_observations": len(self.observations),
            "unique_commands": len(self.command_stats),
            "learned_workflows": len(self.workflows),
            "detected_patterns": len(patterns),
            "detected_sequences": len(sequences),
            "most_common_commands": [
                (cmd, stats["count"]) 
                for cmd, stats in sorted(
                    self.command_stats.items(),
                    key=lambda x: x[1]["count"],
                    reverse=True
                )[:5]
            ],
            "reliable_commands": reliable_commands,
            "problematic_commands": problematic_commands,
            "recommended_workflows": [
                (tuple(seq), count) for seq, count in sequences[:3]
            ]
        }
    
    def _calculate_sequence_confidence(self, sequence: Tuple[str, ...]) -> float:
        """Calculate confidence for a sequence.
        
        Args:
            sequence: Tuple of commands
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not sequence or not self.observations:
            return 0.0
        
        # Count occurrences
        count = 0
        for i, obs in enumerate(self.observations):
            if i + len(sequence) <= len(self.observations):
                subseq = tuple(
                    self.observations[i + j]["command"]
                    for j in range(len(sequence))
                )
                if subseq == sequence:
                    count += 1
        
        # Normalize to 0-1 range
        if not self.observations:
            return 0.0
        return min(count / len(self.observations), 1.0)
    
    def clear_observations(self, older_than: Optional[timedelta] = None):
        """Clear observations to manage memory.
        
        Args:
            older_than: If provided, only clear observations older than this timedelta
        """
        if older_than is None:
            self.observations.clear()
        else:
            cutoff = datetime.now() - older_than
            self.observations = [
                obs for obs in self.observations
                if obs["timestamp"] > cutoff
            ]
    
    def export_learning_data(self) -> Dict[str, Any]:
        """Export all learning data for persistence.
        
        Returns:
            Dictionary containing all learning data
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "observations_count": len(self.observations),
            "workflows": {
                name: workflow.to_dict()
                for name, workflow in self.workflows.items()
            },
            "command_stats": dict(self.command_stats),
            "patterns": self.detect_patterns(),
            "sequences": self.detect_sequences(),
            "insights": self.get_insights()
        }
