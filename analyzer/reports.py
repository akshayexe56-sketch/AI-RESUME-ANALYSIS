import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(analysis):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#1E40AF'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#6B7280'),
        spaceAfter=15
    )
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#1F2937'),
        spaceBefore=12,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        leading=14
    )
    notice_style = ParagraphStyle(
        'AdvisoryNotice',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        textColor=colors.HexColor('#9CA3AF'),
        leading=12
    )

    elements = []

    elements.append(Paragraph("ResumeAI - Evaluation & ATS Audit Report", title_style))
    elements.append(Paragraph(f"Candidate: <b>{analysis.user.username}</b> &nbsp;|&nbsp; File: <b>{analysis.original_filename}</b> &nbsp;|&nbsp; Analyzed on: {analysis.created_at.strftime('%B %d, %Y')}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E5E7EB'), spaceAfter=15))

    # Summary Score Table
    score_data = [
        [
            Paragraph(f"<font size=28 color='#1E40AF'><b>{analysis.overall_score}</b>/100</font><br/><b>Overall Score</b>", styles['Normal']),
            Paragraph(f"<font size=28 color='#10B981'><b>{analysis.ats_compatibility}%</b></font><br/><b>ATS Compatibility</b>", styles['Normal']),
            Paragraph(f"Skills: <b>{analysis.skills_score}%</b><br/>Experience: <b>{analysis.experience_score}%</b><br/>Education: <b>{analysis.education_score}%</b>", styles['Normal']),
            Paragraph(f"Formatting: <b>{analysis.formatting_score}%</b><br/>Keywords: <b>{analysis.keywords_score}%</b>", styles['Normal']),
        ]
    ]
    t = Table(score_data, colWidths=[130, 130, 140, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 15))

    # Skills Section
    elements.append(Paragraph("Identified Key Skills", h2_style))
    skills_text = ", ".join(analysis.skills_found) if analysis.skills_found else "No standard technical skills detected."
    elements.append(Paragraph(skills_text, body_style))
    elements.append(Spacer(1, 10))

    if analysis.missing_skills:
        elements.append(Paragraph("Missing Job Description Keywords", h2_style))
        missing_text = ", ".join(analysis.missing_skills)
        elements.append(Paragraph(f"<font color='#DC2626'>{missing_text}</font>", body_style))
        elements.append(Spacer(1, 10))

    # ATS Checks Table
    elements.append(Paragraph("ATS System Verification Checks", h2_style))
    checks_rows = [["Audit Criterion", "Status", "Evaluation Details"]]
    for chk in analysis.ats_checks:
        status_text = "PASS" if chk.get('passed') else "ATTENTION"
        checks_rows.append([
            chk.get('title', ''),
            status_text,
            chk.get('details', '')
        ])
    ctable = Table(checks_rows, colWidths=[150, 80, 310])
    ctable.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E40AF')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(ctable)
    elements.append(Spacer(1, 15))

    # Grounded Recommendations
    elements.append(Paragraph("Targeted Actionable Recommendations", h2_style))
    for rec in analysis.recommendations:
        elements.append(Paragraph(f"• <b>[{rec.get('category')}] ({rec.get('severity')})</b>: {rec.get('text')}", body_style))
        elements.append(Spacer(1, 4))

    elements.append(Spacer(1, 15))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#D1D5DB'), spaceAfter=8))
    elements.append(Paragraph("Advisory Notice: ResumeAI scores and checks are advisory evaluations designed to support your application strategy, not official scores from proprietary employer ATS vendors.", notice_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
