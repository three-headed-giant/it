import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Report:
    code: str
    lineno: int
    filename: str


def prepare(all_reports, levels):
    result = {}
    for level, reports in all_reports.items():
        if level not in levels:
            continue
        result[level.name] = [asdict(report) for report in reports]
    return json.dumps(result, indent=4)
