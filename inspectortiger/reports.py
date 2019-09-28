from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Report:
    code: str
    lineno: int
    filename: str
