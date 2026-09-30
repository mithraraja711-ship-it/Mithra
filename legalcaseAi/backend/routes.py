from fastapi import APIRouter, Response
from pydantic import BaseModel
from io import BytesIO

router = APIRouter()


class GenerateRequest(BaseModel):
    document_type: str
    parties: str
    terms: str
    effective_date: str


class ExportRequest(BaseModel):
    content: str
    document_type: str
    parties: str
    effective_date: str
    terms: str


@router.post("/generate")
def generate_document(request: GenerateRequest):

    terms_list = [
        term.strip()
        for term in request.terms.split(";")
        if term.strip()
    ]

    clauses = ""

    for index, term in enumerate(terms_list, start=1):
        clauses += f"{index}. {term}\n\n"

    document = f"""
{request.document_type.upper()}

Effective Date: {request.effective_date}

PARTIES

{request.parties}

TERMS AND CONDITIONS

{clauses}

GENERAL PROVISIONS

1. The parties agree to comply with the terms and conditions
   stated in this agreement.

2. Any amendment to this agreement should be made in writing
   and agreed to by the parties.

3. If any provision of this agreement is found to be invalid,
   the remaining provisions shall continue to apply.

SIGNATURES

Party 1:

Name: ______________________________

Signature: _________________________

Date: ______________________________

Party 2:

Name: ______________________________

Signature: _________________________

Date: ______________________________

IMPORTANT NOTICE

This document is an AI-assisted draft and should be reviewed
by a qualified legal professional before signing or relying
upon it.
"""

    return {
        "content": document.strip()
    }


@router.post("/export/txt")
def export_txt(request: ExportRequest):
    return Response(
        content=request.content,
        media_type="text/plain",
        headers={
            "Content-Disposition": 'attachment; filename="LegalEase.txt"'
        }
    )


@router.post("/export/docx")
def export_docx(request: ExportRequest):
    from docx import Document

    doc = Document()

    for line in request.content.splitlines():
        doc.add_paragraph(line)

    buffer = BytesIO()
    doc.save(buffer)

    return Response(
        content=buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": 'attachment; filename="LegalEase.docx"'
        }
    )


@router.post("/export/pdf")
def export_pdf(request: ExportRequest):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import simpleSplit

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter
    y = height - 50

    for line in request.content.splitlines():
        wrapped_lines = simpleSplit(
            line,
            "Helvetica",
            10,
            width - 80
        )

        for wrapped in wrapped_lines:
            if y < 50:
                pdf.showPage()
                y = height - 50

            pdf.drawString(40, y, wrapped)
            y -= 14

    pdf.save()

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="LegalEase.pdf"'
        }
    )