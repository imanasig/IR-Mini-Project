"""Shared collection TF-IDF, deterministic cosine ranking, source passages."""
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .preprocessing import tokenize
from .skills import extract_skills

def rank_resumes(job, documents):
    if not tokenize(job):
        raise ValueError('The job description has no searchable terms.')
    if not documents:
        raise ValueError('Add at least one readable resume.')
    vectorizer = TfidfVectorizer(tokenizer=tokenize, token_pattern=None, lowercase=False)
    matrix = vectorizer.fit_transform([job] + [text for _, text in documents])
    scores = cosine_similarity(matrix[0], matrix[1:]).ravel()
    job_skills = extract_skills(job)
    rows = []
    for index, ((name, text), score) in enumerate(zip(documents, scores)):
        skills = extract_skills(text)
        segments = [s.strip() for s in re.split(r'\n+|(?<=[.!?])\s+', text) if s.strip()]
        passage_scores = cosine_similarity(matrix[0], vectorizer.transform(segments)).ravel()
        passages = sorted(zip(segments, passage_scores), key=lambda p: -p[1])[:3]
        rows.append(dict(id=index, filename=name, similarity=float(score), skills=sorted(skills),
                         matched=sorted(skills & job_skills), missing=sorted(job_skills - skills),
                         text=text, passages=[(s, float(v)) for s, v in passages if v > 0]))
    rows.sort(key=lambda row: (-row['similarity'], row['filename'].casefold(), row['id']))
    for rank, row in enumerate(rows, 1):
        row['rank'] = rank
    return rows, sorted(job_skills)

def comparison_frame(rows):
    return pd.DataFrame([{'Rank': r['rank'], 'Resume': r['filename'],
                          'Cosine similarity': r['similarity'], 'Matched skills': len(r['matched']),
                          'Not detected': len(r['missing']),
                          'Skill coverage': len(r['matched']) / (len(r['matched']) + len(r['missing']))
                          if r['matched'] or r['missing'] else None,
                          'Matched skill names': ', '.join(r['matched']),
                          'Not detected skill names': ', '.join(r['missing'])} for r in rows])

def export_csv(rows):
    return comparison_frame(rows).to_csv(index=False).encode('utf-8-sig')
