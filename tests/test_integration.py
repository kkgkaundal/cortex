"""
Integration tests for Cortex system.
"""
import os
import tempfile
import unittest
from cortex.core.brain import Brain
from cortex.learning.engine import LearningEngine
from cortex.sandbox.runner import Sandbox


class TestIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.brain = Brain(self.temp_db.name)
        self.learning_engine = LearningEngine(self.brain)
        self.sandbox = Sandbox(timeout=5)
        
    def tearDown(self):
        """Clean up test environment."""
        self.brain.close()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)
            
    def test_full_learning_pipeline(self):
        """Test complete learning pipeline."""
        # 1. Start session
        session_id = self.brain.start_session("test learning pipeline")
        self.assertIsNotNone(session_id)
        
        # 2. Observe commands
        commands = ["echo hello", "echo world", "echo test"]
        for cmd in commands:
            self.learning_engine.observe_command(cmd, True, duration_ms=10)
            
        # 3. Get insights
        insights = self.learning_engine.get_insights()
        self.assertGreater(len(insights), 0)
        
        # 4. End session
        self.brain.end_session("learned from commands")
        
    def test_sandbox_with_learning(self):
        """Test sandbox execution integrated with learning."""
        # Execute in sandbox
        result = self.sandbox.run("echo 'sandbox test'")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.return_code, 0)
        
        # Record in brain
        self.brain.observe(
            event_type='sandbox_execution',
            command="echo 'sandbox test'",
            result='success' if result.return_code == 0 else 'failure',
            duration_ms=result.duration_ms
        )
        
        # Verify stored
        stats = self.brain.get_stats()
        self.assertEqual(stats['episodic_count'], 1)
        
    def test_skill_learning_and_reinforcement(self):
        """Test skill learning and improvement through reinforcement."""
        # Learn a skill
        skill_id = self.brain.learn_skill(
            skill_name="test_workflow",
            description="Test workflow",
            steps=["step1", "step2", "step3"],
            confidence=0.5
        )
        
        # Execute and reinforce multiple times
        for i in range(5):
            success = i < 4  # 4 successes, 1 failure
            self.brain.reinforce_skill("test_workflow", success=success, duration_ms=100)
            
        # Check improved confidence
        skill = self.brain.recall_skill("test_workflow")
        self.assertGreater(skill['confidence'], 0.5)
        self.assertEqual(skill['success_count'], 4)
        self.assertEqual(skill['failure_count'], 1)
        
    def test_pattern_detection_integration(self):
        """Test pattern detection in command sequences."""
        # Observe repeated pattern
        pattern = ["git add .", "git commit -m 'update'", "git push"]
        
        for _ in range(3):  # Repeat 3 times
            for cmd in pattern:
                self.learning_engine.observe_command(cmd, True, 100)
                
        # Check if pattern detected
        insights = self.learning_engine.get_insights()
        
        # Should have insights about the pattern
        self.assertGreater(len(insights), 0)
        
    def test_fact_storage_and_recall(self):
        """Test storing and recalling facts."""
        # Store multiple facts
        topics = ["python", "javascript", "deployment"]
        for topic in topics:
            self.brain.learn_fact(
                topic=topic,
                fact=f"This is a fact about {topic}",
                confidence=0.8,
                source_type="test"
            )
            
        # Recall facts
        for topic in topics:
            facts = self.brain.recall_facts(topic=topic)
            self.assertEqual(len(facts), 1)
            self.assertIn(topic, facts[0]['fact'])
            
    def test_session_tracking(self):
        """Test session creation and tracking."""
        # Create multiple sessions
        sessions = []
        for i in range(3):
            session_id = self.brain.start_session(f"test session {i}")
            sessions.append(session_id)
            
            # Add events to each session
            self.brain.observe(
                event_type="test_event",
                command=f"test command {i}",
                result="success"
            )
            
            self.brain.end_session(f"summary {i}")
            
        # Verify sessions exist
        stats = self.brain.get_stats()
        self.assertEqual(stats['session_count'], 3)
        self.assertEqual(stats['episodic_count'], 3)


if __name__ == '__main__':
    unittest.main()
