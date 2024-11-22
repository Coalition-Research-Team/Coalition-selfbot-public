import base64

def userid_from_token(token: str) -> str:
    """
    Extracts the user ID from a Discord token.
    """
    token = token.split(".")[0]
    token += "=" * ((4 - len(token) % 4) % 4)
    return base64.b64decode(token).decode("utf-8")

def escape_mentions(content: str) -> str:
    """Escape @everyone and @here mentions."""
    return content.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
