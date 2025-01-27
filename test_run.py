import asyncio
from src.ai_engine.test_case_generator import TestCaseGenerator
from src.test_engine.test_executor import TestExecutor
import os
from dotenv import load_dotenv

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize components
    test_generator = TestCaseGenerator(api_key=os.getenv('OPENAI_API_KEY'))
    test_executor = TestExecutor(openai_api_key=os.getenv('OPENAI_API_KEY'))
    
    # Example user story
    user_story = """
    As a user, I want to search for 'browser-use' on GitHub,
    so that I can find its repository.
    """
    
    # Generate test cases
    test_cases = test_generator.generate_test_cases(user_story)
    
    # Execute first test case
    if test_cases:
        result = await test_executor.execute_test(test_cases[0])
        print("\nTest Execution Results:")
        print(f"Title: {result['title']}")
        print(f"Status: {result['status']}")
        print(f"Screenshots: {result['screenshots']}")
        if result.get('gif_log'):
            print(f"GIF Log: {result['gif_log']}")
        if result['errors']:
            print(f"Errors: {result['errors']}")

if __name__ == "__main__":
    asyncio.run(main())