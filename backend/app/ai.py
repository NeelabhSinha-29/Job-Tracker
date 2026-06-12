from __future__ import annotations

import re
from collections import Counter


SKILL_PHRASES = [
    "machine learning",
    "deep learning",
    "data analysis",
    "data analytics",
    "prompt engineering",
    "rest api",
    "ci/cd",
    "scikit-learn",
    "next.js",
    "postgresql",
    "typescript",
    "javascript",
    "kubernetes",
    "airflow",
    "tableau",
    "power bi",
    "fastapi",
    "docker",
    "python",
    "sql",
    "react",
    "node.js",
    "flask",
    "django",
    "aws",
    "gcp",
    "azure",
    "pandas",
    "numpy",
    "excel",
    "spark",
    "etl",
    "dbt",
    "git",
    "linux",
    "graphql",
]

SENIORITY_HINTS = {
    "junior": ["junior", "entry level", "graduate", "new grad", "intern"],
    "mid": ["mid-level", "mid level", "intermediate", "associate"],
    "senior": ["senior", "lead", "principal", "staff", "architect", "manager"],
}


def analyze_job_description(job_description: str) -> dict[str, object]:
    cleaned_description = job_description.strip()
    lowered_description = cleaned_description.lower()

    keyword_counts: Counter[str] = Counter()
    for phrase in SKILL_PHRASES:
      pattern = _phrase_pattern(phrase)
      matches = re.findall(pattern, lowered_description)
      if matches:
          keyword_counts[_display_phrase(phrase)] += len(matches)

    suggested_keywords = [
        {
            "keyword": keyword,
            "confidence": min(0.95, 0.45 + (count * 0.1)),
        }
        for keyword, count in keyword_counts.most_common(10)
    ]

    seniority = _detect_seniority(lowered_description)
    summary = _build_summary(cleaned_description, [item["keyword"] for item in suggested_keywords])
    score = min(100, len(suggested_keywords) * 10 + (15 if seniority != "unspecified" else 0))

    return {
        "summary": summary,
        "suggested_keywords": suggested_keywords,
        "seniority": seniority,
        "score": score,
    }


def _phrase_pattern(phrase: str) -> str:
    escaped_phrase = re.escape(phrase).replace(r"\ ", r"\s+")
    return rf"\b{escaped_phrase}\b"


def _display_phrase(phrase: str) -> str:
    if phrase == "ci/cd":
        return "CI/CD"
    if phrase == "rest api":
        return "REST API"
    if phrase == "next.js":
        return "Next.js"
    if phrase == "node.js":
        return "Node.js"
    if phrase == "power bi":
        return "Power BI"
    if phrase == "scikit-learn":
        return "scikit-learn"
    if phrase == "sql":
        return "SQL"
    if phrase == "aws":
        return "AWS"
    if phrase == "gcp":
        return "GCP"
    if phrase == "llm":
        return "LLM"
    return phrase.title()


def _detect_seniority(description: str) -> str:
    for label, hints in SENIORITY_HINTS.items():
        if any(hint in description for hint in hints):
            return label
    return "unspecified"


def _build_summary(description: str, keywords: list[str]) -> str:
    if keywords:
        focus = ", ".join(keywords[:5])
        return f"The role appears to center on {focus}."

    first_sentence = re.split(r"(?<=[.!?])\s+", description, maxsplit=1)[0].strip()
    if not first_sentence:
        return "No clear summary could be extracted from the description."

    return first_sentence[:220]