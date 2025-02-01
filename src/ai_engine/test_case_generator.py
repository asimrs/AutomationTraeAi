from typing import List, Dict
from openai import OpenAI
import json
import logging

class TestCaseGenerator:
    def __init__(self, api_key: str):
        logging.info("Initializing TestCaseGenerator")
        if not api_key:
            logging.error("API key is empty or None")
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=api_key)
        logging.info("OpenAI client initialized successfully")
        
    def _extract_url(self, user_story: str) -> str:
        """Extract URL from user story"""
        url_line = next((line for line in user_story.split('\n') if 'URL:' in line), None)
        if not url_line:
            raise ValueError("User story must contain a URL specification")
        return url_line.split('URL:')[1].strip()
    
    def generate_test_cases(self, user_story: str) -> List[Dict]:
        """Convert user story to test cases using OpenAI"""
        url = self._extract_url(user_story)
        
        prompt = f"""Generate test cases in this exact JSON format:
        {{
            "test_cases": [
                {{
                    "title": "Login with Valid Credentials",
                    "description": "Verify login with valid credentials",
                    "url": "{url}",
                    "steps": [
                        "Navigate to {url}",
                        "Enter email in email field",
                        "Enter password in password field"
                    ],
                    "expected_results": [
                        "User should be logged in successfully"
                    ]
                }}
            ]
        }}

        User Story: {user_story}
        
        Requirements:
        - Maximum 2 test cases
        - Use exact element IDs
        - Include validation steps
        - Return ONLY valid JSON
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a JSON test case generator. Always return valid JSON matching the exact format provided."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.1,  # Even lower for more consistent output
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            # Remove any markdown formatting if present
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            test_cases = json.loads(content.strip())
            return test_cases.get("test_cases", [])
                
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {str(e)}")
            logging.error(f"Received content: {content}")
            raise Exception("Failed to generate valid JSON test cases")
        except Exception as e:
            logging.error(f"Error generating test cases: {str(e)}")
            raise Exception(f"Failed to generate test cases: {str(e)}")