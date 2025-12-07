"""End-to-end tests for AI agent flows using Playwright."""
import pytest
from playwright.async_api import Page, expect


@pytest.fixture
def base_url():
    """Base URL for the application."""
    return "http://localhost:8000"


class TestAgentFlows:
    """E2E tests for agent interaction flows."""

    @pytest.mark.asyncio
    async def test_homepage_loads(self, page: Page, base_url: str):
        """Test that the homepage loads correctly."""
        await page.goto(base_url)
        await expect(page.locator("h1")).to_contain_text("AI Assistant")

    @pytest.mark.asyncio
    async def test_agent_selector_visible(self, page: Page, base_url: str):
        """Test that agent selector is visible."""
        await page.goto(base_url)
        agents_section = page.locator("text=Agents")
        await expect(agents_section).to_be_visible()

    @pytest.mark.asyncio
    async def test_send_message(self, page: Page, base_url: str):
        """Test sending a message to the agent."""
        await page.goto(base_url)

        # Type a message
        input_field = page.locator("textarea")
        await input_field.fill("Hello, can you help me?")

        # Send the message
        send_button = page.locator("button:has(svg)")
        await send_button.last.click()

        # Wait for response
        await page.wait_for_selector(".message-enter", timeout=30000)

        # Verify message appeared
        messages = page.locator(".message-enter")
        count = await messages.count()
        assert count >= 1

    @pytest.mark.asyncio
    async def test_switch_agent(self, page: Page, base_url: str):
        """Test switching between agents."""
        await page.goto(base_url)

        # Click on a different agent if available
        agent_buttons = page.locator("button:has-text('coder')")
        if await agent_buttons.count() > 0:
            await agent_buttons.first.click()

            # Verify agent changed in header
            header = page.locator("header")
            await expect(header).to_contain_text("coder agent")

    @pytest.mark.asyncio
    async def test_clear_chat(self, page: Page, base_url: str):
        """Test clearing the chat history."""
        await page.goto(base_url)

        # Send a message first
        input_field = page.locator("textarea")
        await input_field.fill("Test message")
        send_button = page.locator("button:has(svg)").last
        await send_button.click()

        # Wait for message to appear
        await page.wait_for_timeout(1000)

        # Click clear button
        clear_button = page.locator("[title='Clear chat']")
        await clear_button.click()

        # Verify chat is empty
        empty_state = page.locator("text=Start a conversation")
        await expect(empty_state).to_be_visible()

    @pytest.mark.asyncio
    async def test_settings_modal(self, page: Page, base_url: str):
        """Test opening and closing settings modal."""
        await page.goto(base_url)

        # Open settings
        settings_button = page.locator("text=Settings")
        await settings_button.click()

        # Verify modal opened
        modal = page.locator("text=API Key")
        await expect(modal).to_be_visible()

        # Close modal
        cancel_button = page.locator("button:has-text('Cancel')")
        await cancel_button.click()

        # Verify modal closed
        await expect(modal).not_to_be_visible()

    @pytest.mark.asyncio
    async def test_websocket_connection(self, page: Page, base_url: str):
        """Test WebSocket connection indicator."""
        await page.goto(base_url)

        # Wait for connection
        await page.wait_for_timeout(2000)

        # Check connection indicator
        indicator = page.locator(".bg-green-500, .bg-yellow-500")
        await expect(indicator.first).to_be_visible()

    @pytest.mark.asyncio
    async def test_sidebar_toggle(self, page: Page, base_url: str):
        """Test sidebar toggle functionality."""
        await page.goto(base_url)

        # Get initial sidebar state
        sidebar = page.locator("aside")
        initial_width = await sidebar.evaluate("el => el.offsetWidth")

        # Toggle sidebar
        toggle_button = page.locator("header button").first
        await toggle_button.click()

        await page.wait_for_timeout(500)

        # Verify sidebar collapsed
        new_width = await sidebar.evaluate("el => el.offsetWidth")
        assert new_width != initial_width

    @pytest.mark.asyncio
    async def test_responsive_design(self, page: Page, base_url: str):
        """Test responsive design at different viewports."""
        await page.goto(base_url)

        # Test desktop
        await page.set_viewport_size({"width": 1920, "height": 1080})
        sidebar = page.locator("aside")
        await expect(sidebar).to_be_visible()

        # Test tablet
        await page.set_viewport_size({"width": 768, "height": 1024})
        await page.wait_for_timeout(300)

        # Test mobile
        await page.set_viewport_size({"width": 375, "height": 667})
        await page.wait_for_timeout(300)


class TestAPIEndpoints:
    """E2E tests for API endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, page: Page, base_url: str):
        """Test health check endpoint."""
        response = await page.request.get(f"{base_url}/api/health")
        assert response.ok
        data = await response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_list_agents(self, page: Page, base_url: str):
        """Test listing agents endpoint."""
        response = await page.request.get(f"{base_url}/api/agents")
        assert response.ok
        data = await response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_chat_endpoint(self, page: Page, base_url: str):
        """Test chat endpoint."""
        response = await page.request.post(
            f"{base_url}/api/chat",
            data={
                "message": "Hello",
                "agent": "assistant",
            },
        )
        assert response.ok
        data = await response.json()
        assert "response" in data
        assert "session_id" in data
