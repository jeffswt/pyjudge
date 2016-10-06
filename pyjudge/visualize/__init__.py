
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

def export_py_html():
    data = vis_html_data.html_template_data
    f_handle = open('template.html', 'w', encoding='utf-8')
    f_handle.write(data)
    f_handle.close()
    return

def import_py_html():
    f_handle = open('template.html', 'r', encoding='utf-8')
    data = f_handle.read()
    f_handle.close()
    data = "html_template_data = %s\n" % "\\\n  + ".join(repr(i + '\n') for i in data.split('\n'))
    f_handle = open('vis_html_data.py', 'w', encoding='utf-8')
    f_handle.write(data)
    f_handle.close()
    return
