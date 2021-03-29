from typing import Dict, Any
# dataclasses are only supported on Python >= 3.7


class User:
    def __init__(self, **kwargs):
        vars(self).update(kwargs)
    
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
    
    def __repr__(self) -> str:
        return "User({})".format(
            ",".join(["{}={}".format(*item) for item in vars(self).items()])
        )
