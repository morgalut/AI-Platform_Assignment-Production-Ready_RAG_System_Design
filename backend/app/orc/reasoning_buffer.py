# app/orc/reasoning_buffer.py

class ReasoningBuffer:
    """
    Internal reasoning buffer for ReAct-style agent loops.
    This is NEVER returned to the user.
    """

    def __init__(self):
        self.steps = []

    def add(self, text: str):
        self.steps.append(text)

    def get_trace(self):
        return list(self.steps)
