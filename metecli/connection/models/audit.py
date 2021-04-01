from typing import Dict, Any
# dataclasses are only supported on Python >= 3.7


class Audit:
    def __init__(self, **kwargs):
        vars(self).update(kwargs)
    
    @classmethod
    def from_v1(cls, data: Dict[str, Any]) -> 'Audit':
        return cls(
            id=int(data["id"]),
            # TODO: turn this into datetime?
            created_at=str(data["created_at"]),
            difference=float(data["difference"]),
            drink=int(data["drink"]) if data["drink"] is not None else None,
        )
    
    @classmethod
    def from_v2(cls, data: Dict[str, Any]) -> 'Audit':
        return cls(
            id=int(data["id"]),
            # TODO: turn this into datetime?
            created_at=str(data["created_at"]),
            difference=int(data["difference"]) / 100,
            drink=int(data["product"]) if data["product"] is not None else None,
        )
    
    @classmethod
    def from_v3(cls, data: Dict[str, Any]) -> 'Audit':
        return cls.from_v2(data)
    
    def __repr__(self) -> str:
        return "Audit({})".format(
            ",".join(["{}={}".format(*item) for item in vars(self).items()])
        )


class AuditInfo:
    def __init__(self, **kwargs):
        vars(self).update(kwargs)
    
    @classmethod
    def from_v1(cls, data: Dict[str, Any]) -> 'AuditInfo':
        return cls(
            sum=float(data["sum"]),
            payments_sum=float(data["payments_sum"]),
            deposits_sum=float(data["deposits_sum"]),
            audits=[Audit.from_v1(a) for a in data["audits"]],
        )
    
    @classmethod
    def from_v2(cls, data: Dict[str, Any]) -> 'AuditInfo':
        return cls(
            sum=int(data["sum"]) / 100,
            payments_sum=int(data["payments_sum"]) / 100,
            deposits_sum=int(data["deposits_sum"]) / 100,
            audits=[Audit.from_v2(a) for a in data["audits"]],
        )
    
    @classmethod
    def from_v3(cls, data: Dict[str, Any]) -> 'AuditInfo':
        return cls.from_v2(data)
    
    def __repr__(self) -> str:
        return "AuditInfo({})".format(
            ",".join(["{}={}".format(*item) for item in vars(self).items()])
        )
