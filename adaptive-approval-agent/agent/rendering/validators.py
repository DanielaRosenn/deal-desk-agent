def validate_adaptive_card(card: dict) -> None:
    if not isinstance(card, dict):
        raise ValueError("Adaptive card must be an object")
    if card.get("type") != "AdaptiveCard":
        raise ValueError("Adaptive card missing type=AdaptiveCard")
    if "body" not in card or not isinstance(card["body"], list):
        raise ValueError("Adaptive card must include a body list")
