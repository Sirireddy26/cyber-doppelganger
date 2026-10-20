"""
Cyber Doppelgänger - Desktop Agent Configuration Module
Re-exports settings from agent.configuration.settings for backwards compatibility.
"""

from agent.configuration.settings import AgentSettings, settings

__all__ = ["AgentSettings", "settings"]
