from typing import Dict, Any
# dataclasses are only supported on Python >= 3.7


class Drink:
    def __init__(self, **kwargs):
        vars(self).update(kwargs)
    
    @classmethod
    def from_v1(cls, data: Dict[str, Any]) -> 'Drink':
        return cls(
            id=int(data["id"]),
            name=str(data["name"]),
            bottle_size=float(data["bottle_size"]),
            caffeine=int(data["caffeine"]) if data["caffeine"] is not None else None,
            price=float(data["price"]),
            active=bool(data["active"]),
        )
    
    def to_v1(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "bottle_size": self.bottle_size,
            "caffeine": self.caffeine,
            "price": self.price,
            "active": self.active,
        }
    
    def __repr__(self) -> str:
        return "Drink({})".format(
            ",".join(["{}={}".format(*item) for item in vars(self).items()])
        )
