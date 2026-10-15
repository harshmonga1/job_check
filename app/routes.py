from flask import Blueprint, current_app, redirect, render_template, url_for
from sqlalchemy import select

from app import db
from app.forms import CheckForm
from app.models import Check, RuleHit
from detector.rules import EXPLANATIONS, check, highlight

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET", "POST"])
def index():
    form = CheckForm()
    if form.validate_on_submit():
        text = form.text.data
        result = check(text)
        record = Check(
            source="form",
            text=text,
            rule_score=result["score"],
            indicator=result["indicator"],
            hits=[
                RuleHit(rule_id=h["rule_id"], matched_text=h["matched_text"],
                        span_start=h["start"], span_end=h["end"])
                for h in result["hits"]
            ],
        )
        db.session.add(record)
        db.session.commit()
        # posting text is never logged
        current_app.logger.info(
            "check id=%d source=form score=%d indicator=%s flags=%d",
            record.id, record.rule_score, record.indicator, record.flag_count,
        )
        return redirect(url_for("main.result", check_id=record.id))
    return render_template("index.html", form=form)


@bp.route("/check/<int:check_id>")
def result(check_id):
    record = db.get_or_404(Check, check_id)
    flags = {}
    for h in record.hits:
        flags.setdefault(h.rule_id, []).append(h.matched_text)
    highlighted = highlight(record.text, [(h.span_start, h.span_end) for h in record.hits])
    return render_template("result.html", check=record, flags=flags,
                           explanations=EXPLANATIONS, highlighted=highlighted)


@bp.route("/history")
def history():
    page = db.paginate(select(Check).order_by(Check.id.desc()), per_page=20)
    return render_template("history.html", page=page)
