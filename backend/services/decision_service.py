def decide_path(choice: str):

    if not choice:
        return "fast"

    choice = choice.lower()

    if choice in ["fast", "channels", "directory"]:
        return choice

    return "fast"