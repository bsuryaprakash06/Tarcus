from typing import Dict, Any
from src.utils.logger import get_logger
from src.utils.settings import DRY_RUN

logger = get_logger("tools.browser")

def launch_browser(kwargs: Dict[str, Any], context: Any) -> str:
    """Launches a new browser instance and sets it as active."""
    url = kwargs.get("url", "about:blank")
    if DRY_RUN:
        return f"[DRY RUN] Launched browser and navigated to {url}"
        
    coordinator = getattr(context, "browser_coordinator", None)
    if not coordinator:
        return "Error: Browser Coordinator not available in context."
        
    try:
        instance = coordinator.launch_and_set_active()
        coordinator.navigate_active_tab(url)
        return f"Successfully launched browser (ID: {instance.id}) and navigated to {url}"
    except Exception as e:
        logger.error(f"Failed to launch browser: {e}")
        return f"Failed to launch browser: {str(e)}"

def navigate_to_url(kwargs: Dict[str, Any], context: Any) -> str:
    """Navigates the active tab to a specific URL."""
    url = kwargs.get("url")
    if not url:
        return "Error: URL is required."
        
    if DRY_RUN:
        return f"[DRY RUN] Navigating to {url}"
        
    coordinator = getattr(context, "browser_coordinator", None)
    if not coordinator:
        return "Error: Browser Coordinator not available."
        
    try:
        success = coordinator.navigate_active_tab(url)
        if success:
            return f"Successfully navigated to {url}"
        else:
            return f"Navigation to {url} failed."
    except Exception as e:
        return f"Error during navigation: {str(e)}"

def create_tab(kwargs: Dict[str, Any], context: Any) -> str:
    """Creates a new tab in the active browser."""
    url = kwargs.get("url", "about:blank")
    if DRY_RUN:
        return f"[DRY RUN] Created new tab with URL: {url}"
        
    coordinator = getattr(context, "browser_coordinator", None)
    if not coordinator:
        return "Error: Browser Coordinator not available."
        
    browser_id = coordinator.resolve_active_browser()
    if not browser_id:
        return "Error: No active browser found."
        
    try:
        tab = coordinator.manager.create_tab(browser_id, url)
        if tab:
            return f"Created new tab (ID: {tab.id}) pointing to {url}"
        return "Failed to create tab."
    except Exception as e:
        return f"Error creating tab: {str(e)}"

def close_tab(kwargs: Dict[str, Any], context: Any) -> str:
    """Closes the currently active tab."""
    if DRY_RUN:
        return "[DRY RUN] Closed active tab."
        
    coordinator = getattr(context, "browser_coordinator", None)
    if not coordinator:
        return "Error: Browser Coordinator not available."
        
    browser_id = coordinator.resolve_active_browser()
    session = coordinator.manager.registry.get_session_for_browser(browser_id) if browser_id else None
    
    if not session or not session.active_tab_id:
        return "Error: No active tab to close."
        
    try:
        coordinator.manager.close_tab(browser_id, session.active_tab_id)
        return "Successfully closed active tab."
    except Exception as e:
        return f"Error closing tab: {str(e)}"

def close_browser(kwargs: Dict[str, Any], context: Any) -> str:
    """Closes the active browser instance."""
    if DRY_RUN:
        return "[DRY RUN] Closed active browser."
        
    coordinator = getattr(context, "browser_coordinator", None)
    if not coordinator:
        return "Error: Browser Coordinator not available."
        
    browser_id = coordinator.resolve_active_browser()
    if not browser_id:
        return "Error: No active browser to close."
        
    try:
        coordinator.manager.close(browser_id)
        # coordinator.active_browser_id = None # Let resolve handle it
        return "Successfully closed browser."
    except Exception as e:
        return f"Error closing browser: {str(e)}"
