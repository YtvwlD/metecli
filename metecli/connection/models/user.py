from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class User:
    id: int
    name: str
    email: Optional[str]
    balance: float
    active: bool
    audit: bool
    redirect: bool
    
    @classmethod
    def from_v1(cls, data: Dict[str, Any]) -> 'User':
        return cls(
            id=int(data["id"]),
            name=str(data["name"]),
            email=str(data["email"]) if data["email"] is not None else None,
            balance=float(data["balance"]),
            active=bool(data["active"]),
            audit=bool(data["audit"]),
            redirect=bool(data["redirect"]),
        )
    
    def to_v1(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "balance": self.balance,
            "active": self.active,
            "audit": self.audit,
            "redirect": self.redirect,
        }
