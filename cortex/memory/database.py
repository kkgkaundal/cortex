"""
Database manager for Cortex memory system.
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from .schema import get_schema


class MemoryDatabase:
    """Manages SQLite database operations for Cortex memory."""
    
    def __init__(self, db_path: str = "cortex.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self._hot_cache = {}  # In-memory cache for hot tier
        
    def connect(self):
        """Establish database connection and initialize schema."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._initialize_schema()
        
    def _initialize_schema(self):
        """Create tables if they don't exist."""
        cursor = self.conn.cursor()
        cursor.executescript(get_schema())
        self.conn.commit()
        
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        try:
            yield self.conn
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
            
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            
    # Episodic Memory Operations
    def add_episodic_memory(self, event_type: str, command: str = None, 
                          result: str = None, duration_ms: int = None,
                          context: str = None, session_id: str = None) -> int:
        """Add an episodic memory entry."""
        with self.transaction():
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO episodic_memory 
                (event_type, command, result, duration_ms, context, session_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (event_type, command, result, duration_ms, context, session_id))
            return cursor.lastrowid
            
    def get_episodic_memories(self, session_id: str = None, 
                             limit: int = 100) -> List[Dict]:
        """Retrieve episodic memories."""
        cursor = self.conn.cursor()
        if session_id:
            cursor.execute("""
                SELECT * FROM episodic_memory 
                WHERE session_id = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (session_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM episodic_memory 
                ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
        
    # Semantic Memory Operations
    def add_semantic_memory(self, topic: str, fact: str, confidence: float = 0.5,
                          source: str = None, source_type: str = None,
                          reliability: float = 0.5) -> int:
        """Add a semantic memory entry."""
        with self.transaction():
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO semantic_memory 
                (topic, fact, confidence, source, source_type, reliability)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (topic, fact, confidence, source, source_type, reliability))
            return cursor.lastrowid
            
    def get_semantic_memories(self, topic: str = None, 
                             min_confidence: float = 0.0,
                             limit: int = 100) -> List[Dict]:
        """Retrieve semantic memories."""
        cursor = self.conn.cursor()
        if topic:
            cursor.execute("""
                SELECT * FROM semantic_memory 
                WHERE topic = ? AND confidence >= ?
                ORDER BY confidence DESC, access_count DESC LIMIT ?
            """, (topic, min_confidence, limit))
        else:
            cursor.execute("""
                SELECT * FROM semantic_memory 
                WHERE confidence >= ?
                ORDER BY confidence DESC, access_count DESC LIMIT ?
            """, (min_confidence, limit))
        return [dict(row) for row in cursor.fetchall()]
        
    def update_semantic_access(self, memory_id: int):
        """Update access count for a semantic memory."""
        with self.transaction():
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE semantic_memory 
                SET access_count = access_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (memory_id,))
            
    # Skill Memory Operations
    def add_skill(self, skill_name: str, description: str = None,
                 steps: List[str] = None, prerequisites: List[str] = None,
                 confidence: float = 0.5) -> int:
        """Add a skill to memory."""
        steps_json = json.dumps(steps) if steps else None
        prereq_json = json.dumps(prerequisites) if prerequisites else None
        
        with self.transaction():
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO skill_memory 
                (skill_name, description, steps, prerequisites, confidence)
                VALUES (?, ?, ?, ?, ?)
            """, (skill_name, description, steps_json, prereq_json, confidence))
            return cursor.lastrowid
            
    def get_skill(self, skill_name: str) -> Optional[Dict]:
        """Retrieve a skill by name."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM skill_memory WHERE skill_name = ?
        """, (skill_name,))
        row = cursor.fetchone()
        if row:
            skill = dict(row)
            if skill['steps']:
                skill['steps'] = json.loads(skill['steps'])
            if skill['prerequisites']:
                skill['prerequisites'] = json.loads(skill['prerequisites'])
            return skill
        return None
        
    def update_skill_stats(self, skill_name: str, success: bool, 
                          duration_ms: int = None):
        """Update skill statistics after execution."""
        with self.transaction():
            cursor = self.conn.cursor()
            
            # Get current stats
            cursor.execute("""
                SELECT success_count, failure_count, avg_duration_ms 
                FROM skill_memory WHERE skill_name = ?
            """, (skill_name,))
            row = cursor.fetchone()
            
            if row:
                success_count = row['success_count']
                failure_count = row['failure_count']
                avg_duration = row['avg_duration_ms']
                
                # Update counts
                if success:
                    success_count += 1
                else:
                    failure_count += 1
                    
                # Calculate new confidence
                total = success_count + failure_count
                confidence = (success_count + 1) / (total + 2)
                
                # Update average duration
                if duration_ms and avg_duration:
                    avg_duration = (avg_duration + duration_ms) // 2
                elif duration_ms:
                    avg_duration = duration_ms
                    
                cursor.execute("""
                    UPDATE skill_memory 
                    SET success_count = ?, 
                        failure_count = ?,
                        confidence = ?,
                        avg_duration_ms = ?,
                        last_used = CURRENT_TIMESTAMP
                    WHERE skill_name = ?
                """, (success_count, failure_count, confidence, 
                     avg_duration, skill_name))
                     
    def list_skills(self, min_confidence: float = 0.0, 
                   limit: int = 100) -> List[Dict]:
        """List all skills."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM skill_memory 
            WHERE confidence >= ?
            ORDER BY confidence DESC, last_used DESC LIMIT ?
        """, (min_confidence, limit))
        
        skills = []
        for row in cursor.fetchall():
            skill = dict(row)
            if skill['steps']:
                skill['steps'] = json.loads(skill['steps'])
            if skill['prerequisites']:
                skill['prerequisites'] = json.loads(skill['prerequisites'])
            skills.append(skill)
        return skills
        
    # Session Operations
    def create_session(self, session_id: str, context: str = None) -> str:
        """Create a new session."""
        with self.transaction():
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (id, context)
                VALUES (?, ?)
            """, (session_id, context))
            return session_id
            
    def end_session(self, session_id: str, summary: str = None):
        """End a session."""
        with self.transaction():
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE sessions 
                SET end_time = CURRENT_TIMESTAMP,
                    summary = ?
                WHERE id = ?
            """, (summary, session_id))
            
    # Sandbox Operations
    def add_sandbox_experiment(self, experiment_type: str, plan: str,
                              command: str = None, status: str = None,
                              duration_ms: int = None, logs: str = None,
                              errors: str = None, skill_id: int = None) -> int:
        """Record a sandbox experiment."""
        with self.transaction():
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO sandbox_experiments 
                (experiment_type, plan, command, status, duration_ms, 
                 logs, errors, skill_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (experiment_type, plan, command, status, duration_ms,
                 logs, errors, skill_id))
            return cursor.lastrowid
            
    def get_sandbox_experiments(self, skill_id: int = None,
                               limit: int = 100) -> List[Dict]:
        """Retrieve sandbox experiments."""
        cursor = self.conn.cursor()
        if skill_id:
            cursor.execute("""
                SELECT * FROM sandbox_experiments 
                WHERE skill_id = ?
                ORDER BY created_at DESC LIMIT ?
            """, (skill_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM sandbox_experiments 
                ORDER BY created_at DESC LIMIT ?
            """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
        
    # Statistics
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Count records in each table
        cursor.execute("SELECT COUNT(*) as count FROM episodic_memory")
        stats['episodic_count'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM semantic_memory")
        stats['semantic_count'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM skill_memory")
        stats['skill_count'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM sessions")
        stats['session_count'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM sandbox_experiments")
        stats['sandbox_count'] = cursor.fetchone()['count']
        
        # Database size
        stats['db_size_bytes'] = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        
        return stats
