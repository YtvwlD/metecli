from typing import Dict, Any
import logging
log = logging.getLogger(__name__)
# dataclasses are only supported on Python >= 3.7


class Drink:
    def __init__(self, **kwargs):
        vars(self).update(kwargs)
    
    @classmethod
    def from_v1(cls, data: Dict[str, Any]) -> 'Drink':
        return cls(
            id=int(data["id"]) if data["id"] is not None else None,
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
    
    @classmethod
    def from_v2(cls, data: Dict[str, Any]) -> 'Drink':
        return cls(
            id=int(data["id"]),
            name=str(data["name"]),
            bottle_size=None,
            caffeine=int(data["caffeine"]) if data["caffeine"] is not None else None,
            price=int(data["price"]) / 100,
            active=bool(data["active"]),
        )
    
    def to_v2(self) -> Dict[str, Any]:
        if self.bottle_size is not None:
            log.warn("This API version does not support bottle_size, ignoring value.")
        return {
            "id": self.id,
            "name": self.name,
            "caffeine": self.caffeine,
            "price": int(self.price * 100),
            "active": self.active,
        }
    
    @classmethod
    def from_v3(cls, data: Dict[str, Any]) -> 'Drink':
        # TODO: perhaps support alcohol, energy and sugar
        return cls.from_v2(data)
    
    def to_v3(self) -> Dict[str, Any]:
        # TODO: perhaps support alcohol, energy and sugar
        return self.to_v2()
    
    def __repr__(self) -> str:
        return "Drink({})".format(
            ",".join(["{}={}".format(*item) for item in vars(self).items()])
        )
