# SkillMatch

**Resume Retrieval and Job Description Matching Using TF-IDF and Cosine Similarity**

SPPU · B.E. Computer Engineering (2019 Pattern) · 410245(A) Information Retrieval · 410247 Laboratory Practice IV · Academic year 2026–27.

This custom mini-project should receive faculty approval if that has not already been obtained. It is an academic document retrieval prototype, not a hiring decision system.

## Problem and objectives

Comparing many resumes manually is time-consuming. SkillMatch retrieves resumes whose language is relevant to a job description and provides source evidence. It accepts documents, extracts and preprocesses text, identifies explicit technical skills, computes real document similarity, ranks resumes, explains matched and undetected skills, and exports the comparison.

## Run on macOS

Python 3.11 or newer is required; Python 3.12 or 3.13 is a good option if an older dependency lacks wheels for your interpreter. From this project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit (usually http://localhost:8501). To stop, press Control-C. If using the environment already installed during implementation, only activation and the Streamlit command are needed.

Optional focused verification:

```bash
python -m pip install pytest
python -m pytest -q
```

## Using the application

1. Open **Upload & process**.
2. Select **Synthetic demo**, choose one of three roles, and leave the eight fictional resumes selected, or select **My documents** to paste/upload a job description and upload multiple resumes.
3. Click **Analyze & rank resumes**.
4. Open **Matching results** for the ranking, chart, source passages, extracted text and CSV download.
5. Open **Resume comparison** for a side-by-side skill table.

Changing inputs does not automatically update results: analyze again. Clear session removes the stored analysis and resets input widgets. Invalid resumes are skipped with messages; an invalid JD prevents analysis. Files are limited to 5 MB each. Duplicate filenames retain distinct internal IDs. Uploads are processed in memory, never executed or saved by application code, and are not sent to external services. This is a local demonstration app; no database, authentication or cloud deployment is used.

## Features and technologies

- Streamlit dashboard with overview, input, results, comparison and methodology tabs.
- PyMuPDF reads text PDFs; python-docx reads paragraphs and table cells; TXT uses UTF-8.
- scikit-learn computes TF-IDF and cosine similarity; Pandas builds tables and CSV.
- Explicit curated skill dictionary, technical aliases and reproducible tie handling.
- Document similarity chart, matched/undetected skill chart and relevant source segments.
- Eight synthetic resumes and three job descriptions: Python Backend Developer, Data Analyst and Frontend Web Developer. Names are fictional and no contact data is included. The systems resume covers C++, C# and .NET; the full-stack resume covers Node.js.

## Architecture and workflow

```text
Job description + resumes
        ↓
In-memory text extraction (PDF / DOCX / TXT)
        ↓
Case + alias normalization → tokenization → stop-word removal
        ↓
Shared collection TF-IDF → cosine similarity → deterministic ranking
        ↓
Explicit skill comparison + passage retrieval
        ↓
Streamlit tables / charts / source evidence / CSV
```

The application keeps the last successful comparison in Streamlit session state. Extraction, preprocessing, skills and ranking are separate small modules, making the algorithm easy to explain during a viva.

## Preprocessing and skills

Text is lowercased; known dictionary aliases become stable canonical tokens before tokenization. For example JS and JavaScript share `skill_javascript`, while C++ and C# remain distinct tokens. English stop words are removed using scikit-learn's list; punctuation separates ordinary terms, and numeric-only tokens are removed. No stemming is used because it can distort technical vocabulary.

`skillmatch/skills.py` contains the complete manageable dictionary spanning languages, web, backend, databases, analytics, ML, cloud and development tools. Case-insensitive boundary-aware regular expressions recognize explicit phrases, including Postgres/PostgreSQL and RESTful API/REST API. R does not match inside an unrelated word. Skill mentions are detected from original text, independently of the retrieval score. The dictionary does not infer unmentioned skills, proficiency or whether a mention is negated. Ambiguous abbreviations can still produce false positives.

All detected JD skills are compared, whether the description calls them required, optional, or mentions them in another context. Matched skills are the intersection of JD and resume sets. “Not detected” is the JD set minus the resume set; it does not mean the person lacks that skill.

## TF-IDF and ranking

Each term receives a frequency weight multiplied by its inverse document frequency. With scikit-learn defaults, smoothed IDF is:

```text
idf(t) = log((1 + N) / (1 + df(t))) + 1
weight(t,d) = count(t,d) × idf(t)
```

Vectors are L2 normalized. The model is fitted once on the JD plus all resumes in the current comparison, producing a shared feature space. Cosine similarity is `dot(q,d) / (norm(q) × norm(d))`. For nonnegative TF-IDF it ranges from 0 to 1. Scores are calculated, not hardcoded. Sorting uses descending score, case-insensitive filename, then input order. Empty/unsearchable JDs are rejected; unreadable uploads are rejected during extraction. A readable resume with no searchable tokens receives a zero vector and zero similarity.

Source text is split on line breaks or sentence-ending punctuation. Each segment is transformed with the same fitted vectorizer and compared against the JD vector. The three highest-scoring positive segments are shown verbatim. Segments can be short due to PDF layout; they are evidence of lexical overlap, not independent justification of competency.

## Interpreting results and evaluation

**Cosine similarity** measures lexical document relevance. **Explicit skill coverage** measures matched detected skills divided by all detected JD skills, and is blank when no JD skills are detected. Coverage is displayed as a 0–1 fraction. These values are separate and are never combined into a suitability score. Full-precision values are exported; the UI rounds similarities for readability. The highest-ranked resume is not necessarily the most qualified person. Adding or removing resumes changes IDF and may change scores.

The focused tests verify representative PDF/DOCX/TXT extraction, corrupt and empty input handling, technical aliases, controlled ranking, grounded passages, deterministic results, CSV equality and a Streamlit demo run. The controlled backend example should rank Aarav above the unrelated operations resume. This is a basic sanity check, not a measured retrieval-effectiveness benchmark. Precision, recall and MAP require faculty-reviewed relevance judgments and are future evaluation work.

## Project structure

```text
app.py                       Streamlit interface
requirements.txt             Runtime dependencies
.streamlit/config.toml       Accent theme and upload limit
skillmatch/
  extractor.py               In-memory document extraction
  preprocessing.py           Consistent retrieval tokenization
  skills.py                  Curated dictionary and explicit matching
  ranking.py                 TF-IDF, passages, tables and CSV
 data/samples/
  job_descriptions/          Three fictional roles
  resumes/                   Eight fictional resumes
 tests/test_core.py          Focused essential checks
```

## Relation to the IR syllabus

| Unit | Implemented relationship |
| --- | --- |
| I | Tokenization, stop words, TF-IDF and vector space retrieval. No stemming. |
| II | JD acts as a query for ranked document retrieval. Vocabulary and sparse term matrices relate to index concepts; no custom inverted index is implemented. |
| IV | Similarity ranking and comparison/filtering of documents in the UI. No BM25 or probabilistic retrieval model. |
| V | Controlled retrieval checks, reproducibility and interpretation. No formal benchmark or relevance judgments yet. |

Units III and VI are not implemented; the project does not claim coverage of all six units.

## Limitations and future scope

TF-IDF measures lexical overlap rather than deep semantic meaning. Unknown synonyms and dictionary gaps reduce matching; keyword repetition influences relevance. Resume formatting affects extraction; text in DOCX drawings/headers and scanned PDFs may not be read. OCR is not supported. The system does not interpret negation, experience duration, qualification validity or actual competency. It must not automatically hire or reject people.

Future work could add OCR, a reviewed skill dictionary, BM25 comparisons, labeled relevance judgments with precision/recall evaluation, and improved PDF reading order. A full academic report and screenshots are intentionally left for later manual demonstration and documentation.

## Report screenshots and manual cases

See [SCREENSHOT_TEST_CASES.md](SCREENSHOT_TEST_CASES.md) for reproducible scenarios, computed demo reference values and suggested figure captions. Additional upload fixtures in `data/screenshot_cases/` include a technical-skills JD, equivalent fictional TXT/PDF/DOCX resumes, an empty TXT and a blank no-text PDF. These fixtures are separate from the default eight-resume demo collection.
