from typing import List, Dict
from openai import OpenAI
import json

class TestCaseGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def generate_test_cases(self, user_story: str) -> List[Dict]:
        """Convert user story to test cases using OpenAI"""
        prompt = f"""
        Convert this user story into detailed test cases:
        {user_story}
        
        Generate test cases in the following JSON format:
        {{
            "test_cases": [
                {{
                    "title": "Test case title",
                    "description": "Test case description",
                    "preconditions": ["condition1", "condition2"],
                    "steps": ["step1", "step2"],
                    "expected_results": ["result1", "result2"],
                    "priority": "High/Medium/Low"
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            test_cases = json.loads(response.choices[0].message.content)
            return test_cases["test_cases"]
        except Exception as e:
            raise Exception(f"Failed to generate test cases: {str(e)}")