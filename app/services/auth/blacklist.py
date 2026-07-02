# Simple in-memory blacklist (upgrade to Redis later)
BLACKLISTED_TOKENS = set()


def add_token_to_blacklist(token: str):
    BLACKLISTED_TOKENS.add(token)


def is_token_blacklisted(token: str) -> bool:
    return token in BLACKLISTED_TOKENS