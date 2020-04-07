from dataclasses import asdict

from it.reports import Report, _prepare_result


def test_prepare_result(tmp_path):
    reports = [
        asdict(Report("MY_ERROR", 0, 0, tmp_path / f"{idx}.py"))
        for idx in range(3)
    ]
    reports = {"blabla": reports[:1], "otherbla": reports[1:]}
    assert _prepare_result(reports) == (
        "[blabla]\n"
        f"  - {tmp_path}/0.py:0:0     => MY_ERROR\n"
        "[otherbla]\n"
        f"  - {tmp_path}/1.py:0:0     => MY_ERROR\n"
        f"  - {tmp_path}/2.py:0:0     => MY_ERROR\n"
    )
