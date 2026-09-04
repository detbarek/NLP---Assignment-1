import re

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class TextInput(BaseModel):
    text: str


# Word-level sentiment lexicon (Danish + English), keyed by score.
POSITIVE_WORDS = {
    3: ["god", "godt", "gode", "good", "nice", "fint"],
    5: ["fantastisk", "fremragende", "excellent", "amazing", "outstanding"],
}

NEGATIVE_WORDS = {
    -3: ["dårlig", "dårligt", "bad", "dry", "tør", "kedelig", "boring"],
    -5: ["forfærdelig", "elendig", "terrible", "horrible", "awful"],
}

# Multi-word phrases, checked as substrings.
NEGATIVE_PHRASES = {
    -3: ["did not learn", "lærte ikke", "ikke lære"],
}


def score_text(text: str) -> int:
    lowered = text.lower()
    matches = []

    for score, words in POSITIVE_WORDS.items():
        for word in words:
            if re.search(r"\b" + re.escape(word) + r"\b", lowered):
                matches.append(score)

    for score, words in NEGATIVE_WORDS.items():
        for word in words:
            if re.search(r"\b" + re.escape(word) + r"\b", lowered):
                matches.append(score)

    for score, phrases in NEGATIVE_PHRASES.items():
        for phrase in phrases:
            if phrase in lowered:
                matches.append(score)

    if not matches:
        return 0

    average = sum(matches) / len(matches)
    result = round(average)
    return max(-5, min(5, result))


@app.post("/v1/sentiment")
def analyze_sentiment(input: TextInput):
    return {"score": score_text(input.text)}