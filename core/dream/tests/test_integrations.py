from core.dream.integrations import AIIntegration

from django.test import TestCase

class TestAIIntegration(TestCase):
    def test_generate_dream_steps_success(self):
        # Setup a simple integration test
        integration = AIIntegration()
        
        # Call the method we want to test
        steps = integration.generate_dream_steps("Накопить на mustang 2.3 ecoboost цена 3кк")
        
        # Basic verification - just make sure it executes without errors
        self.assertIsNotNone(steps)
        print(f"Generated steps: {steps}")  # Print output for manual inspection
