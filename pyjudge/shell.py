
import optparse

from . import compiler
from . import judger

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
