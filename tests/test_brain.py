"""
Basic tests for Brain functionality.
"""
import os
import tempfile
import unittest
from cortex.core.brain import Brain


class TestBrain(unittest.TestCase):
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.brain = Brain(self.temp_db.name)
        
    def tearDown(self):
        """Clean up test database."""
        self.brain.close()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)
            
    def test_session_management(self):
        """Test session creation and ending."""
        session_id = self.brain.start_session("test context")
        self.assertIsNotNone(session_id)
        self.brain.end_session("test summary")
        
    def test_observe_event(self):
        """Test event observation."""
        session_id = self.brain.start_session()
        self.brain.observe(
            event_type="command",
            command="ls -la",
            result="success",
            duration_ms=100
        )
        # No exception means success
        self.brain.end_session()
        
    def test_learn_fact(self):
        """Test learning a fact."""
        fact_id = self.brain.learn_fact(
            topic="python",
            fact="Python is a programming language",
            confidence=0.9,
            source_type="system"
        )
        self.assertIsNotNone(fact_id)
        self.assertGreater(fact_id, 0)
        
    def test_recall_facts(self):
        """Test recalling facts."""
        self.brain.learn_fact(
            topic="python",
            fact="Python uses indentation",
            confidence=0.8
        )
        
        facts = self.brain.recall_facts(topic="python")
        self.assertGreater(len(facts), 0)
        
    def test_learn_skill(self):
        """Test learning a skill."""
        skill_id = self.brain.learn_skill(
            skill_name="deploy_app",
            description="Deploy application to server",
            steps=["npm run build", "npm run deploy"],
            confidence=0.7
        )
        self.assertIsNotNone(skill_id)
        
    def test_recall_skill(self):
        """Test recalling a skill."""
        self.brain.learn_skill(
            skill_name="test_skill",
            description="Test skill",
            steps=["step1", "step2"]
        )
        
        skill = self.brain.recall_skill("test_skill")
        self.assertIsNotNone(skill)
        self.assertEqual(skill['skill_name'], "test_skill")
        self.assertEqual(len(skill['steps']), 2)
        
    def test_reinforce_skill(self):
        """Test skill reinforcement."""
        self.brain.learn_skill(
            skill_name="build_project",
            confidence=0.5
        )
        
        # Reinforce with success
        self.brain.reinforce_skill("build_project", success=True, duration_ms=5000)
        
        skill = self.brain.recall_skill("build_project")
        self.assertGreater(skill['confidence'], 0.5)
        self.assertEqual(skill['success_count'], 1)
        
    def test_list_skills(self):
        """Test listing skills."""
        self.brain.learn_skill("skill1", confidence=0.8)
        self.brain.learn_skill("skill2", confidence=0.6)
        
        skills = self.brain.list_skills(min_confidence=0.5)
        self.assertGreaterEqual(len(skills), 2)
        
    def test_get_stats(self):
        """Test getting statistics."""
        stats = self.brain.get_stats()
        self.assertIn('episodic_count', stats)
        self.assertIn('semantic_count', stats)
        self.assertIn('skill_count', stats)


if __name__ == '__main__':
    unittest.main()
