from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class Audit:
    id: int
    created_at: str
    difference: float
    drink: Optional[int]
    
    @classmethod
    def from_v1(cls, data: Dict[str, Any]) -> 'Audit':
        return cls(
            id=int(data["id"]),
            # TODO: turn this into datetime?
            created_at=str(data["created_at"]),
            difference=float(data["difference"]),
            drink=int(data["drink"]) if data["drink"] is not None else None,
        )


@dataclass
class AuditInfo:
    sum: float
    payments_sum: float
    deposits_sum: float
    audits: List[Audit]
    
    @classmethod
    def from_v1(cls, data: Dict[str, Any]) -> 'AuditInfo':
        return cls(
            sum=float(data["sum"]),
            payments_sum=float(data["payments_sum"]),
            deposits_sum=float(data["deposits_sum"]),
            audits=[Audit.from_v1(a) for a in data["audits"]],
        )
