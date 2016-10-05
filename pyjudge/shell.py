
import optparse

from . import compiler
from . import judger
from . import table

__version = '20161005-dev'

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
        dest='time_limit', type='float', default=1.0,
        help='Time limit of execution')
opts.add_option('-m', '--memory-limit',
        dest='memory_limit', type='int', default=0,
        help='Memory limit of execution')
opts.add_option('-s', '--seed',
        dest='seed', type='int', default=0,
        help='Force random seed')
opts.add_option('-v', '--visualize',
        dest='visualization', type='string', default='cli',
        help='Type of visualization (cli, json)')

commands, args = opts.parse_args()

# Main function

def main():
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
        exit(1)

    # Compiling source codes
    print('--> Compiling source codes...')
    # print('--> Compiling input source...')
    comp_input = compiler.AdaptiveCompiler(
        commands.input,
        source_type = commands.input_type or None)
    # comp_input.compile()
    # print('... Compilation complete.')

    # print('--> Compiling standard output...')
    comp_output = compiler.AdaptiveCompiler(
        commands.output,
        source_type = commands.output_type or None)
    # comp_output.compile()
    # print('... Compilation complete.')

    # print('--> Compiling user code...')
    comp_code = compiler.AdaptiveCompiler(
        commands.code,
        source_type = commands.code_type or None)
    # comp_code.compile()
    # print('... Compilation complete.')

    # Compile files with judger
    j_worker = judger.DataComparisonJudger(
        input_handle = comp_input,
        out_handle = comp_code,
        stdout_handle = comp_output,
        seed = commands.seed)
    print('... Compilation complete.')

    # Judging results
    all_results = []
    for run_count in range(0, commands.count):
        print('--> Running judge on test #%d:' % (run_count + 1,))
        results = j_worker.judge(
            time_limit = commands.time_limit,
            memory_limit = commands.memory_limit)
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
    return
