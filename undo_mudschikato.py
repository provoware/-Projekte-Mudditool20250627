"""
undo_mudschikato.py
-------------------
Einfacher Undo-Manager für Mudschikato.
Merkt die letzten n Aktionen (default: 5) und macht sie rückgängig.
Robust und laientauglich.
"""

from typing import Callable, Any, List

class UndoAction:
    """
    Kapselt eine Aktion mit ihrem Undo-Callback und optionalen Metadaten.
    """
    def __init__(self, undo_func: Callable, description: str = "", meta: Any = None):
        self.undo_func = undo_func
        self.description = description
        self.meta = meta

    def undo(self):
        if callable(self.undo_func):
            self.undo_func()

class UndoManager:
    """
    Undo-Manager speichert die letzten n Aktionen als UndoAction-Objekte.
    """
    def __init__(self, limit: int = 5):
        self.stack: List[UndoAction] = []
        self.limit = limit

    def add(self, action: UndoAction):
        self.stack.append(action)
        if len(self.stack) > self.limit:
            self.stack.pop(0)

    def undo(self):
        if self.stack:
            last_action = self.stack.pop()
            last_action.undo()
            return last_action.description
        else:
            return "Nichts rückgängig zu machen!"

    def clear(self):
        self.stack.clear()

# Beispiel für den Standalone-Test
if __name__ == "__main__":
    def test_func():
        print("Letzte Aktion wurde rückgängig gemacht!")

    um = UndoManager()
    um.add(UndoAction(test_func, description="Testaktion 1"))
    um.add(UndoAction(test_func, description="Testaktion 2"))
    print(um.undo())  # Gibt "Testaktion 2"
    print(um.undo())  # Gibt "Testaktion 1"
    print(um.undo())  # Gibt "Nichts rückgängig zu machen!"
