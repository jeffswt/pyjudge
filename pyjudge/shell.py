import os
import json
import optparse

from . import compiler
from . import judger
from . import table
from . import visualize

__version = '20221026-dev'

opts = optparse.OptionParser(usage='pyjudge [OPTIONS]', version=__version)

opts.add_option('-i', '--input',
                dest='input', type='string', default='',
                help='Standard input to code')
opts.add_option('--input-type',
                dest='input_type', type='string', default='',
                help='Force type of the standard input (Python/File...)')
opts.add_option('-o', '--output',
                dest='output', type='string', default='',
                help='Standard output to be compared')
opts.add_option('--output-type',
                dest='output_type', type='string', default='',
                help='Force type of the standard output (C++/Python/File...)')
opts.add_option('-c', '--code',
                dest='code', type='string', default='',
                help='File of the user\'s code')
opts.add_option('--code-type',
                dest='code_type', type='string', default='',
                help='Type of the user\'s code (C/C++/Python...)')
opts.add_option('-x', '--count',
                dest='count', type='int', default=1,
                help='Iterations of judging')
opts.add_option('-t', '--time-limit',
                dest='time_limit', type='int', default=1000,
                help='Time limit of execution (ms)')
opts.add_option('-m', '--memory-limit',
                dest='memory_limit', type='int', default=512*1024*1024,
                help='Memory limit of execution (bytes)')
opts.add_option('-s', '--seed',
                dest='seed', type='int', default=0,
                help='Force random seed')
opts.add_option('-j', '--json-output',
                dest='json_output_file', type='string', default='./results.json',
                help='Output location of exact results in JSON')
opts.add_option('--json-no-io',
                dest='json_export_io', action='store_false', default=True,
                help='Do not export Input/Output data in JSON')
opts.add_option('-v', '--visualize',
                dest='json_file', type='string', default='',
                help='Visualize JSON output in HTML')

commands, args = opts.parse_args()

# Main function


def main():
    if commands.json_file:
        f_handle = open(commands.json_file, 'r', encoding='utf-8')
        json_stringify = f_handle.read()
        f_handle.close()
        json_data = json.loads(json_stringify)
        html_data = visualize.create(json_data)
        # We are not using temp...
        f_handle = open('./results.html', 'w', encoding='utf-8')
        f_handle.write(html_data)
        f_handle.close()
        try:
            os.startfile('./results.html')
        except:
            os.startfile('.\\results.html')
        return 0

    # Normal actions
    try:
        if not commands.input:
            raise Exception()
        if not commands.output:
            raise Exception()
        if not commands.code:
            raise Exception()
    except:
        print('pyjudge: fatal error: arguments insufficient')
        print('judge process terminated')
        return 1

    # Compiling source codes
    print('--> Compiling source codes...')
    # print('--> Compiling input source...')
    comp_input = compiler.AdaptiveCompiler(
        commands.input,
        source_type=commands.input_type or None)
    # comp_input.compile()
    # print('... Compilation complete.')

    # print('--> Compiling standard output...')
    comp_output = compiler.AdaptiveCompiler(
        commands.output,
        source_type=commands.output_type or None)
    # comp_output.compile()
    # print('... Compilation complete.')

    # print('--> Compiling user code...')
    comp_code = compiler.AdaptiveCompiler(
        commands.code,
        source_type=commands.code_type or None)
    # comp_code.compile()
    # print('... Compilation complete.')

    # Compile files with judger
    j_worker = judger.DataComparisonJudger(
        input_handle=comp_input,
        out_handle=comp_code,
        stdout_handle=comp_output,
        seed=commands.seed)
    print('... Compilation complete.')

    # Judging results
    all_results = []
    for run_count in range(0, commands.count):
        print('--> Running judge on test #%d:' % (run_count + 1,))
        results = j_worker.judge(
            time_limit=commands.time_limit,
            memory_limit=commands.memory_limit)
        all_results.append(results)
        print('... Judge complete. Results:')
        print(results)
        continue

    # Close compilers at termination
    if not comp_input.closed():
        comp_input.close()
    if not comp_output.closed():
        comp_output.close()
    if not comp_code.closed():
        comp_code.close()

    # Print final results
    print('--> All tests done.')
    tab_inp = []
    for i in range(0, len(all_results)):
        res = all_results[i]
        tab_inp.append((i + 1, judger.status_codes[res.judge_result]))
    tab = table.Table(title='Aggregative results', data=tab_inp)
    print(tab)

    print('--> Writing results statistics to JSON...')
    json_output = {
        'pyjudge-version': __version,
        'compiler-output': {
            'input': {
                'return-code': all_results[0].input_compile_result.return_code,
                'output': all_results[0].input_compile_result.output,
            },
            'output': {
                'return-code': all_results[0].stdout_compile_result.return_code,
                'output': all_results[0].stdout_compile_result.output,
            },
            'user-code': {
                'return-code': all_results[0].out_compile_result.return_code,
                'output': all_results[0].out_compile_result.output,
            },
        },
        'judger-output': [],
    }
    show_output = commands.json_export_io != ''
    for result_id in range(0, len(all_results)):
        results = all_results[result_id]
        json_output['judger-output'].append({
            'judge-id': result_id,
            'hash': results.hash(),
            'execution-status': {
                'input': {
                    'return-code': results.input_execute_result.return_code,
                    'time': results.input_execute_result.time,
                    'memory': results.input_execute_result.memory,
                    'stdout': results.input_execute_result.stdout if commands.json_export_io else '',
                    'stderr': results.input_execute_result.stderr if commands.json_export_io else '',
                },
                'output': {
                    'return-code': results.stdout_execute_result.return_code,
                    'time': results.stdout_execute_result.time,
                    'memory': results.stdout_execute_result.memory,
                    'stdout': results.stdout_execute_result.stdout if commands.json_export_io else '',
                    'stderr': results.stdout_execute_result.stderr if commands.json_export_io else '',
                },
                'user-code': {
                    'return-code': results.out_execute_result.return_code,
                    'time': results.out_execute_result.time,
                    'memory': results.out_execute_result.memory,
                    'stdout': results.out_execute_result.stdout if commands.json_export_io else '',
                    'stderr': results.out_execute_result.stderr if commands.json_export_io else '',
                },
            },
            'judge-result': results.judge_result,
            'judge-result-str': judger.status_codes[results.judge_result],
            'display-output': commands.json_export_io != '',
        })
    json_stringify = json.dumps(
        json_output,
        indent=4,
        sort_keys=True)
    try:
        if not commands.json_output_file:
            raise
        json_handle = open(commands.json_output_file, 'w', encoding='utf-8')
        json_handle.write(json_stringify)
        json_handle.flush()
        json_handle.close()
    except:
        print('!!! Unable to write to JSON file.')
    else:
        print('... Succeeded.')
    return 0
