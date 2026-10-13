"""Curated explicit aliases; boundaries prevent substring skill matches."""
import re

SKILLS = {
    'Python': ['python'], 'Java': ['java'], 'JavaScript': ['javascript', 'js'],
    'TypeScript': ['typescript'], 'C++': ['c++'], 'C#': ['c#'], '.NET': ['.net', 'dotnet'],
    'R': ['r'], 'Go': ['golang', 'go language'], 'HTML': ['html', 'html5'],
    'CSS': ['css', 'css3'], 'React': ['react', 'react.js', 'reactjs'],
    'Node.js': ['node.js', 'nodejs'], 'Angular': ['angular'], 'Vue': ['vue', 'vue.js'],
    'Django': ['django'], 'Flask': ['flask'], 'FastAPI': ['fastapi'],
    'REST API': ['rest api', 'rest apis', 'restful api', 'restful apis'],
    'SQL': ['sql'], 'PostgreSQL': ['postgresql', 'postgres'], 'MySQL': ['mysql'],
    'SQLite': ['sqlite'], 'MongoDB': ['mongodb'], 'Redis': ['redis'],
    'Pandas': ['pandas'], 'NumPy': ['numpy'], 'Excel': ['excel'],
    'Power BI': ['power bi', 'powerbi'], 'Tableau': ['tableau'],
    'Machine Learning': ['machine learning', 'ml'], 'scikit-learn': ['scikit-learn', 'sklearn'],
    'TensorFlow': ['tensorflow'], 'PyTorch': ['pytorch'],
    'AWS': ['aws', 'amazon web services'], 'Azure': ['azure'], 'GCP': ['gcp', 'google cloud'],
    'Docker': ['docker'], 'Kubernetes': ['kubernetes', 'k8s'],
    'Git': ['git'], 'GitHub': ['github'], 'Linux': ['linux'],
    'CI/CD': ['ci/cd', 'continuous integration', 'continuous delivery'],
    'Testing': ['pytest', 'unit testing'],
}

def alias_pattern(alias):
    return r'(?<![\w+#.])' + re.escape(alias).replace(r'\ ', r'\s+') + r'(?![\w+#])'

PATTERNS = {skill: re.compile('|'.join(alias_pattern(a) for a in aliases), re.I)
            for skill, aliases in SKILLS.items()}

def extract_skills(text):
    return {skill for skill, pattern in PATTERNS.items() if pattern.search(text)}
