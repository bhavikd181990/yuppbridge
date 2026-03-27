import logging
try:
    import browser_cookie3
except ImportError:
    browser_cookie3 = None

from . import config, constants, auth

logger = logging.getLogger("yuppbridge.session_extractor")

def extract_yupp_token():
    """Extract session token from local browsers."""
    if not browser_cookie3:
        logger.error("browser-cookie3 is not installed.")
        return None
        
    try:
        # Load cookies from all supported browsers for yupp.ai
        cj = browser_cookie3.load(domain_name="yupp.ai")
        
        # Look for the session cookie
        for cookie in cj:
            if cookie.name == constants.SESSION_TOKEN_COOKIE:
                return cookie.value
                
    except Exception as e:
        logger.error(f"Failed to extract browser cookie: {e}")
        
    return None

async def attempt_auto_update():
    """Try to update the token and reload accounts if a new token is found."""
    logger.info("Attempting to auto-update session token from local browsers...")
    
    new_token = extract_yupp_token()
    if not new_token:
        logger.warning("No session token found in local browsers. Make sure you are logged into yupp.ai.")
        return False
        
    cfg = config.get_config()
    current_tokens = config.get_auth_tokens(cfg)
    
    if new_token in current_tokens:
        logger.info("Extracted token is identical to the current one. It might still be valid or the browser token is also expired.")
        # Re-enable the account if it was marked invalid, maybe it just hit a temporary block
        return False
        
    logger.info("Successfully extracted a new session token! Updating config...")
    
    # Update config.json
    cfg['auth_tokens'] = [new_token]
    config.save_config(cfg)
    
    # Reload accounts dynamically
    await auth.load_yupp_accounts(new_token)
    
    logger.info("Token updated and accounts reloaded.")
    return True
