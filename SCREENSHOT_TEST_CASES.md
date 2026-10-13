# Screenshot test cases for SkillMatch

Run `python -m streamlit run app.py` from your activated virtual environment. Use a desktop browser at approximately 1280–1440 pixels wide, close the sidebar if you need more table space, and capture the actual app output. All documents below are fictional. Record the observed outcome before marking a case “Pass” in your report.

For cases 2–6, choose **Synthetic demo**, keep **all eight resumes** selected and click **Analyze & rank resumes** after changing the role. Scores below were computed with this exact collection; rounding or package versions can affect the final digit, and a different collection changes TF-IDF weights.

| ID | Scenario and actions | Expected outcome | Suggested figure caption |
| --- | --- | --- | --- |
| TC01 | Open **Overview** before analyzing. | Header, three workflow cards and clear navigation appear. | SkillMatch home interface and document retrieval workflow. |
| TC02 | Choose **Python Backend Developer**; analyze; open **Matching results**. Capture the metrics and ranked table, then scroll for the chart. | `01_aarav_backend.txt` ranks first, cosine approximately **0.7024**; 8 resumes and 7 JD skills. | Resume ranking for the Python backend job description using TF-IDF and cosine similarity. |
| TC03 | Continue TC02; select `02_meera_backend.txt` under **Inspect a resume**. Capture skill badges and source passages. | Matched: Git, Python, REST API. Not detected: Django, Docker, PostgreSQL, Testing. Positive passages come from Meera’s text. | Explicit matched and undetected skills with supporting resume passages for a partial backend match. |
| TC04 | Continue TC02; open **Resume comparison** and select Aarav, Meera and Nila (remove any other selections). | Aarav matches all 7 JD skills; Meera matches 3; Nila matches none. Similarity and coverage remain separate columns. | Side-by-side comparison of strong, partial and unrelated resume documents. |
| TC05 | Choose **Data Analyst**; analyze; open **Matching results**. | `03_ishaan_analyst.txt` ranks first, cosine approximately **0.5912**. JD skills: Excel, Pandas, Power BI, Python, SQL. | Retrieval results for the data analyst job description. |
| TC06 | Choose **Frontend Web Developer**; analyze; open **Matching results**. | `04_sana_frontend.txt` ranks first, cosine approximately **0.7286**. Seven JD skills are detected. | Retrieval results for the frontend web developer job description. |
| TC07 | Choose **My documents → Upload file** for the JD. Upload `technical_skills_job.txt` from `data/screenshot_cases/`; upload all three `technical_skills_resume` files (TXT, PDF, DOCX); analyze. Inspect one resume and expand its extracted text. | All three files process. Each matches C++, C#, .NET, Node.js, JavaScript, PostgreSQL and REST API. JS, Postgres and RESTful API aliases normalize correctly. Do not require identical cosine scores: line layouts may differ. | Technical symbol and alias recognition across TXT, PDF and DOCX documents. |
| TC08 | Continue TC07; also upload `empty_resume.txt` and `no_text_resume.pdf`. Capture the warnings in **Upload & process**. | Empty TXT is skipped; no-text PDF is skipped with an OCR message. The 3 readable files remain usable. The PDF fixture is blank, simulating a PDF with no extractable text; it is not a scanned resume. | Graceful handling of empty documents and PDFs without extractable text. |
| TC09 | Run TC02; click **Download comparison CSV**. Open the downloaded file in Numbers/Excel. | 8 ranked records, with the same similarities, skill counts, coverage and skill names as the application. CSV retains full precision. | Exported resume comparison results for the backend role. |
| TC10 | Choose **My documents → Paste text**, leave JD empty; click **Analyze & rank resumes**. | A message asks for a readable JD and at least one resume; no crash or fabricated results. | Input validation before document retrieval. |

## Recommended report set

Use TC01, TC02, TC03, TC04, TC07 and TC08 for a compact six-figure report. Add TC05/TC06 to demonstrate generalization across the three sample roles and TC09 if documenting export.

For a legible screenshot, frame one section at a time rather than shrinking the whole page. Keep the selected role or resume visible. Describe scores as **cosine similarity**, never hiring suitability or competency percentages. Label undetected skills exactly as **not detected in the document**.

## Test record template

| Test ID | Input / action | Expected outcome | Observed outcome | Pass / Fail |
| --- | --- | --- | --- | --- |
| TC02 | Backend JD + all 8 synthetic resumes | Aarav ranks first | Fill after running | Fill after running |

The expected values are computed reference results, not proof that you manually ran the cases. Populate observed outcomes from your own demonstration.
