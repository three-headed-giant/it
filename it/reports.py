from dataclasses import dataclass


@dataclass
class Report:
    code: str
    column: int
    lineno: int
    filename: str


def _prepare_result(all_reports, indent_with=2):
    """
    [PLUGIN]
      - file:lineno:column => code

    [misc]
      - ../t.py:2:3     => DEFAULT_MUTABLE_ARG
      - ../t.py:5:5     => CONTROL_FLOW_INSIDE_FINALLY
    [upgradeable]
      - ../t.py:2:7     => OPTIONAL
      - ../t.py:6:8     => SUPER_ARGS
      - ../t.py:14:1    => YIELD_FROM
    [unreachable_except]
      - ../t.py:5:2     => UNREACHABLE_EXCEPT
    """
    buffer = ""
    for plugin, reports in all_reports.items():
        buffer += f"[{plugin}]\n"
        for report in reports:
            buffer += " " * indent_with
            buffer += (
                f"- {report['filename']}:{report['lineno']}:{report['column']}"
            )
            buffer += " " * (
                8
                - (len(str(report["lineno"])) + len(str(report["column"])) + 1)
            )
            buffer += f"=> {report['code']}\n"
    return buffer
