import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_company_pdf(company_data):
    """
    Generates a professional PDF dossier for a company using ReportLab.
    Returns a bytes object of the PDF.
    """
    buffer = io.BytesIO()
    
    # Page setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=24
    )
    
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    
    label_style = ParagraphStyle(
        'LabelText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569')
    )

    # Document Header
    story.append(Paragraph("PLACEMENT MANAGEMENT SYSTEM", subtitle_style))
    story.append(Paragraph(f"Company Verification Dossier: {company_data.get('company_name', 'N/A')}", title_style))
    story.append(Spacer(1, 10))
    
    # Meta / Info Box
    status_data = [
        [
            Paragraph("Approval Status", label_style),
            Paragraph(company_data.get('approval_status', 'PENDING'), body_style),
            Paragraph("Placement Status", label_style),
            Paragraph(company_data.get('placement_status', 'COLD'), body_style)
        ],
        [
            Paragraph("Submitted By", label_style),
            Paragraph(company_data.get('submitted_by', 'N/A'), body_style),
            Paragraph("Approved By", label_style),
            Paragraph(company_data.get('approved_by') or 'N/A', body_style)
        ]
    ]
    
    status_table = Table(status_data, colWidths=[110, 140, 110, 140])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
    ]))
    
    story.append(status_table)
    story.append(Spacer(1, 20))
    
    # Profile Section
    story.append(Paragraph("Company Information", h2_style))
    
    profile_data = [
        [Paragraph("Company Name", label_style), Paragraph(company_data.get('company_name', 'N/A'), body_style)],
        [Paragraph("Website", label_style), Paragraph(company_data.get('website', 'N/A'), body_style)],
        [Paragraph("Location", label_style), Paragraph(company_data.get('location', 'N/A'), body_style)],
        [Paragraph("Overview / Content", label_style), Paragraph(company_data.get('content', 'N/A'), body_style)],
        [Paragraph("HR Contact Email", label_style), Paragraph(company_data.get('hr_email', 'N/A'), body_style)],
        [Paragraph("HR Contact Phone", label_style), Paragraph(company_data.get('hr_phone', 'N/A'), body_style)],
        [Paragraph("Address", label_style), Paragraph(company_data.get('company_address', 'N/A'), body_style)]
    ]
    
    profile_table = Table(profile_data, colWidths=[130, 370])
    profile_table.setStyle(TableStyle([
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    
    story.append(profile_table)
    story.append(Spacer(1, 30))
    
    # Footer Notice
    notice_style = ParagraphStyle(
        'FooterNotice',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#94A3B8'),
        alignment=1 # Center
    )
    story.append(Paragraph("This is an automatically generated document from the college Placement Management System. Confidentiality and compliance rules apply.", notice_style))
    
    doc.build(story)
    
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_resume_match_pdf(jd_title, matches):
    """
    Generates a professional PDF compatibility report for a job description match run.
    Returns a bytes object of the PDF.
    """
    buffer = io.BytesIO()
    
    # Page setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=24
    )
    
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    
    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.white
    )
    
    # Document Header
    story.append(Paragraph("PLACEMENT MANAGEMENT SYSTEM", subtitle_style))
    story.append(Paragraph(f"Resume Compatibility Match Report: {jd_title}", title_style))
    story.append(Spacer(1, 10))
    
    # Candidates Table Header
    story.append(Paragraph("Matching Candidates List (Sorted by Score)", h2_style))
    story.append(Spacer(1, 8))
    
    table_data = [
        [
            Paragraph("Rank", header_cell_style),
            Paragraph("Student Name", header_cell_style),
            Paragraph("Reg Number", header_cell_style),
            Paragraph("Department", header_cell_style),
            Paragraph("Match Score", header_cell_style)
        ]
    ]
    
    for idx, m in enumerate(matches, 1):
        table_data.append([
            Paragraph(str(idx), body_style),
            Paragraph(m.get("student_name", "N/A"), body_style),
            Paragraph(m.get("reg_number", "N/A"), body_style),
            Paragraph(m.get("department", "N/A"), body_style),
            Paragraph(f"{m.get('score', 0)}% Match ({m.get('score_range', '0-50')})", body_style)
        ])
        
    scores_table = Table(table_data, colWidths=[40, 150, 110, 110, 90])
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4F46E5')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
    ]))
    
    story.append(scores_table)
    story.append(Spacer(1, 30))
    
    # Footer Notice
    notice_style = ParagraphStyle(
        'FooterNotice',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#94A3B8'),
        alignment=1 # Center
    )
    story.append(Paragraph("This is an automatically generated document from the college Placement Management System. Confidentiality and compliance rules apply.", notice_style))
    
    doc.build(story)
    
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_generic_report_pdf(report_type, data, meta=None):
    """
    Generates a professional PDF dossier for any tabular report layout.
    """
    if meta is None:
        meta = {}
        
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=18, leading=22,
        textColor=colors.HexColor('#1E293B'), spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=13,
        textColor=colors.HexColor('#64748B'), spaceAfter=20
    )
    h2_style = ParagraphStyle(
        'SectionHeader', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=12, leading=16,
        textColor=colors.HexColor('#0F172A'), spaceBefore=8, spaceAfter=8
    )
    body_style = ParagraphStyle(
        'BodyTextCustom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11,
        textColor=colors.HexColor('#334155')
    )
    header_cell_style = ParagraphStyle(
        'HeaderCell', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=12,
        textColor=colors.white
    )
    
    notice_style = ParagraphStyle(
        'FooterNotice',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#94A3B8'),
        alignment=1 # Center
    )

    story.append(Paragraph("PLACEMENT MANAGEMENT SYSTEM — EXPORT HUB", subtitle_style))
    
    if report_type == "student_company":
        company = meta.get("company_name", "All Companies")
        story.append(Paragraph(f"Registered Candidates Report: {company}", title_style))
        story.append(Paragraph("A list of registered/placed candidates matching the company profile.", body_style))
        story.append(Spacer(1, 10))
        
        table_data = [[
            Paragraph("Rank", header_cell_style),
            Paragraph("Student Name", header_cell_style),
            Paragraph("Reg Number", header_cell_style),
            Paragraph("Department", header_cell_style),
            Paragraph("Email", header_cell_style),
            Paragraph("Phone", header_cell_style)
        ]]
        for idx, item in enumerate(data, 1):
            table_data.append([
                Paragraph(str(idx), body_style),
                Paragraph(item.get("name", "N/A"), body_style),
                Paragraph(item.get("reg_number", "N/A"), body_style),
                Paragraph(item.get("department", "N/A"), body_style),
                Paragraph(item.get("email", "N/A"), body_style),
                Paragraph(item.get("phone", "N/A"), body_style)
            ])
        col_widths = [35, 120, 90, 80, 120, 75]
        
    elif report_type == "student_placed":
        story.append(Paragraph("Drive Selections & Package Roster Report", title_style))
        story.append(Spacer(1, 10))
        table_data = [[
            Paragraph("Rank", header_cell_style),
            Paragraph("Student Name", header_cell_style),
            Paragraph("Reg Number", header_cell_style),
            Paragraph("Department", header_cell_style),
            Paragraph("Placed Company", header_cell_style),
            Paragraph("Package (LPA)", header_cell_style)
        ]]
        for idx, item in enumerate(data, 1):
            table_data.append([
                Paragraph(str(idx), body_style),
                Paragraph(item.get("name", "N/A"), body_style),
                Paragraph(item.get("reg_number", "N/A"), body_style),
                Paragraph(item.get("department", "N/A"), body_style),
                Paragraph(item.get("placed_company", "N/A"), body_style),
                Paragraph(f"{item.get('ctc_lpa', 0.0)} LPA", body_style)
            ])
        col_widths = [35, 120, 85, 80, 120, 80]
        
    elif report_type == "student_overall":
        story.append(Paragraph("Overall Student Placement Registry Report", title_style))
        story.append(Spacer(1, 10))
        table_data = [[
            Paragraph("Rank", header_cell_style),
            Paragraph("Student Name", header_cell_style),
            Paragraph("Reg Number", header_cell_style),
            Paragraph("Department", header_cell_style),
            Paragraph("Status", header_cell_style),
            Paragraph("Company Info", header_cell_style)
        ]]
        for idx, item in enumerate(data, 1):
            status_val = item.get("placement_status", "YTPP")
            company_info = f"{item.get('placed_company', 'N/A')} ({item.get('ctc_lpa', 0.0)} LPA)" if status_val == "PLACED" else "N/A"
            table_data.append([
                Paragraph(str(idx), body_style),
                Paragraph(item.get("name", "N/A"), body_style),
                Paragraph(item.get("reg_number", "N/A"), body_style),
                Paragraph(item.get("department", "N/A"), body_style),
                Paragraph(status_val, body_style),
                Paragraph(company_info, body_style)
            ])
        col_widths = [35, 120, 85, 80, 80, 120]
        
    elif report_type == "company_pipeline":
        story.append(Paragraph("Company Pipeline Sourcing Report", title_style))
        story.append(Spacer(1, 10))
        table_data = [[
            Paragraph("No", header_cell_style),
            Paragraph("Company Name", header_cell_style),
            Paragraph("Location", header_cell_style),
            Paragraph("Verification Status", header_cell_style),
            Paragraph("Pipeline Status", header_cell_style),
            Paragraph("HR Email", header_cell_style)
        ]]
        for idx, item in enumerate(data, 1):
            table_data.append([
                Paragraph(str(idx), body_style),
                Paragraph(item.get("company_name", "N/A"), body_style),
                Paragraph(item.get("location", "N/A"), body_style),
                Paragraph(item.get("approval_status", "PENDING"), body_style),
                Paragraph(item.get("placement_status", "COLD"), body_style),
                Paragraph(item.get("hr_email", "N/A"), body_style)
            ])
        col_widths = [30, 120, 90, 90, 90, 100]
        
    elif report_type == "company_drive":
        company = meta.get("company_name", "Completed Drives")
        story.append(Paragraph(f"Campus Drive Summary Report: {company}", title_style))
        story.append(Spacer(1, 10))
        table_data = [[
            Paragraph("No", header_cell_style),
            Paragraph("Student Name", header_cell_style),
            Paragraph("Reg Number", header_cell_style),
            Paragraph("Department", header_cell_style),
            Paragraph("Phone", header_cell_style)
        ]]
        for idx, item in enumerate(data, 1):
            table_data.append([
                Paragraph(str(idx), body_style),
                Paragraph(item.get("name", "N/A"), body_style),
                Paragraph(item.get("reg_number", "N/A"), body_style),
                Paragraph(item.get("department", "N/A"), body_style),
                Paragraph(item.get("phone", "N/A"), body_style)
            ])
        col_widths = [40, 150, 110, 110, 110]
        
    else:
        story.append(Paragraph("Placement Registry Export Document", title_style))
        table_data = [[Paragraph("Data Field", header_cell_style)]]
        for item in data:
            table_data.append([Paragraph(str(item), body_style)])
        col_widths = [520]

    report_table = Table(table_data, colWidths=col_widths)
    report_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4F46E5')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
    ]))
    
    story.append(report_table)
    story.append(Spacer(1, 25))
    story.append(Paragraph("Confidential report generated from college Placement Management System. All rights reserved.", notice_style))
    
    doc.build(story)
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
