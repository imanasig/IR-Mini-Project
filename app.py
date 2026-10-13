from pathlib import Path
from html import escape
import pandas as pd
import streamlit as st
from skillmatch.extractor import extract_text, ExtractionError
from skillmatch.ranking import rank_resumes, comparison_frame, export_csv

st.set_page_config(page_title='SkillMatch · Resume retrieval', page_icon='◈', layout='wide')
st.markdown('''<style>
.block-container {max-width:1200px;padding-top:2rem;padding-bottom:3rem;}
h1 {letter-spacing:-.045em;} h2,h3 {letter-spacing:-.025em;}
[data-testid="stSidebar"] {background:linear-gradient(160deg,#6366f112,#0d948815);border-right:1px solid #87999b30;}
[data-testid="stMetric"] {background:linear-gradient(135deg,#6366f112,#06b6d409);border:1px solid #6366f130;border-radius:16px;padding:20px;}
[data-testid="stMetric"] [data-testid="stMetricValue"] {color:#6366f1;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:16px;}
.stButton button[kind="primary"] {background:linear-gradient(110deg,#4f46e5,#0d9488);border:none;border-radius:10px;min-height:3rem;}
button[data-baseweb="tab"] {padding:12px 18px;border-radius:9px 9px 0 0;}
button[data-baseweb="tab"][aria-selected="true"] {background:#6366f115;}
.hero {background:linear-gradient(115deg,#172554 0%,#3730a3 52%,#0f766e 100%);padding:34px 38px;border-radius:22px;color:#fff;margin-bottom:24px;box-shadow:0 12px 30px #312e8118;}
.hero .eyebrow {font-size:.75rem;letter-spacing:.14em;color:#c7d2fe;font-weight:600;}
.hero h1 {color:#fff;font-size:clamp(1.9rem,4vw,2.8rem);line-height:1.15;margin:14px 0;}
.hero p {color:#e0e7ff;max-width:740px;font-size:1rem;line-height:1.65;margin-bottom:20px;}
.hero-tags {display:flex;flex-wrap:wrap;gap:8px;}
.hero-tags span {border:1px solid #ffffff35;background:#ffffff12;border-radius:50px;padding:5px 12px;font-size:.78rem;color:#f0fdfa;}
.step-card {padding:24px;border-radius:16px;min-height:210px;border:1px solid #6366f130;background:linear-gradient(145deg,#6366f113,#6366f103);}
.step-card.teal {border-color:#14b8a640;background:linear-gradient(145deg,#14b8a619,#14b8a604);}
.step-card.amber {border-color:#f59e0b40;background:linear-gradient(145deg,#f59e0b19,#f59e0b04);}
.step-number {display:inline-block;font-weight:700;color:#818cf8;font-size:.8rem;letter-spacing:.1em;margin-bottom:12px;}
.teal .step-number {color:#0d9488;} .amber .step-number {color:#d97706;}
.step-card h3 {font-size:1.2rem;margin:0 0 10px;}
.step-card p {font-size:.94rem;line-height:1.65;opacity:.85;margin:0;}
.skill-chips {display:flex;flex-wrap:wrap;gap:7px;margin:10px 0 18px;}
.skill-chip {padding:5px 11px;border-radius:8px;font-size:.83rem;font-weight:600;background:#6366f118;color:#818cf8;border:1px solid #6366f140;}
.skill-chip.match {background:#14b8a618;color:#0d9488;border-color:#14b8a640;}
.skill-chip.missing {background:#f59e0b18;color:#b77908;border-color:#f59e0b40;}
@media(max-width:640px) {.hero {padding:24px;} .step-card {min-height:0;margin-bottom:10px;}}
</style>''', unsafe_allow_html=True)

def skill_chips(skills, tone=''):
    if not skills:
        st.caption('None detected')
        return
    chips = ''.join(f'<span class="skill-chip {tone}">{escape(skill)}</span>' for skill in skills)
    st.markdown(f'<div class="skill-chips">{chips}</div>', unsafe_allow_html=True)

