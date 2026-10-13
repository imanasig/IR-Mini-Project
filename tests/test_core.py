from io import BytesIO
from pathlib import Path
import fitz
import pytest
from docx import Document
from skillmatch.extractor import extract_text, ExtractionError
from skillmatch.skills import extract_skills
from skillmatch.preprocessing import tokenize
from skillmatch.ranking import rank_resumes, comparison_frame, export_csv


def test_extraction_formats_and_errors():
    assert extract_text('a.txt', b'Python SQL') == 'Python SQL'
    doc = Document()
    doc.add_paragraph('Python SQL')
    buffer = BytesIO()
    doc.save(buffer)
    assert 'Python SQL' in extract_text('a.docx', buffer.getvalue())
    with fitz.open() as pdf:
        pdf.new_page().insert_text((72, 72), 'Python SQL')
        assert 'Python SQL' in extract_text('a.pdf', pdf.tobytes())
    for name, data in [('empty.txt', b''), ('bad.pdf', b'invalid'), ('bad.exe', b'test')]:
        with pytest.raises(ExtractionError):
            extract_text(name, data)
    with fitz.open() as pdf:
        pdf.new_page()
        with pytest.raises(ExtractionError, match='OCR'):
            extract_text('scan.pdf', pdf.tobytes())


def test_skills_and_aliases():
    found = extract_skills('C++ C# .NET Node.js React.js JS Postgres RESTful API ML R')
    assert {'C++', 'C#', '.NET', 'Node.js', 'React', 'JavaScript', 'PostgreSQL', 'REST API', 'Machine Learning', 'R'} <= found
    assert not extract_skills('progress javaScripted cargo')
    assert tokenize('JS Postgres') == tokenize('JavaScript PostgreSQL')
    assert len(set(tokenize('C++ C# .NET Node.js'))) == 4


def test_ranking_passages_and_csv():
    root = Path(__file__).parents[1] / 'data/samples'
    job = (root/'job_descriptions/python_backend_developer.txt').read_text()
    docs = [(p.name, p.read_text()) for p in sorted((root/'resumes').glob('*.txt'))]
    rows, skills = rank_resumes(job, docs)
    assert rows[0]['filename'] == '01_aarav_backend.txt'
    assert rows[0]['similarity'] > next(r['similarity'] for r in rows if r['filename'] == '08_nila_operations.txt')
    assert rows[0]['passages'] and all(p in rows[0]['text'] for p, _ in rows[0]['passages'])
    assert export_csv(rows).decode('utf-8-sig') == comparison_frame(rows).to_csv(index=False)
    assert rank_resumes(job, docs)[0] == rows
    tied, _ = rank_resumes('Python', [('z.txt', 'Python'), ('a.txt', 'Python')])
    assert tied[0]['filename'] == 'a.txt'
    with pytest.raises(ValueError):
        rank_resumes('the and', docs)


def test_streamlit_app_starts_and_demo_runs():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(Path(__file__).parents[1] / 'app.py')).run(timeout=30)
    assert not app.exception
    next(b for b in app.button if b.label == 'Analyze & rank resumes').click().run(timeout=30)
    assert not app.exception
    assert app.session_state['analysis']['rows']
