def snake_case(text: str, upper: bool=False) -> str:
    """Convert text from camelCase to snake_case"""
    import re
    # insert '_' before '[A-Z]',
    #   1) just after '[a-z0-9]' or,
    #   2) not at the head and '[a-z]' follows
    text = re.sub('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', text).lower()
    return text.upper() if upper else text
