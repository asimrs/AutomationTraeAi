from typing import List, Dict
from openai import OpenAI
import json

class TestCaseGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def generate_test_cases(self, user_story: str) -> List[Dict]:
        """Convert user story to test cases using OpenAI"""
        prompt = f"""Please convert this user story into test cases and return ONLY a valid JSON object in the following format:
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

User Story:
{user_story}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a test case generator. Always respond with valid JSON only."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            test_cases = json.loads(content)
            return test_cases.get("test_cases", [])
                
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {str(e)}")
            logging.error(f"Received content: {content}")
            raise Exception("Failed to generate valid JSON test cases")
        except Exception as e:
            logging.error(f"Error generating test cases: {str(e)}")
            raise Exception(f"Failed to generate test cases: {str(e)}")