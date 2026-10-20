"""
Cyber Doppelgänger - Collectors Package
"""

from agent.collectors.base import BaseCollector
from agent.collectors.keyboard.keyboard_collector import KeyboardCollector
from agent.collectors.mouse.mouse_collector import MouseCollector
from agent.collectors.application.application_collector import ApplicationCollector
from agent.collectors.session.session_collector import SessionCollector

__all__ = [
    "BaseCollector",
    "KeyboardCollector",
    "MouseCollector",
    "ApplicationCollector",
    "SessionCollector"
]
