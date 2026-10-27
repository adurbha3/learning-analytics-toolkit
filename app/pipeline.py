"""Runs the full pipeline end to end: generate messy data, clean it, score
students for academic support needs, compute marketing analytics, and write
the Excel reporting workbook."""
from __future__ import annotations

from pathlib import Path

from app.cleaning import clean_keyword_data, clean_sessions, clean_web_analytics
from app.excel_report import build_workbook
from app.marketing_analytics import conversion_rate_by_source, keyword_opportunities
from app.risk_scoring import score_students
from app.synthetic_data import generate_keyword_data, generate_sessions, generate_web_analytics


def run(output_dir: str = "output") -> str:
    Path(output_dir).mkdir(exist_ok=True)

    sessions = clean_sessions(generate_sessions())
    web = clean_web_analytics(generate_web_analytics())
    keywords = clean_keyword_data(generate_keyword_data())

    student_scores = score_students(sessions)
    conversion = conversion_rate_by_source(web)
    opportunities = keyword_opportunities(keywords)

    output_path = str(Path(output_dir) / "learning_analytics_report.xlsx")
    build_workbook(student_scores, conversion, opportunities, output_path)
    return output_path


if __name__ == "__main__":
    path = run()
    print("wrote", path)
