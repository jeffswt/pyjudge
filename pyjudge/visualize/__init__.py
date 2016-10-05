
import mako
import mako.template

def create(json_data):
    """ Create visualized HTML with JSON input in dict(). """
    f_handle_1 = open('./pyjudge/visualize/static/index.html')
    data = f_handle_1.read()
    f_handle_1.close()
    if type(data) == bytes:
        data = data.decode('utf-8', 'ignore')
    data = mako.template.Template(
        text = data,
        input_encoding = 'utf-8',
        output_encoding = 'utf-8').render(
            json_data = json_data
        ).decode('utf-8')
    return data