SAMPLES = Path(__file__).parent / 'data' / 'samples'
with st.sidebar:
    st.markdown('## ◈ SkillMatch')
    st.caption('INFORMATION RETRIEVAL LAB')
    st.divider()
    st.markdown('**Your documents. Clear evidence.**')
    st.write('Compare resumes with a job description using explainable text retrieval.')
    st.divider()
    st.caption('LOCAL PROCESSING · NO EXTERNAL APIS')
    st.caption('PDF · DOCX · TXT\n\n5 MB per document')
    if st.button('Clear session', use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.markdown('''<div class="hero">
<div class="eyebrow">SKILLMATCH · INFORMATION RETRIEVAL WORKSPACE</div>
<h1>Find relevance.<br>See the evidence.</h1>
<p>Turn a collection of resumes into a clear, explainable comparison. Explore textual relevance, technical skills, and the source passages behind every result.</p>
<div class="hero-tags"><span>TF-IDF + cosine similarity</span><span>Local document processing</span><span>SPPU · 2026–27</span></div>
</div>''', unsafe_allow_html=True)
home, upload, results, compare, about = st.tabs(['Overview', 'Upload & process', 'Matching results', 'Resume comparison', 'Methodology'])
with home:
    st.subheader('From documents to an explainable ranking')
    a, b, c = st.columns(3)
    cards = [
        (a, '', '01 / DOCUMENTS', 'Add your collection', 'Enter a job description and upload resumes, or explore our fictional demo collection.'),
        (b, 'teal', '02 / RETRIEVAL', 'Discover relevance', 'Compare document language with TF-IDF and cosine similarity, using real computed scores.'),
        (c, 'amber', '03 / EVIDENCE', 'Understand each result', 'Inspect explicit skills and source passages, compare resumes, and export your findings.'),
    ]
    for column, tone, number, title, description in cards:
        with column:
            st.markdown(f'<div class="step-card {tone}"><span class="step-number">{number}</span><h3>{title}</h3><p>{description}</p></div>', unsafe_allow_html=True)
    st.write('')
    st.info('Start in Upload & process. Similarity describes documents; it does not measure competency or determine hiring decisions.')
    st.caption('8 fictional resumes · 3 example roles · Reproducible local calculations')
with upload:
    st.subheader('Build your comparison')
    mode = st.radio('Document source', ['Synthetic demo', 'My documents'], horizontal=True)
    documents = []
    job = ''
    label = ''
    if mode == 'Synthetic demo':
        paths = sorted((SAMPLES / 'job_descriptions').glob('*.txt'))
        selected = st.selectbox('Choose a job description', paths, format_func=lambda p: p.stem.replace('_', ' ').title())
        job = selected.read_text()
        label = selected.stem.replace('_', ' ').title()
        st.text_area('Job description preview', job, height=190, disabled=True)
        resume_paths = sorted((SAMPLES / 'resumes').glob('*.txt'))
        chosen = st.multiselect('Resume collection', resume_paths, default=resume_paths, format_func=lambda p: p.name)
        documents = [(p.name, p.read_text()) for p in chosen]
        st.caption('All names and documents in this collection are fictional.')
    else:
        label = st.text_input('Comparison label', 'My job description')
        source = st.radio('Job description input', ['Paste text', 'Upload file'], horizontal=True)
        if source == 'Paste text':
            job = st.text_area('Job description', height=220, placeholder='Paste the role, responsibilities, and technical skills…')
        else:
            jd = st.file_uploader('Job description file', type=['pdf', 'docx', 'txt'], key='jd')
            if jd:
                try:
                    job = extract_text(jd.name, jd.getvalue())
                except ExtractionError as exc:
                    st.error(str(exc))
        files = st.file_uploader('Resume documents', type=['pdf', 'docx', 'txt'], accept_multiple_files=True)
        for file in files:
            try:
                documents.append((file.name, extract_text(file.name, file.getvalue())))
            except ExtractionError as exc:
                st.warning(f'{file.name}: {exc} This document will be skipped.')
        st.caption('Uploads stay in session memory and are not saved by SkillMatch. TXT files must use UTF-8 encoding.')
    if st.button('Analyze & rank resumes', type='primary', use_container_width=True):
        st.session_state.pop('analysis', None)
        if not job.strip() or not documents:
            st.error('Provide a readable job description and at least one resume.')
        else:
            try:
                with st.spinner('Extracting skills and computing document relevance…'):
                    rows, skills = rank_resumes(job, documents)
                    st.session_state.analysis = dict(rows=rows, skills=skills, label=label)
                st.success('Comparison ready. Open Matching results to explore the ranking.')
            except ValueError as exc:
                st.error(str(exc))
    if 'analysis' in st.session_state:
        st.caption('Results reflect the last successful analysis. Run analysis again after changing inputs.')

analysis = st.session_state.get('analysis')

with results:
    if not analysis:
        st.info('Add documents and run analysis to see your ranking.')
    else:
        rows = analysis['rows']
        st.subheader(analysis['label'])
        a, b, c = st.columns(3)
        a.metric('Resumes processed', len(rows))
        b.metric('Job description skills', len(analysis['skills']))
        c.metric('Highest cosine similarity', f"{rows[0]['similarity']:.3f}")
        st.markdown('**Technical skills detected in the job description**')
        skill_chips(analysis['skills'])
        frame = comparison_frame(rows)
        st.subheader('Ranked documents')
        st.dataframe(frame.iloc[:, :6], hide_index=True, use_container_width=True,
                     column_config={'Cosine similarity': st.column_config.NumberColumn(format='%.4f'),
                                    'Skill coverage': st.column_config.NumberColumn(format='%.2f')})
        st.caption('Cosine similarity: 0–1 lexical relevance. Skill coverage: fraction of detected JD skills also detected in the resume; blank when the JD contains none. All detected JD skills are compared, including any described as optional.')
        st.bar_chart(frame.set_index('Resume')[['Cosine similarity']], horizontal=True, sort=False, color='#6366F1')
        st.download_button('Download comparison CSV', export_csv(rows), 'skillmatch_results.csv', 'text/csv')
        st.divider()
        selected_id = st.selectbox('Inspect a resume', [r['id'] for r in rows], format_func=lambda i: next(f"#{r['rank']} · {r['filename']}" for r in rows if r['id'] == i))
        row = next(r for r in rows if r['id'] == selected_id)
        left, right = st.columns(2)
        with left:
            with st.container(border=True):
                st.markdown('**Matched technical skills**')
                skill_chips(row['matched'], 'match')
                st.markdown('**Job description skills not detected**')
                skill_chips(row['missing'], 'missing')
                st.caption('Not detected means absent from the extracted text under the dictionary rules.')
                st.markdown('**All resume skills detected**')
                skill_chips(row['skills'])
        with right:
            st.markdown('**Relevant source passages**')
            for passage, score in row['passages']:
                with st.container(border=True):
                    st.write(passage)
                    st.caption(f'Passage cosine similarity · {score:.3f}')
            if not row['passages']:
                st.caption('No passages have positive similarity with this job description.')
        st.bar_chart(pd.DataFrame({'Matched': [len(row['matched'])], 'Not detected': [len(row['missing'])]}, index=['Job description skills']), color=['#14B8A6', '#F59E0B'], stack=False)
        with st.expander('Extracted resume text'):
            st.text(row['text'])
with compare:
    st.subheader('Compare explicit technical skills')
    if not analysis:
        st.info('Run an analysis to compare resumes side by side.')
    else:
        rows = analysis['rows']
        choices = st.multiselect('Select resumes', [r['id'] for r in rows], default=[r['id'] for r in rows[:3]], format_func=lambda i: next(f"#{r['rank']} · {r['filename']}" for r in rows if r['id'] == i))
        selected_rows = [r for r in rows if r['id'] in choices]
        if selected_rows:
            st.dataframe(comparison_frame(selected_rows), hide_index=True, use_container_width=True)
            if analysis['skills']:
                matrix = pd.DataFrame({'Job description skill': analysis['skills']})
                for row in selected_rows:
                    matrix[f"#{row['rank']} {row['filename']}"] = ['Detected' if s in row['skills'] else 'Not detected' for s in analysis['skills']]
                st.dataframe(matrix, hide_index=True, use_container_width=True)
with about:
    st.subheader('A transparent vector space model')
    st.markdown('''1. Extract text from PDF, DOCX, or UTF-8 TXT in memory.
2. Normalize case and curated aliases, tokenize, and remove English stop words. Known technical skills receive stable tokens, preserving C++, C#, .NET, and Node.js distinctions.
3. Fit TF-IDF on the job description and the current resume collection together.
4. Compute cosine similarity to the job vector and rank by descending score. Ties use filename, then upload order.
5. Match explicit dictionary skills and retrieve the three highest-scoring positive source segments using the same fitted vocabulary.

**TF-IDF** weights a term by its frequency and how uncommon it is in this collection. **Cosine similarity** compares the direction of normalized document vectors. Changing the comparison collection can change IDF weights and scores.

**Limits:** lexical matching cannot assess competency, negation, years of experience, or deep semantic meaning. Dictionary detection can be ambiguous (for example R or ML), and mentions do not imply proficiency. Scanned PDFs need OCR; document formatting can affect extraction. There is no custom inverted index, BM25, model training, or automated hiring decision.

**Academic alignment:** Unit I covers preprocessing, TF-IDF and vector spaces; Unit II relates to query processing and ranked retrieval; Unit IV relates to similarity ranking and filtering; Unit V introduces interpretation and controlled retrieval checks. Faculty approval is still needed for this custom mini-project title if not already obtained.''')
