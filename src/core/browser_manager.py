from playwright.sync_api import sync_playwright
from typing import Optional
import logging

class BrowserManager:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        
    def start_browser(self, headless: bool = True):
        """Initialize browser session"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=headless)
            self.context = self.browser.new_context(record_video_dir="recordings/")
            self.page = self.context.new_page()
            return True
        except Exception as e:
            logging.error(f"Failed to start browser: {str(e)}")
            return False
            
    def navigate_to(self, url: str) -> bool:
        """Navigate to specified URL"""
        try:
            self.page.goto(url)
            return True
        except Exception as e:
            logging.error(f"Navigation failed: {str(e)}")
            return False
            
    def close_browser(self):
        """Clean up browser resources"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()