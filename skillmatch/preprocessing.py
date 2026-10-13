"""Normalize known skill aliases before symbol-preserving tokenization."""
import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from .skills import PATTERNS

def tokenize(text):
    normalized = text.lower()
    # A single substitution avoids replacing an alias inside another replacement.
    matches = []
    for skill, pattern in PATTERNS.items():
        matches.extend((m.start(), m.end(), re.sub(r'\W+', '_', skill.lower().replace('+', 'plus').replace('#', 'sharp')).strip('_'))
                       for m in pattern.finditer(normalized))
    end = 0
    parts = []
    for start, stop, canonical in sorted(matches, key=lambda m: (m[0], -m[1])):
        if start < end:
            continue
        parts.extend([normalized[end:start], ' skill_' + canonical + ' '])
        end = stop
    parts.append(normalized[end:])
    return [t for t in re.findall(r'skill_[a-z0-9_]+|\.net|[a-z0-9]+(?:[.+#/-][a-z0-9+#]+)*', ''.join(parts))
            if t not in ENGLISH_STOP_WORDS and not t.isdigit()]
