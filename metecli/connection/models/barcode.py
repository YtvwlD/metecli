from typing import Dict, Any
# dataclasses are only supported on Python >= 3.7


class Barcode:
    def __init__(self, **kwargs):
        vars(self).update(kwargs)
    
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
    
    def __repr__(self) -> str:
        return "Barcode({})".format(
            ",".join(["{}={}".format(*item) for item in vars(self).items()])
        )
