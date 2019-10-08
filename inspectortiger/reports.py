from dataclasses import dataclass


@dataclass
class Report:
    code: str
    lineno: int
    filename: str


def _prepare_result(all_reports, indent_with=2):
    """
    [PLUGIN]
      - :file:lineno: code

    [MISC]
      - :test.py:32: SUPER_ARGS
    """
    buffer = ""
    for plugin, reports in all_reports.items():
        buffer += f"[{plugin}]\n"
        for report in reports:
            buffer += " " * indent_with
            buffer += f"- :{report['filename']}:{report['lineno']}: {report['code']}\n"
    return buffer
