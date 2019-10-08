from dataclasses import dataclass


@dataclass
class Report:
    code: str
    lineno: int
    filename: str


def _prepare_result(all_reports, indent_with=2):
    """
    [PLUGIN]
      - file:lineno => code

    [misc]
      - ../t.py:2    => DEFAULT_MUTABLE_ARG
      - ../t.py:5    => CONTROL_FLOW_INSIDE_FINALLY
    [upgradeable]
      - ../t.py:2    => OPTIONAL
      - ../t.py:6    => SUPER_ARGS
      - ../t.py:14   => YIELD_FROM
    [unreachable_except]
      - ../t.py:5    => UNREACHABLE_EXCEPT
    """
    buffer = ""
    for plugin, reports in all_reports.items():
        buffer += f"[{plugin}]\n"
        for report in reports:
            buffer += " " * indent_with
            buffer += f"- {report['filename']}:{report['lineno']}"
            buffer += " " * (5 - len(str(report["lineno"])))
            buffer += f"=> {report['code']}\n"
    return buffer
