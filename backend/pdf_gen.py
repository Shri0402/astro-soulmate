"""Server-side PDF generation for Kundali reports - maroon & gold theme."""
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

MAROON = HexColor("#7A1E2C")
GOLD = HexColor("#D4AF37")
DARK_BG = HexColor("#2A0E18")
CREAM = HexColor("#F3E6C6")
TEXT = HexColor("#1A0810")


def generate_kundali_pdf(user: dict, match: dict) -> bytes:
    """Generate a multi-page maroon/gold kundali compatibility PDF."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=28, textColor=GOLD, alignment=TA_CENTER, spaceAfter=8
    )
    subtitle = ParagraphStyle(
        "subtitle", parent=styles["Normal"], fontName="Helvetica-Oblique",
        fontSize=12, textColor=MAROON, alignment=TA_CENTER, spaceAfter=24
    )
    h2 = ParagraphStyle(
        "h2", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=16, textColor=MAROON, spaceAfter=10, spaceBefore=18
    )
    body = ParagraphStyle(
        "body", parent=styles["Normal"], fontName="Helvetica",
        fontSize=11, textColor=TEXT, leading=16, alignment=TA_LEFT, spaceAfter=8
    )
    verdict_style = ParagraphStyle(
        "verdict", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=13, textColor=MAROON, leading=18, alignment=TA_CENTER,
        backColor=HexColor("#F9EFD4"), borderPadding=12, spaceAfter=16
    )

    story = []

    # Header
    story.append(Paragraph("✦ Stars Connection ✦", title_style))
    story.append(Paragraph("Kundali Compatibility Report", subtitle))

    # Score banner
    score_table = Table(
        [[Paragraph(f"<b>Ashtakoota Score</b>", body),
          Paragraph(f"<font size=22 color='#7A1E2C'><b>{match['score']} / 36</b></font>", body)]],
        colWidths=[3 * inch, 3 * inch]
    )
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CREAM),
        ("BOX", (0, 0), (-1, -1), 1.5, GOLD),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("PADDING", (0, 0), (-1, -1), 16),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 20))

    # Birth details
    story.append(Paragraph("Birth Details", h2))
    details = [
        ["Field", user.get("name", "—"), match.get("match_name", "—")],
        ["Gender", user.get("gender", "—"), match.get("match_gender", "—")],
        ["Date of Birth", user.get("dob", "—"), match.get("match_dob", "—")],
        ["Birth City", user.get("birth_city", "—"), match.get("match_city", "—")],
        ["Rashi (Moon Sign)", user.get("astro", {}).get("rashi", "—"), "—"],
        ["Nakshatra", user.get("astro", {}).get("nakshatra", "—"), "—"],
    ]
    t = Table(details, colWidths=[1.8 * inch, 2.3 * inch, 2.3 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), MAROON),
        ("TEXTCOLOR", (0, 0), (-1, 0), CREAM),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, GOLD),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, HexColor("#F9EFD4")]),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t)

    # Ashtakoota breakdown
    story.append(Paragraph("Ashtakoota - 8 Gunas Breakdown", h2))
    rows = [["Guna", "Score", "Max", "Significance"]]
    significance = {
        "Varna": "Spiritual / work compatibility",
        "Vashya": "Mutual attraction & control",
        "Tara": "Health & well-being",
        "Yoni": "Physical & sexual compatibility",
        "Graha Maitri": "Mental & psychological bond",
        "Gana": "Temperament harmony",
        "Bhakoot": "Family welfare & prosperity",
        "Nadi": "Genetic & health compatibility",
    }
    for name, data in match["breakdown"].items():
        rows.append([name, str(data["score"]), str(data["max"]), significance.get(name, "")])
    t2 = Table(rows, colWidths=[1.3 * inch, 0.7 * inch, 0.6 * inch, 3.8 * inch])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), MAROON),
        ("TEXTCOLOR", (0, 0), (-1, 0), CREAM),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, GOLD),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CREAM, HexColor("#F9EFD4")]),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t2)

    # Mangal Dosha
    story.append(Paragraph("Mangal Dosha Analysis", h2))
    mangal_text = (
        f"{user.get('name', 'You')}: "
        f"<b>{'Mangal Dosha Present' if match['mangal_a'] else 'No Mangal Dosha'}</b><br/>"
        f"{match.get('match_name', 'Partner')}: "
        f"<b>{'Mangal Dosha Present' if match['mangal_b'] else 'No Mangal Dosha'}</b>"
    )
    story.append(Paragraph(mangal_text, body))

    # Verdict
    story.append(Paragraph("Final Verdict", h2))
    story.append(Paragraph(match["verdict"], verdict_style))

    story.append(Spacer(1, 24))
    footer = ParagraphStyle(
        "footer", parent=body, fontSize=9, textColor=HexColor("#8A6B72"),
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        "Generated by Stars Connection · stars-connection.app · For guidance only",
        footer
    ))

    doc.build(story)
    return buf.getvalue()
