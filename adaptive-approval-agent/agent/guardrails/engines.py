def evaluate_condition(actual, operator: str, expected) -> bool:
    if operator == "==":
        return actual == expected
    if operator == "!=":
        return actual != expected
    if operator == ">":
        return actual is not None and actual > expected
    if operator == "<":
        return actual is not None and actual < expected
    if operator == ">=":
        return actual is not None and actual >= expected
    if operator == "<=":
        return actual is not None and actual <= expected
    if operator == "in":
        return actual in expected
    if operator == "not in":
        return actual not in expected
    if operator == "contains":
        return expected in actual
    return False
