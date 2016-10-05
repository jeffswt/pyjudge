
import mako
import mako.template

from . import vis_html_data

def create(json_data):
    """ Create visualized HTML with JSON input in dict(). """
    data = vis_html_data.html_template_data
    if type(data) == bytes:
        data = data.decode('utf-8', 'ignore')
    data = mako.template.Template(
        text = data,
        input_encoding = 'utf-8',
        output_encoding = 'utf-8').render(
            json_data = json_data
        ).decode('utf-8')
    return data
