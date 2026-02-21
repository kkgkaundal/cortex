"""
Sandbox Runner - Safe command execution environment for Cortex.

This module provides secure execution of commands in an isolated environment
with timeout support, environment variable management, and result tracking.
"""
import subprocess
import time
import os
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple, Any
from datetime import datetime


@dataclass
class SandboxResult:
    """Result of a sandboxed command execution.
    
    Attributes:
        command: The command that was executed
        return_code: Exit code of the command (0 for success)
        stdout: Standard output from the command
        stderr: Standard error output from the command
        duration_ms: Execution duration in milliseconds
        timeout: Whether the command timed out
        timestamp: When the command was executed
        environment: Dictionary of environment variables used
    """
    command: str
    return_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_ms: float = 0.0
    timeout: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    environment: Dict[str, str] = field(default_factory=dict)
    
    def success(self) -> bool:
        """Check if the command executed successfully.
        
        Returns:
            True if return_code is 0 and no timeout occurred
        """
        return self.return_code == 0 and not self.timeout
    
    def get_output(self) -> str:
        """Get combined stdout and stderr.
        
        Returns:
            Combined output from stdout and stderr
        """
        output = self.stdout
        if self.stderr:
            output += f"\n{self.stderr}"
        return output
    
    def __str__(self) -> str:
        """Return human-readable result summary."""
        status = "SUCCESS" if self.success() else "FAILED"
        timeout_msg = " (TIMEOUT)" if self.timeout else ""
        return f"{status}{timeout_msg}: {self.command} (exit={self.return_code}, {self.duration_ms:.2f}ms)"


class Sandbox:
    """Safe execution environment for running commands with resource controls.
    
    The Sandbox class provides a controlled environment for command execution
    with timeout support, environment variable management, and result tracking.
    
    Example:
        >>> sandbox = Sandbox(timeout=30)
        >>> result = sandbox.run("ls -la")
        >>> if result.success():
        ...     print(result.stdout)
    """
    
    def __init__(self, 
                 timeout: int = 30,
                 env: Optional[Dict[str, str]] = None,
                 cwd: Optional[str] = None,
                 shell: bool = False):
        """Initialize the Sandbox.
        
        Args:
            timeout: Command execution timeout in seconds (default: 30)
            env: Dictionary of environment variables to use. If None, inherits
                 from parent process.
            cwd: Working directory for command execution. If None, uses current
                 directory.
            shell: Whether to run command through shell (default: False).
                   Only set to True if absolutely necessary.
        """
        self.timeout = timeout
        self.env = env if env is not None else os.environ.copy()
        self.cwd = cwd or os.getcwd()
        self.shell = shell
        self.execution_history: List[SandboxResult] = []
        
    def run(self, 
            command: str,
            timeout: Optional[int] = None,
            env: Optional[Dict[str, str]] = None,
            cwd: Optional[str] = None) -> SandboxResult:
        """Execute a command in the sandbox.
        
        Args:
            command: The command to execute
            timeout: Override default timeout in seconds. If None, uses instance timeout.
            env: Override environment variables for this command only
            cwd: Override working directory for this command only
            
        Returns:
            SandboxResult containing command output and metadata
            
        Raises:
            ValueError: If command is empty
        """
        if not command or not command.strip():
            raise ValueError("Command cannot be empty")
        
        # Use provided values or fall back to instance defaults
        exec_timeout = timeout if timeout is not None else self.timeout
        exec_env = env if env is not None else self.env
        exec_cwd = cwd if cwd is not None else self.cwd
        
        start_time = time.time()
        result = SandboxResult(command=command, environment=exec_env)
        
        try:
            # Execute the command with subprocess
            process = subprocess.Popen(
                command if self.shell else command.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=exec_env,
                cwd=exec_cwd,
                shell=self.shell,
                text=True
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=exec_timeout)
                result.stdout = stdout
                result.stderr = stderr
                result.return_code = process.returncode
                result.timeout = False
            except subprocess.TimeoutExpired:
                # Kill the process if timeout exceeded
                process.kill()
                stdout, stderr = process.communicate()
                result.stdout = stdout or ""
                result.stderr = stderr or ""
                result.return_code = process.returncode or -1
                result.timeout = True
                
        except OSError as e:
            result.stderr = f"Error executing command: {str(e)}"
            result.return_code = -1
            result.timeout = False
        except Exception as e:
            result.stderr = f"Unexpected error: {str(e)}"
            result.return_code = -1
            result.timeout = False
        finally:
            # Calculate duration
            duration_sec = time.time() - start_time
            result.duration_ms = duration_sec * 1000
            
            # Store in history
            self.execution_history.append(result)
        
        return result
    
    def run_sequence(self, 
                    commands: List[str],
                    stop_on_error: bool = True) -> List[SandboxResult]:
        """Execute a sequence of commands.
        
        Args:
            commands: List of commands to execute sequentially
            stop_on_error: If True, stop execution on first failure
            
        Returns:
            List of SandboxResult objects for each command
        """
        results = []
        for command in commands:
            result = self.run(command)
            results.append(result)
            if stop_on_error and not result.success():
                break
        return results
    
    def get_history(self) -> List[SandboxResult]:
        """Get execution history.
        
        Returns:
            List of all command executions in chronological order
        """
        return self.execution_history.copy()
    
    def clear_history(self):
        """Clear execution history."""
        self.execution_history.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get sandbox execution statistics.
        
        Returns:
            Dictionary containing execution statistics
        """
        if not self.execution_history:
            return {
                "total_commands": 0,
                "successful": 0,
                "failed": 0,
                "timeouts": 0,
                "total_duration_ms": 0.0,
                "average_duration_ms": 0.0
            }
        
        successful = sum(1 for r in self.execution_history if r.success())
        failed = len(self.execution_history) - successful
        timeouts = sum(1 for r in self.execution_history if r.timeout)
        total_duration = sum(r.duration_ms for r in self.execution_history)
        
        return {
            "total_commands": len(self.execution_history),
            "successful": successful,
            "failed": failed,
            "timeouts": timeouts,
            "total_duration_ms": total_duration,
            "average_duration_ms": total_duration / len(self.execution_history)
        }
    
    def update_env(self, env_dict: Dict[str, str]):
        """Update sandbox environment variables.
        
        Args:
            env_dict: Dictionary of environment variables to add/update
        """
        self.env.update(env_dict)
    
    def set_timeout(self, timeout: int):
        """Update the default timeout.
        
        Args:
            timeout: Timeout in seconds
            
        Raises:
            ValueError: If timeout is not positive
        """
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        self.timeout = timeout
