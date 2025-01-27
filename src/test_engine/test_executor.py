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
            model="gpt-4o",
            openai_api_key=openai_api_key,
            temperature=0.2
        )
        
    async def execute_test(self, test_case: Dict) -> Dict:
        test_results = {
            "title": test_case["title"],
            "status": "Failed",
            "errors": [],
            "result": None,
            "screenshots": [],
            "steps_completed": []
        }
        
        try:
            task_description = self._create_task_description(test_case)
            agent = Agent(
                task=task_description,
                llm=self.llm
            )
            
            # Execute each step separately
            for step in test_case["steps"]:
                try:
                    logging.info(f"Executing step: {step}")
                    result = await agent.run()
                    test_results["steps_completed"].append({
                        "step": step,
                        "status": "Passed",
                        "result": str(result)
                    })
                except Exception as step_error:
                    error_msg = f"Step '{step}' failed: {str(step_error)}"
                    logging.error(error_msg)
                    test_results["errors"].append(error_msg)
                    test_results["steps_completed"].append({
                        "step": step,
                        "status": "Failed",
                        "error": str(step_error)
                    })
                    break
            
            # Mark test as passed if all steps completed without errors
            if not test_results["errors"]:
                test_results["status"] = "Passed"
                test_results["result"] = "All steps completed successfully"
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Test execution failed: {error_msg}")
            test_results["errors"].append(error_msg)
        finally:
            if 'agent' in locals():
                await self._cleanup_browser(agent)
            
        return test_results

    def _create_task_description(self, test_case: Dict) -> str:
        """Create detailed task description for the agent"""
        return f"""
        Execute this test scenario carefully and precisely:
        
        Test Objective: {test_case['description']}
        
        Required Steps:
        {self._format_steps(test_case['steps'])}
        
        Success Criteria:
        {self._format_expectations(test_case['expected_results'])}
        
        Additional Instructions:
        - Verify each step before proceeding to the next
        - Report any errors or unexpected behavior
        - Ensure all actions are completed successfully
        """

    def _format_steps(self, steps: List[str]) -> str:
        """Format steps with numbers and details"""
        formatted_steps = []
        for i, step in enumerate(steps, 1):
            formatted_steps.append(f"{i}. {step}")
        return "\n".join(formatted_steps)

    def _format_expectations(self, expectations: List[str]) -> str:
        """Format expected results with bullet points"""
        return "\n".join([f"• {exp}" for exp in expectations])

    async def _cleanup_browser(self, agent) -> None:
        """Safely cleanup browser resources"""
        try:
            if hasattr(agent, 'browser') and agent.browser:
                await agent.browser.close()
        except Exception as close_error:
            logging.error(f"Browser cleanup failed: {str(close_error)}")

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