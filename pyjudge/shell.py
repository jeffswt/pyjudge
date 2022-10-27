import os
import json
import argparse

from . import compiler
from . import judger
from . import table
from . import visualize

__version = '20221027-dev'

parser = argparse.ArgumentParser(
    usage='pyjudge [OPTIONS]', description='A simple judger for OI/ACM.')

parser.add_argument('-i', '--input',
                    dest='input', type=str, default='',
                    help='Standard input to code')
parser.add_argument('--input-type',
                    dest='input_type', type=str, default='',
                    help='Force type of the standard input (Python/File...)')
parser.add_argument('-o', '--output',
                    dest='output', type=str, default='',
                    help='Standard output to be compared')
parser.add_argument('-io', '--test-cases',
                    dest='testcases', type=str, default='',
                    help='Folder to store Standard IO files')
parser.add_argument('--output-type',
                    dest='output_type', type=str, default='',
                    help='Force type of the standard output (C++/Python/File...)')
parser.add_argument('-c', '--code',
                    dest='code', type=str, default='',
                    help='File of the user\'s code')
parser.add_argument('--code-type',
                    dest='code_type', type=str, default='',
                    help='Type of the user\'s code (C/C++/Python...)')
parser.add_argument('-t', '--time-limit',
                    dest='time_limit', type=int, default=1000,
                    help='Time limit of execution (ms)')
parser.add_argument('-m', '--memory-limit',
                    dest='memory_limit', type=int, default=512*1024*1024,
                    help='Memory limit of execution (bytes)')
parser.add_argument('-s', '--seed',
                    dest='seed', type=int, default=0,
                    help='Force random seed')
parser.add_argument('-j', '--json-output',
                    dest='json_output_file', type=str, default='./results.json',
                    help='Output location of exact results in JSON')
parser.add_argument('--json-no-io',
                    dest='json_export_io', action='store_false', default=True,
                    help='Do not export Input/Output data in JSON')
parser.add_argument('-v', '--visualize',
                    dest='json_file', type=str, default='',
                    help='Visualize JSON output in HTML')

commands = parser.parse_args()

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
        if not commands.input and not commands.testcases:
            raise Exception()
        if not commands.output and not commands.testcases:
            raise Exception()
        if not commands.code:
            raise Exception()
    except:
        print('pyjudge: fatal error: arguments insufficient')
        print('judge process terminated')
        return 1

    # Compiling source codes
    print('--> Compiling source codes...')

    comp_code = compiler.AdaptiveCompiler(
        commands.code,
        source_type=commands.code_type or None)
    comp_code.compile()

    print('... Compilation complete.')

    # Judging results
    all_results = []
    run_count = 0
    if commands.testcases:
        for root, dirs, files in os.walk(commands.testcases):
            for name in files:
                if name.find('.in') != -1:
                    input_path = os.path.join(root, name)
                    output_path = input_path.replace('.in', '.ans')
                    if not os.path.exists(output_path):
                        output_path = input_path.replace('.in', '.out')
                    if not os.path.exists(output_path):
                        if not comp_code.closed():
                            comp_code.close()
                        print(
                            'pyjudge: fatal error: no standard output file found for standard input file %s', input_path)
                        print('judge process terminated')
                        return 1
                    print('--> Running judge on test #%d:' % (run_count + 1,))
                    comp_input = compiler.AdaptiveCompiler(
                        input_path)
                    comp_output = compiler.AdaptiveCompiler(
                        output_path)
                    j_worker = judger.DataComparisonJudger(
                        input_handle=comp_input,
                        out_handle=comp_code,
                        stdout_handle=comp_output,
                        seed=commands.seed)
                    results = j_worker.judge(
                        time_limit=commands.time_limit,
                        memory_limit=commands.memory_limit)
                    all_results.append(results)
                    run_count += 1
                    print('... Judge complete. Results:')
                    print(results)
                    if not comp_input.closed():
                        comp_input.close()
                    if not comp_output.closed():
                        comp_output.close()
    else:
        comp_input = compiler.AdaptiveCompiler(
            commands.input,
            source_type=commands.input_type or None)
        comp_output = compiler.AdaptiveCompiler(
            commands.output,
            source_type=commands.output_type or None)
        print('--> Running judge on %s', commands.code)
        j_worker = judger.DataComparisonJudger(
            input_handle=comp_input,
            out_handle=comp_code,
            stdout_handle=comp_output,
            seed=commands.seed)
        results = j_worker.judge(
            time_limit=commands.time_limit,
            memory_limit=commands.memory_limit)
        print('... Judge complete. Results:')
        print(results)
        all_results.append(results)

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
