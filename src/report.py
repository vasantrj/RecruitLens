from fpdf import FPDF

def _clean(text: str) -> str:
    """Replace unicode chars unsupported by core fonts."""
    return (str(text)
            .replace("\u2014", "-")   # em dash
            .replace("\u2013", "-")   # en dash
            .replace("\u2011", "-")   # ← FIX: non-breaking hyphen
            .replace("\u2019", "'")   # right single quote
            .replace("\u2018", "'")   # left single quote
            .replace("\u201c", '"')   # left double quote
            .replace("\u201d", '"')   # right double quote
            .replace("\u2022", "*")   # bullet
            .replace("\u202f", " ")   # narrow no-break space
            .replace("\xa0", " ")     # non-breaking space
           )

def generate_report(parsed: dict, prediction: str, skills: list,
                    score: float, missing: list, feedback: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 180, 140)
    pdf.cell(0, 12, "RecruitLens AI - Candidate Report", ln=True)
    pdf.set_draw_color(0, 180, 140)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    def section(title):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(0, 180, 140)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_text_color(40, 40, 40)
        pdf.set_font("Helvetica", size=10)

    def row(label, value):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(45, 7, label)
        pdf.set_font("Helvetica", size=10)
        pdf.set_text_color(20, 20, 20)
        pdf.cell(0, 7, _clean(value), ln=True)

    section("CANDIDATE INFO")
    row("Name:",       parsed.get("name", "N/A"))
    row("Email:",      parsed.get("email", "N/A"))
    row("Phone:",      parsed.get("phone", "N/A"))
    row("Experience:", parsed.get("experience", "N/A"))
    pdf.ln(4)

    section("RESUME CATEGORY")
    row("Predicted:", prediction)
    pdf.ln(4)

    section("JOB MATCH SCORE")
    row("Score:", f"{score}%")
    pdf.ln(4)

    section("EXTRACTED SKILLS")
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 7, _clean(", ".join(skills) if skills else "None detected"))
    pdf.ln(4)

    section("MISSING SKILLS")
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 7, _clean(", ".join(missing) if missing else "None - all skills present"))
    pdf.ln(4)

    section("AI RECRUITER FEEDBACK")
    pdf.set_font("Helvetica", size=10)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 7, _clean(feedback if feedback else "Not generated"))

    # return bytes(pdf.output())
    return pdf.output(dest='S').encode('latin1')