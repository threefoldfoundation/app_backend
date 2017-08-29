import os
import jinja2

from xhtml2pdf import pisa

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

ASSETS_FOLDER = os.path.join(os.path.dirname(__file__), 'assets')
JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader([ASSETS_FOLDER]))

def get_cna_stream():
    template_variables = {
        'logo_path': 'assets/logo.png',
        'param_1': 'A',
        'param_2': 'B',
        'param_3': 'C'
    }

    source_html = JINJA_ENVIRONMENT.get_template('assets/cna.html').render(template_variables)

    output_stream = StringIO()
    pisa.CreatePDF(src=source_html, dest=output_stream, path='%s' % ASSETS_FOLDER)
    pdf_contents = output_stream.getvalue()
    output_stream.close()

    return pdf_contents
