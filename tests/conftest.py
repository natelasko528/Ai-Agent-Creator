"""Pytest configuration for E2E tests."""
import pytest
from playwright.async_api import async_playwright


@pytest.fixture(scope="session")
def base_url():
    """Base URL for tests."""
    return "http://localhost:8000"


@pytest.fixture(scope="function")
async def page():
    """Create a new browser page for each test."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        yield page
        await context.close()
        await browser.close()


@pytest.fixture(scope="function")
async def authenticated_page(page):
    """Page with authentication if needed."""
    # Add any authentication logic here
    yield page
