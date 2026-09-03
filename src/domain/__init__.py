"""Domain layer — pure business logic and port definitions (AD-2).

Published interface: the port Protocols below. Adapters, ``app`` and ``worker``
may import from here; the domain imports nothing from them (enforced by
import-linter, see ``pyproject.toml``).
"""

from src.domain.ports.clock import Clock
from src.domain.ports.config_store import ConfigStore, ConfigVersion
from src.domain.ports.crm import CrmPort
from src.domain.ports.llm import LlmPort
from src.domain.ports.telegram import TelegramPort

__all__ = ["Clock", "ConfigStore", "ConfigVersion", "CrmPort", "LlmPort", "TelegramPort"]
