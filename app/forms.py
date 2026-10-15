import re

from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired, Length

MIN_LENGTH, MAX_LENGTH = 50, 10_000


def clean_whitespace(s):
    """remove spaces/tabs, trim lines, keep at most one blank line."""
    if not s:
        return s
    s = re.sub(r"[^\S\n]+", " ", s.replace("\r\n", "\n"))
    s = re.sub(r" ?\n ?", "\n", s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


class CheckForm(FlaskForm):
    text = TextAreaField(
        "Job posting text",
        filters=[clean_whitespace],
        validators=[DataRequired(), Length(min=MIN_LENGTH, max=MAX_LENGTH)],
        render_kw={"maxlength": MAX_LENGTH, "rows": 12},
    )
