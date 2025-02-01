from browser_use import Agent
from langchain_openai import ChatOpenAI
from typing import Dict, List
import logging
from datetime import datetime  # Change this line
import os
import asyncio
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.test_data.user_stories import USER_STORIES
from src.ai_engine.test_case_generator import TestCaseGenerator

class TestExecutor:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4o",  # Changed to vision-capable model
            openai_api_key=openai_api_key,
            temperature=0.1,
            max_tokens=1000
        )
        self.test_results = []
        self.agent = None
        self.MAX_RETRIES = 2
        
    async def execute_test(self, test_case: Dict) -> Dict:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        gif_name = f"{test_case['title'].replace(' ', '_')}_{timestamp}_agent_history.gif"
        gif_path = os.path.join("test_recordings", gif_name)
        
        test_results = {
            "title": test_case["title"],
            "status": "Failed",
            "errors": [],
            "result": None,
            "recording": gif_path,
            "steps_completed": []
        }
        
        try:
            if 'url' not in test_case or not test_case['url']:
                raise Exception("Test case is missing required URL")
                
            task = f"""
            Test Execution Steps:
            1. Open browser and navigate to: {test_case['url']}
            2. Execute the following steps in order:
            {self._format_steps(test_case['steps'])}
            
            Validation Requirements:
            {self._format_expectations(test_case['expected_results'])}
            
            Important Instructions:
            - Execute each step exactly as specified
            - Verify each step completion before moving to next
            - Take screenshots after each significant action
            - Report step completion status
            - Use exact element selectors when available
            - Wait for page loads and elements to be visible
            """
            
            agent = Agent(
                task=task,
                llm=self.llm
            )
            
            logging.info(f"Starting test execution: {test_case['title']}")
            result = await agent.run()
            
            # Verify execution result
            if result and isinstance(result, str):
                if "error" in result.lower() or "failed" in result.lower():
                    test_results["errors"].append(result)
                elif "done" in result.lower() or "success" in result.lower():
                    test_results["status"] = "Passed"
                    test_results["result"] = result
                    test_results["steps_completed"] = [{"step": step, "status": "Passed"} for step in test_case["steps"]]
            
            # Save recording if exists
            if os.path.exists("agent_history.gif"):
                os.rename("agent_history.gif", gif_path)
                logging.info(f"Test recording saved: {gif_path}")
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Test execution failed: {error_msg}")
            test_results["errors"].append(error_msg)
        finally:
            if 'agent' in locals():
                await self._cleanup_browser(agent)
            
        self.test_results.append(test_results)
        return test_results

    async def cleanup(self):
        """Cleanup resources after all tests"""
        if self.agent:
            await self._cleanup_browser(self.agent)

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

    def generate_summary_report(self) -> str:
        """Generate a summary report of all test executions"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"] == "Passed")
        
        report = [
            "\n=== Test Execution Summary ===",
            f"Total Tests: {total_tests}",
            f"Passed: {passed_tests}",
            f"Failed: {total_tests - passed_tests}",
            f"Success Rate: {(passed_tests/total_tests)*100:.2f}%\n",
            "\nDetailed Results:"
        ]
        
        for result in self.test_results:
            report.extend([
                f"\nTest: {result['title']}",
                f"Status: {result['status']}",
                f"Recording: {result.get('recording', 'Not available')}",  # Changed from gif_path to recording
                "Steps Completed:",
                *[f"  - {step['step']} ({step['status']})" for step in result['steps_completed']],
                "Errors:" if result['errors'] else "No Errors",
                *[f"  - {error}" for error in result['errors']]
            ])
        
        return "\n".join(report)

async def test_agent():
    # Load environment variables from specific path
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("OPENAI_API_KEY")
    logging.info(f"Loading .env from: {env_path}")
    logging.info(f"API Key loaded: {'Present' if api_key else 'Missing'}")
    
    if not api_key:
        raise ValueError(f"OPENAI_API_KEY not found in environment variables at {env_path}")
    
    # Initialize both generators
    test_case_generator = TestCaseGenerator(api_key=api_key)
    executor = TestExecutor(openai_api_key=api_key)
    
    all_results = []
    # Process each user story
    for story in USER_STORIES:
        print(f"\n{'='*50}")
        print(f"Processing User Story:\n{story}")
        print(f"{'='*50}")
        
        # Generate test cases from user story
        test_cases = test_case_generator.generate_test_cases(story)
        
        # Display test cases and wait for user confirmation
        print("\nGenerated Test Cases:")
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}:")
            print(f"Title: {test_case['title']}")
            print(f"Description: {test_case['description']}")
            print("Steps:")
            for step in test_case['steps']:
                print(f"  - {step}")
            print("Expected Results:")
            for result in test_case['expected_results']:
                print(f"  - {result}")
        
        # Ask for user confirmation
        response = input("\nAre these test cases correct? (y/n): ").lower().strip()
        if response != 'y':
            print("Test execution terminated by user.")
            return
        
        # Execute each generated test case
        for test_case in test_cases:
            print(f"\nExecuting Test: {test_case['title']}")
            result = await executor.execute_test(test_case)
            all_results.append(result)
            print(f"Results: {result}")
    
    # Generate and print summary report
    print("\n" + executor.generate_summary_report())

if __name__ == "__main__":
    # Create recordings directory if it doesn't exist
    os.makedirs("test_recordings", exist_ok=True)
    asyncio.run(test_agent())