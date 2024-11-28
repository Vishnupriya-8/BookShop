from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

def renderPdf(template_path, context_dict):
    template = get_template(template_path)
    html = template.render(context_dict)
    result = BytesIO()
    
    try:
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            return result.getvalue()
        return None
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        return None