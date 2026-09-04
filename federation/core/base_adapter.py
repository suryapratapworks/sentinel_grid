from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

class BaseAdapter(ABC):
    def __init__(self, adapter_id: str, name: str, vendor: str, config: Optional[Dict[str, Any]] = None):
        self.adapter_id = adapter_id
        self.name = name
        self.vendor = vendor
        self.config = config or {}
        self.status = "ONLINE"
        self.reconnect_count = 0
        self.event_count = 0

    @abstractmethod
    async def connect(self) -> bool:
        """Establish session or stream connection"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect and release resources"""
        pass

    @abstractmethod
    async def discover_devices(self) -> List[Dict[str, Any]]:
        """Discover connected cameras or nodes"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Query connection health and statistics"""
        pass
