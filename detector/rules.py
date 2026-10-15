"""Rule-based red-flag detector.

Interface used by the web app:

    check(text) -> {"score": int, "indicator": "red_flags" | "no_flags",
                    "hits": [{"rule_id", "explanation", "matched_text", "start", "end"}]}

The two rules below are a stand-in so the app works end to end
need to replace then with a full set
added some basic rules for now, will change later
"""
import re
from dataclasses import dataclass

from markupsafe import Markup, escape


@dataclass(frozen=True)
class Rule:
    id: str
    pattern: re.Pattern
    weight: int
    explanation: str


RULES = [
    Rule(
        "payment_fee",
        re.compile(r"\b(?:registration|security|training|joining)\s+(?:fee|deposit|charges?)\b", re.I),
        3,
        "Asks for a fee or deposit.",
    ),
    Rule(
        "off_platform_contact",
        re.compile(r"\b(?:wa|t)\.me/\S+|\b(?:whats\s?app|telegram)\b", re.I),
        2,
        "Moves the conversation to WhatsApp or Telegram channels.",
    ),
]
EXPLANATIONS = {r.id: r.explanation for r in RULES}
THRESHOLD = 1 


def check(text):
    hits = [
        {"rule_id": r.id, "explanation": r.explanation, "matched_text": m.group(0),
         "start": m.start(), "end": m.end()}
        for r in RULES
        for m in r.pattern.finditer(text)
    ]
    fired = {h["rule_id"] for h in hits}
    score = sum(r.weight for r in RULES if r.id in fired)
    return {"score": score, "indicator": "red_flags" if score >= THRESHOLD else "no_flags", "hits": hits}


def highlight(text, spans):
    """Return text as safe HTML with each (start, end) span wrapped in <mark>.

    The text is escaped before tags are added, so pasted HTML is never rendered.
    Overlapping spans are merged.
    """
    merged = []
    for start, end in sorted(spans):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    parts, pos = [], 0
    for start, end in merged:
        parts += [escape(text[pos:start]), Markup("<mark>"), escape(text[start:end]), Markup("</mark>")]
        pos = end
    parts.append(escape(text[pos:]))
    return Markup("").join(parts)
