
import mako
import mako.template

from . import vis_html_data

html_template_data_main = r"""
<body class="hold-transition skin-blue sidebar-mini">
<div id="container-mainframe" class="animated">
    <section class="content-header">
        <h1>pyJudge Aggregative Results<small>${json_data['pyjudge-version']}</small></h1>
        <ol class="breadcrumb"><li class="active">Results</li></ol>
    </section>
    <section class="content"><div class="row"><div class="col-md-12">
        <div class="nav-tabs-custom">
            <ul class="nav nav-tabs">
                <li class="active"><a href="#compiler" data-toggle="tab">Compiler</a></li>
                % for test in json_data['judger-output']:
                <li><a href="#test-${test['judge-id']}" data-toggle="tab">Test #${test['judge-id'] + 1}</a></li>
                % endfor
            </ul>
            <div class="tab-content">
                <div class="active tab-pane" id="compiler">
                    <div class="form-horizontal"><div class="form-group">
                        <label class="col-sm-2 control-label">Input / Compiler Return Code</label>
                        <div class="col-sm-10"><input class="form-control" value="${json_data['compiler-output']['input']['return-code']}"></div>
                    </div></div>
                    % if len(json_data['compiler-output']['input']['output']) > 1:
                    <div class="form-horizontal"><div class="form-group">
                        <label class="col-sm-2 control-label">Input / Compiler Output</label>
                        <div class="col-sm-10"><textarea class="form-control" style="font-family: Consolas; height: 150px; resize: none;">${json_data['compiler-output']['input']['output']}</textarea></div>
                    </div></div>
                    % endif
                    <div class="form-horizontal"><div class="form-group">
                        <label class="col-sm-2 control-label">Standard Output / Compiler Return Code</label>
                        <div class="col-sm-10"><input class="form-control" value="${json_data['compiler-output']['output']['return-code']}"></div>
                    </div></div>
                    % if len(json_data['compiler-output']['output']['output']) > 1:
                    <div class="form-horizontal"><div class="form-group">
                        <label class="col-sm-2 control-label">Standard Output / Compiler Output</label>
                        <div class="col-sm-10"><textarea class="form-control" style="font-family: Consolas; height: 150px; resize: none;">${json_data['compiler-output']['output']['output']}</textarea></div>
                    </div></div>
                    % endif
                    <div class="form-horizontal"><div class="form-group">
                        <label class="col-sm-2 control-label">Output / Compiler Return Code</label>
                        <div class="col-sm-10"><input class="form-control" value="${json_data['compiler-output']['user-code']['return-code']}"></div>
                    </div></div>
                    % if len(json_data['compiler-output']['user-code']['output']) > 1:
                    <div class="form-horizontal"><div class="form-group">
                        <label class="col-sm-2 control-label">Output / Compiler Output</label>
                        <div class="col-sm-10"><textarea class="form-control" style="font-family: Consolas; height: 150px; resize: none;">${json_data['compiler-output']['user-code']['output']}</textarea></div>
                    </div></div>
                    % endif
                    % for test in json_data['judger-output']:
                    <div class="form-horizontal"><div class="form-group">
                        <label class="col-sm-2 control-label">Test #${test['judge-id'] + 1} Results</label>
                        <div class="col-sm-10"><input class="form-control" value="${test['judge-result-str']}"></div>
                    </div></div>
                    % endfor
                </div>
                % for test in json_data['judger-output']:
                <div class="tab-pane" id="test-${test['judge-id']}">
                    <div class="form-horizontal"><div class="form-group">
                        <label class="col-sm-2 control-label">Status</label>
                        <div class="col-sm-10"><input class="form-control" value="${test['judge-result-str']}"></div>
                    </div></div>
                    <div class="form-horizontal"><div class="form-group">
                        <label class="col-sm-2 control-label">Time Cost</label>
                        <div class="col-sm-10"><input class="form-control" value="User: ${int(test['execution-status']['user-code']['time'] * 1000)} ms / Std: ${int(test['execution-status']['output']['time'] * 1000)} ms"></div>
                    </div></div>
                    <div class="form-horizontal"><div class="form-group">
                        <label class="col-sm-2 control-label">Memory Cost</label>
                        <div class="col-sm-10"><input class="form-control" value="User: ${int(test['execution-status']['user-code']['memory'] / 1024)} KB / Std: ${int(test['execution-status']['output']['memory'] / 1024)} KB"></div>
                    </div></div>
                    <div class="form-horizontal"><div class="form-group">
                        <label class="col-sm-2 control-label">Case Hash</label>
                        <div class="col-sm-10"><input class="form-control" value="${test['hash']}"></div>
                    </div></div>
                    % if test['display-output']:
                    <div class="row">
<%
s_stdout = test['execution-status']['output']['stdout']
s_userout = test['execution-status']['user-code']['stdout']
s_stdin = test['execution-status']['input']['stdout']
test['execution-status']['input']['stdout'] = s_stdout
test['execution-status']['user-code']['stdout'] = s_userout
test['execution-status']['output']['stdout'] = s_stdin
%>
                        <div class="col-sm-4">
                            <h4><b>Input</b></h4>
                            <textarea style="font-family: Consolas; resize: none; width: 100%; height: 1000px;">${test['execution-status']['input']['stdout']}</textarea>
                        </div>
                        <div class="col-sm-4">
                            <h4><b>User Output</b></h4>
                            <textarea style="font-family: Consolas; resize: none; width: 100%; height: 1000px;">${test['execution-status']['user-code']['stdout']}</textarea>
                        </div>
                        <div class="col-sm-4">
                            <h4><b>Standard Output</b></h4>
                            <textarea style="font-family: Consolas; resize: none; width: 100%; height: 1000px;">${test['execution-status']['output']['stdout']}</textarea>
                        </div>
                    </div>
                    % endif
                </div>
                % endfor
            </div>
        </div>
    </div></div></section>
</div>
"""


def create(json_data):
    """ Create visualized HTML with JSON input in dict(). """
    data = html_template_data_main
    if type(data) == bytes:
        data = data.decode('utf-8', 'ignore')
    data = mako.template.Template(
        text=data,
        input_encoding='utf-8').render(
            json_data=json_data
    )
    data = vis_html_data.html_template_data_begin + \
        data + vis_html_data.html_template_data_end
    return data
