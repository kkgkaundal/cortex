"""
Brain Core - Central intelligence for Cortex.
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from cortex.memory.database import MemoryDatabase
from cortex.learning.background import BackgroundLearner


class Brain:
    """Central intelligence that coordinates memory, learning, and reasoning."""
    
    def __init__(self, db_path: str = "cortex.db", enable_background_learning: bool = True):
        """Initialize the brain.
        
        Args:
            db_path: Path to the memory database
            enable_background_learning: Whether to start background learning system
        """
        self.db = MemoryDatabase(db_path)
        self.db.connect()
        self.current_session_id = None
        
        # Initialize background learning system
        self.background_learner: Optional[BackgroundLearner] = None
        if enable_background_learning:
            self.background_learner = BackgroundLearner(
                db_path=db_path,
                batch_size=10,
                cycle_time=2.0  # Process every 2 seconds
            )
            self.background_learner.start()
        
    def start_session(self, context: str = None) -> str:
        """Start a new learning session.
        
        Args:
            context: Optional context for the session
            
        Returns:
            session_id: Unique identifier for the session
        """
        self.current_session_id = str(uuid.uuid4())
        self.db.create_session(self.current_session_id, context)
        return self.current_session_id
        
    def end_session(self, summary: str = None):
        """End the current session."""
        if self.current_session_id:
            self.db.end_session(self.current_session_id, summary)
            self.current_session_id = None
            
    def observe(self, event_type: str, command: str = None, 
               result: str = None, duration_ms: int = None, 
               context: str = None):
        """Observe and record an event.
        
        Args:
            event_type: Type of event (e.g., 'command', 'file_change')
            command: Command executed (if applicable)
            result: Result of the event
            duration_ms: Duration in milliseconds
            context: Additional context
        """
        self.db.add_episodic_memory(
            event_type=event_type,
            command=command,
            result=result,
            duration_ms=duration_ms,
            context=context,
            session_id=self.current_session_id
        )
        
    def learn_fact(self, topic: str, fact: str, confidence: float = 0.5,
                  source: str = None, source_type: str = None,
                  reliability: float = 0.5) -> int:
        """Learn a new fact.
        
        Args:
            topic: Topic of the fact
            fact: The fact itself
            confidence: Confidence in this fact (0.0 to 1.0)
            source: Source of the fact
            source_type: Type of source ('system', 'internet', 'document', 'sandbox')
            reliability: Reliability of the source (0.0 to 1.0)
            
        Returns:
            memory_id: ID of the stored fact
        """
        memory_id = self.db.add_semantic_memory(
            topic=topic,
            fact=fact,
            confidence=confidence,
            source=source,
            source_type=source_type,
            reliability=reliability
        )
        
        # Add topic to background learning queue for continuous improvement
        if self.background_learner and confidence < 0.9:
            priority = 8 if confidence < 0.6 else 6
            self.background_learner.add_topic(topic, priority=priority)
        
        return memory_id
        
    def learn_skill(self, skill_name: str, description: str = None,
                   steps: List[str] = None, prerequisites: List[str] = None,
                   confidence: float = 0.5) -> int:
        """Learn a new skill.
        
        Args:
            skill_name: Name of the skill
            description: Description of what the skill does
            steps: List of steps to perform the skill
            prerequisites: List of prerequisites
            confidence: Initial confidence (0.0 to 1.0)
            
        Returns:
            skill_id: ID of the stored skill
        """
        return self.db.add_skill(
            skill_name=skill_name,
            description=description,
            steps=steps,
            prerequisites=prerequisites,
            confidence=confidence
        )
        
    def recall_skill(self, skill_name: str) -> Optional[Dict]:
        """Recall a skill from memory.
        
        Args:
            skill_name: Name of the skill to recall
            
        Returns:
            Skill details or None if not found
        """
        return self.db.get_skill(skill_name)
        
    def recall_facts(self, topic: str = None, 
                    min_confidence: float = 0.0) -> List[Dict]:
        """Recall facts from memory.
        
        Args:
            topic: Optional topic filter
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of facts
        """
        return self.db.get_semantic_memories(
            topic=topic,
            min_confidence=min_confidence
        )
        
    def reinforce_skill(self, skill_name: str, success: bool, 
                       duration_ms: int = None):
        """Reinforce a skill based on execution results.
        
        Args:
            skill_name: Name of the skill
            success: Whether the execution was successful
            duration_ms: Duration of execution
        """
        self.db.update_skill_stats(skill_name, success, duration_ms)
        
    def list_skills(self, min_confidence: float = 0.0) -> List[Dict]:
        """List all learned skills.
        
        Args:
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of skills
        """
        return self.db.list_skills(min_confidence=min_confidence)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get brain statistics.
        
        Returns:
            Dictionary of statistics
        """
        stats = self.db.get_memory_stats()
        
        # Add background learning stats if available
        if self.background_learner:
            stats['background_learning'] = self.background_learner.get_status()
        
        return stats
    
    def get_background_learning_status(self) -> Optional[Dict[str, Any]]:
        """Get status of background learning system.
        
        Returns:
            Status dictionary or None if not enabled
        """
        if self.background_learner:
            return self.background_learner.get_status()
        return None
    
    def list_learning_topics(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List topics currently being learned in background.
        
        Args:
            limit: Maximum topics to return
            
        Returns:
            List of topic statuses
        """
        if self.background_learner:
            return self.background_learner.list_active_topics(limit=limit)
        return []
    
    def boost_topic_priority(self, topic: str):
        """Boost priority of a topic (e.g., user just asked about it).
        
        Args:
            topic: Topic to boost
        """
        if self.background_learner:
            self.background_learner.update_priority(topic, priority=9)
        
    def close(self):
        """Close the brain and database connection."""
        # Stop background learning
        if self.background_learner:
            self.background_learner.save_state()
            self.background_learner.stop()
        
        self.db.close()
