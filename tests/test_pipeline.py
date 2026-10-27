from pathlib import Path

from app.pipeline import run


def test_pipeline_runs_end_to_end_and_writes_workbook(tmp_path):
    output_path = run(output_dir=str(tmp_path))
    assert Path(output_path).exists()
    assert Path(output_path).suffix == ".xlsx"
