from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Barcode:
    id: str
    drink: Optional[int]
    
    @classmethod
    def from_v1(cls, data: Dict[str, Any]) -> 'Barcode':
        return cls(
            id=str(data["id"]),
            drink=int(data["drink"]) if data["drink"] is not None else None,
        )
    
    def to_v1(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "drink": self.drink,
        }
