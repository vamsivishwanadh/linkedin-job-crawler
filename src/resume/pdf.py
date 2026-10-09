from __future__ import annotations

from pathlib import Path

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

from src.resume.models import TailoredResume


def render_resume_pdf(tailored: TailoredResume, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ResumeTitle",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=6,
        alignment=TA_LEFT,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=4,
        alignment=TA_LEFT,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        alignment=TA_LEFT,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=12,
        bulletIndent=0,
    )

    story: list = []
    contact_bits = []
    c = tailored.contact
    if c.name:
        contact_bits.append(c.name)
    if c.email:
        contact_bits.append(c.email)
    if c.phone:
        contact_bits.append(c.phone)
    if c.location:
        contact_bits.append(c.location)
    if c.linkedin:
        contact_bits.append(c.linkedin)
    if contact_bits:
        story.append(Paragraph(" | ".join(contact_bits), body_style))
        story.append(Spacer(1, 8))

    if tailored.summary:
        story.append(Paragraph("Professional Summary", heading_style))
        story.append(Paragraph(_escape(tailored.summary), body_style))

    if tailored.skills:
        story.append(Paragraph("Technical Skills", heading_style))
        story.append(Paragraph(_escape(", ".join(tailored.skills)), body_style))

    if tailored.experience:
        story.append(Paragraph("Professional Experience", heading_style))
        for entry in tailored.experience:
            header = f"<b>{_escape(entry.title)}</b> — {_escape(entry.company)}"
            if entry.location:
                header += f" ({_escape(entry.location)})"
            dates = entry.start_date
            if entry.end_date:
                dates = f"{entry.start_date} – {entry.end_date}"
            story.append(Paragraph(f"{header} | {_escape(dates)}", body_style))
            if entry.bullets:
                items = [
                    ListItem(Paragraph(_escape(b.text), bullet_style))
                    for b in entry.bullets
                ]
                story.append(ListFlowable(items, bulletType="bullet", start="•"))
            story.append(Spacer(1, 6))

    if tailored.projects:
        story.append(Paragraph("Relevant Projects", heading_style))
        for project in tailored.projects:
            story.append(Paragraph(f"<b>{_escape(project.name)}</b>", body_style))
            if project.bullets:
                items = [
                    ListItem(Paragraph(_escape(b.text), bullet_style))
                    for b in project.bullets
                ]
                story.append(ListFlowable(items, bulletType="bullet", start="•"))

    if tailored.education:
        story.append(Paragraph("Education", heading_style))
        for edu in tailored.education:
            line = _escape(edu.institution)
            if edu.degree:
                line += f" — {_escape(edu.degree)}"
            if edu.dates:
                line += f" ({_escape(edu.dates)})"
            story.append(Paragraph(line, body_style))
            if edu.details:
                story.append(Paragraph(_escape(edu.details), body_style))

    if tailored.certifications:
        story.append(Paragraph("Certifications", heading_style))
        for cert in tailored.certifications:
            story.append(Paragraph(f"• {_escape(cert)}", body_style))

    doc.build(story)


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
