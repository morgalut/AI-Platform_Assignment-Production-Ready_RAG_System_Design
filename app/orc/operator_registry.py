# app/orc/operator_registry.py

class OperatorRegistry:
    def __init__(self):
        self._operators = {}

    def register(self, name: str, operator):
        if name in self._operators:
            raise ValueError(f"Operator '{name}' already registered")
        self._operators[name] = operator

    def get(self, name: str):
        return self._operators.get(name)

    def names(self):
        return list(self._operators.keys())
