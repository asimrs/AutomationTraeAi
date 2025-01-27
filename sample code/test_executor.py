from browser_use import Agent
from langchain_openai import ChatOpenAI
from typing import Dict, List
import logging
import imageio
import os
from datetime import datetime
import asyncio

class TestExecutor:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",  # Changed to GPT-4
            openai_api_key=openai_api_key,
            temperature=0.2  # Reduced temperature for more consistent results
        )
        
    async def execute_test(self, test_case: Dict) -> Dict:
        test_results = {
            "title": test_case["title"],
            "status": "Failed",
            "errors": [],
            "result": None,
            "screenshots": []  # Added screenshots field to prevent KeyError
        }
        
        try:
            agent = Agent(
                task="""
                Navigate to GitHub and search:
                1. Go to https://github.com
                2. Wait for the page to load
                3. Look for the search box at the top
                4. Click the search box
                5. Type 'browser-use'
                6. Press Enter to search
                """,
                llm=self.llm
            )
            
            # Single run attempt with increased wait time
            await asyncio.sleep(5)  # Wait longer for browser to initialize
            result = await agent.run()
            test_results["result"] = str(result)
            test_results["status"] = "Passed"
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Test execution failed: {error_msg}")
            test_results["errors"].append(error_msg)
        finally:
            if 'agent' in locals():
                try:
                    if hasattr(agent, 'browser') and agent.browser:
                        await agent.browser.close()
                except Exception as close_error:
                    logging.error(f"Browser close error: {str(close_error)}")
            
        return test_results

# Simplified test case
async def test_agent():
    test_case = {
        "title": "Simple GitHub Search Test",
        "description": "Basic search functionality test",
        "steps": ["Search for browser-use repository"],
        "expected_results": ["Search results are displayed"]
    }

    executor = TestExecutor()
    result = await executor.execute_test(test_case)
    print(result)

if __name__ == "__main__":
    asyncio.run(test_agent())