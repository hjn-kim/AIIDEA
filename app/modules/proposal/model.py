import dataclasses
from typing import Dict


@dataclasses.dataclass
class Proposal:
    title: str = ""
    date: str = ""
    from_company: str = ""
    to_company: str = ""
    template_name: str = "일반 제안서"
    sections: Dict[str, str] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
