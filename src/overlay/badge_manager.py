class BadgeManager:
    """
    Manages the assignment of sequential badges (e.g., T1, T2, T3) to interaction targets.
    Numbers are strictly ascending and never reused within a session to prevent user confusion.
    """
    def __init__(self):
        self._counter = 0
        self._target_badges = {}

    def assign_badge(self, target_id: str) -> str:
        """
        Assigns the next available badge to the target. If the target already has one, returns it.
        """
        if target_id in self._target_badges:
            return self._target_badges[target_id]
            
        self._counter += 1
        badge = f"T{self._counter}"
        self._target_badges[target_id] = badge
        return badge
        
    def get_badge(self, target_id: str) -> str:
        return self._target_badges.get(target_id, "")
