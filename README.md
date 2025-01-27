# Automation3Trae (A3T)

An AI-powered web testing framework that leverages OpenAI's GPT models for autonomous web testing.

## Overview

A3T combines natural language processing with browser automation to create a powerful, maintenance-free testing solution. It converts user stories into executable test cases and performs web interactions without requiring predefined selectors or scripts.

## Key Features

- 🤖 AI-Powered Test Generation
- 🌐 Autonomous Web Navigation
- 📸 Automatic Screenshot Capture
- 🎥 Test Execution Recording
- 📝 Natural Language Test Cases
- 🔄 Step-by-Step Execution Tracking

## Installation

1. Clone the repository:
```bash
git clone https://github.com/asimrs/AutomationTraeAi.git
cd AutomationTraeAi


2. Install dependencies:
pip install -r requirements.txt
```

3. Set up environment variables:
cp .env.example .env

## Usage Examples
### Generate Test Cases from User Story

from ai_engine.test_case_generator import TestCaseGenerator

user_story = """
As a GitHub user
I want to search for repositories
So that I can find relevant projects
"""

generator = TestCaseGenerator(api_key="your_api_key")
test_cases = generator.generate_test_cases(user_story)

### Execute Test Cases
from test_engine.test_executor import TestExecutor
import asyncio

async def run_test():
    test_case = {
        "title": "GitHub Search Test",
        "description": "Verify GitHub search functionality",
        "steps": [
            "Navigate to GitHub homepage",
            "Search for 'browser-use' repository",
            "Verify search results"
        ],
        "expected_results": [
            "Search results displayed",
            "'browser-use' repository found"
        ]
    }

    executor = TestExecutor(openai_api_key="your_api_key")
    result = await executor.execute_test(test_case)
    print(result)

asyncio.run(run_test())


#Test Case Format

{
    "title": "Test case title",
    "description": "Test case description",
    "steps": [
        "Step 1 description",
        "Step 2 description"
    ],
    "expected_results": [
        "Expected result 1",
        "Expected result 2"
    ]
}


## Dependencies
- Python 3.8+
- OpenAI API key
- Chrome/Chromium browser
- Required Python packages:
  - langchain-openai>=0.0.3
  - browser-use>=0.1.0
  - openai>=1.3.0
  - python-dotenv>=1.0.0
  - imageio>=2.31.5