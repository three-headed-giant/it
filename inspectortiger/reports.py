from dataclasses import dataclass
from typing import Optional


@dataclass
class Report:
    code: str
    lineno: int
    filename: str
    annotation: Optional[str] = None
