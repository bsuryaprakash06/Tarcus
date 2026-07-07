from abc import ABC, abstractmethod
from typing import List
from src.models.target import InteractionTarget, TargetCapability

class CapabilityProvider(ABC):
    """
    Interface for backends to analyze targets and discover their capabilities and controls.
    """
    @abstractmethod
    def analyze(self, target: InteractionTarget) -> List[TargetCapability]:
        """Analyzes a target and returns the capabilities it supports."""
        pass
        
    @abstractmethod
    def discover(self, target: InteractionTarget):
        """Discovers standard controls (like primary edit fields) for a target."""
        pass
        
    @abstractmethod
    def refresh(self, target: InteractionTarget):
        """Refreshes the capability and control cache for a target."""
        pass
