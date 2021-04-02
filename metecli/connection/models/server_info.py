from typing import Dict, Any
# dataclasses are only supported on Python >= 3.7


class ServerInfo:
    def __init__(self, **kwargs):
        vars(self).update(kwargs)
    
    # from_v1: not supported
    
    @classmethod
    def from_v2(cls, data: Dict[str, Any]) -> 'ServerInfo':
        log.warn("This server does not let us know of its defaults. Using our own.")
        return cls(
            version=None, global_credit_limit=None,
            currency="€", currency_before=False, decimal_seperator=",",
            energy="kcal", defaults=Default.from_v2(),
        )
    
    @classmethod
    def from_v3(cls, data: Dict[str, Any]) -> 'ServerInfo':
        return cls(
            version=str(data["version"]),
            global_credit_limit=int(data["global_credit_limit"]) if data["global_credit_limit"] not in (False, None) else None,
            currency=str(data["currency"]),
            currency_before=bool(data["currency_before"]),
            decimal_seperator=str(data["decimal_seperator"]) if data["decimal_seperator"] is not None else None,
            energy=str(data["energy"]),
            defaults=Defaults.from_v3(data["defaults"]),
        )
    
    def __repr__(self) -> str:
        return "ServerInfo({})".format(
            ",".join(["{}={}".format(*item) for item in vars(self).items()])
        )


class Defaults:
    def __init__(self, **kwargs):
        vars(self).update(kwargs)
    
    # from_v1: not supported
    
    @classmethod
    def from_v2(cls, data: Dict[str, Any]) -> 'Defaults':
        return cls(price=1.5, package_size=None, caffeine=None, active=True)
    
    @classmethod
    def from_v3(cls, data: Dict[str, Any]) -> 'Defaults':
        return cls(
            price=int(data["price"]) / 100,
            package_size=str(data["package_size"]),
            caffeine=int(data["currency"]),
            # TODO: alcohol, energy, sugar
            active=bool(data["active"]),
        )
    
    def __repr__(self) -> str:
        return "Defaults({})".format(
            ",".join(["{}={}".format(*item) for item in vars(self).items()])
        )

