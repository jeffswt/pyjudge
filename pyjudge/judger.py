import binascii
import copy
import hashlib
import random

from . import compiler
from . import config
from . import process
from . import table


class JudgerError(Exception):
    def __init__(self, *args):
        self.args = args
        return
    pass


class JudgerResult:
    """ Result of judger. """

    def __init__(self,
                 judge_result='IJI',
                 input_compile_result=compiler.CompilerResult(),
                 input_execute_result=process.ProcessResult(),
                 out_compile_result=compiler.CompilerResult(),
                 out_execute_result=process.ProcessResult(),
                 stdout_compile_result=compiler.CompilerResult(),
                 stdout_execute_result=process.ProcessResult()):
        self.judge_result = judge_result
        self.input_compile_result = input_compile_result
        self.input_execute_result = input_execute_result
        self.out_compile_result = out_compile_result
        self.out_execute_result = out_execute_result
        self.stdout_compile_result = stdout_compile_result
        self.stdout_execute_result = stdout_execute_result
        return

    def __repr__(self):

        def time_cast(tim):
            suf = 'ms'
            if tim >= 1000:
                tim /= 1000
                suf = 's'
                if tim >= 60:
                    tim /= 60
                    suf = 'min'
                    if tim >= 60:
                        tim /= 60
                        suf = 'h'
            return str(round(tim, 2)) + suf

        def memory_cast(mem):
            suf = 'bytes'
            if mem >= 1024:
                mem /= 1024
                suf = 'KB'
                if mem >= 1024:
                    mem /= 1024
                    suf = 'MB'
                    if mem >= 1024:
                        mem /= 1024
                        suf = 'GB'
            return str(round(mem, 2)) + suf

        def cutdown(raw_str: str):
            cutlen = 0
            if len(raw_str) > 64:
                cutlen = len(raw_str) - 64
                raw_str = raw_str[:64] + \
                    '...(omit %d characters)' % cutlen
            return raw_str

        table_list = [
            ('Judge Result', status_codes[self.judge_result]),
            ('Execution Time', time_cast(self.out_execute_result.time)),
            ('Memory Cost', memory_cast(self.out_execute_result.memory)),
            ('Return Code', self.out_execute_result.return_code),
            ('Compiler Output', self.out_compile_result.output),
        ]
        if self.judge_result == 'IJI':
            table_list += [
                ('Input Compiler', self.input_compile_result.output),
                ('Input', cutdown(self.input_execute_result.stdout)),
            ]
        elif self.judge_result in {'CE', 'AC'}:
            pass
        else:
            table_list += [
                ('Input', cutdown(self.input_execute_result.stdout)),
                ('Output', cutdown(self.out_execute_result.stdout)),
                ('Standard Output', cutdown(self.stdout_execute_result.stdout)),
            ]
        return repr(table.Table('Judge Results', table_list))
        pass

    def clone(self,
              judge_result=None,
              input_compile_result=None,
              input_execute_result=None,
              out_compile_result=None,
              out_execute_result=None,
              stdout_compile_result=None,
              stdout_execute_result=None):
        """ Create a clone of oneself, not mutating the original properties. """
        return JudgerResult(
            judge_result=copy.deepcopy(judge_result or self.judge_result),
            input_compile_result=copy.deepcopy(
                input_compile_result or self.input_compile_result),
            input_execute_result=copy.deepcopy(
                input_execute_result or self.input_execute_result),
            out_compile_result=copy.deepcopy(
                out_compile_result or self.out_compile_result),
            out_execute_result=copy.deepcopy(
                out_execute_result or self.out_execute_result),
            stdout_compile_result=copy.deepcopy(
                stdout_compile_result or self.stdout_compile_result),
            stdout_execute_result=copy.deepcopy(stdout_execute_result or self.stdout_execute_result))
        pass

    def hash(self):
        str_concat = ('random:%f | judge:%s | input:%d-%s-%f-%d-%s-%s | stdout:%d-%s-%f-%d-%s-%s | out:%d-%s-%f-%d-%s-%s' % (
            random.random(),
            self.judge_result,
            self.input_compile_result.return_code,
            self.input_compile_result.output,
            self.input_execute_result.time,
            self.input_execute_result.memory,
            self.input_execute_result.stdout,
            self.input_execute_result.stderr,
            self.stdout_compile_result.return_code,
            self.stdout_compile_result.output,
            self.stdout_execute_result.time,
            self.stdout_execute_result.memory,
            self.stdout_execute_result.stdout,
            self.stdout_execute_result.stderr,
            self.out_compile_result.return_code,
            self.out_compile_result.output,
            self.out_execute_result.time,
            self.out_execute_result.memory,
            self.out_execute_result.stdout,
            self.out_execute_result.stderr,
        )).encode('utf-8', 'ignore')
        str_hash = binascii.hexlify(hashlib.sha256(
            str_concat).digest()).decode('utf-8')
        return str_hash
    pass


status_codes = {
    'AC': 'Accepted',
    'CE': 'Compile Error',
    'WA': 'Wrong Answer',
    'RE': 'Runtime Error',
    'TLE': 'Time Limit Exceeded',
    'MLE': 'Memory Limit Exceeded',
    'OLE': 'Output Limit Exceeded',
    'PE': 'Presentation Error',
    'IJI': 'Invalid Judger Input',
}


def wrap_judger(input_class):
    class JudgerWrapper(input_class):
        def __init__(self, *args, **kwargs):
            self.__sequence = 0
            ret = input_class.__init__(self, *args, **kwargs)
            self.__sequence = 1
            return ret

        def judge(self, *args, **kwargs):
            if self.__sequence != 1:
                raise AttributeError('Judger had already been closed')
            ret = input_class.judge(self, *args, **kwargs)
            return ret

        def close(self, *args, **kwargs):
            if self.__sequence == 0:
                raise AttributeError('Judger had already been closed')
            ret = input_class.close(self, *args, **kwargs)
            self.__sequence = 0
            return ret

        def closed(self):
            return self.__sequence == 0
        pass
    return JudgerWrapper


@wrap_judger
class Judger:
    """ Base judger, always returns NotImplementedError on all actions. Extend
    this class for further functionalities.

    Additional arguments must be passed in upon __init__. judge() function upon
    call should be accustomed with limits, when necessary. It always should
    return a dict() with a JudgerResult. """

    def __init__(self):
        return

    def judge(self, *args, **kwargs):
        """ judge(...) -- Get judger result """
        raise NotImplementedError()

    def close(self):
        """ close() -- Closes all handles this judger owns executively. """
        raise NotImplementedError()
    pass


@wrap_judger
class DataComparisonJudger(Judger):
    """ Compares data between files, will raise presentation error if found
    correct answer yet incorrect formatting. Receives following arguments at
    initialization:

        input_handle : Input file handle
        out_handle : User output handle
        stdout_handle : Handle of standard output
        seed : Random seed, randomize if not given

    Used to judge I/O from local files. """

    def __init__(self,
                 input_handle=None,
                 out_handle=None,
                 stdout_handle=None,
                 seed=None):
        if not input_handle:
            raise AttributeError('Must provide input handle')
        if not out_handle:
            raise AttributeError('Must provide output handle')
        if not stdout_handle:
            raise AttributeError('Must provide standard output handle')
        # Building compilers, in case they haven't been built
        if type(input_handle) == str:
            input_handle = compiler.AdaptiveCompiler(input_handle)
            self.input_handle_is_temp = True
        else:
            self.input_handle_is_temp = False
        if type(out_handle) == str:
            out_handle = compiler.AdaptiveCompiler(out_handle)
            self.out_handle_is_temp = True
        else:
            self.out_handle_is_temp = False
        if type(stdout_handle) == str:
            stdout_handle = compiler.AdaptiveCompiler(stdout_handle)
            self.stdout_handle_is_temp = True
        else:
            self.stdout_handle_is_temp = False
        self.input_handle = input_handle
        self.out_handle = out_handle
        self.stdout_handle = stdout_handle
        self.seed = seed
        # Precompiling input
        self.j_result = JudgerResult(judge_result='AC')
        try:
            if not self.input_handle.compiled():
                self.j_result.input_compile_result = self.input_handle.compile()
        except compiler.CompilerError as err:
            self.j_result.judge_result = 'IJI'
            self.j_result.input_compile_result = compiler.CompilerResult(
                output=err.args[0])
            return
        # Precompiling stdout
        try:
            if not self.stdout_handle.compiled():
                self.j_result.stdout_compile_result = self.stdout_handle.compile()
        except compiler.CompilerError as err:
            self.j_result.judge_result = 'IJI'
            self.j_result.stdout_compile_result = compiler.CompilerResult(
                output=err.args[0])
            return
        # Precompiling user program
        try:
            if not self.out_handle.compiled():
                self.j_result.out_compile_result = self.out_handle.compile()
        except compiler.CompilerError as err:
            self.j_result.judge_result = 'CE'
            self.j_result.out_compile_result = compiler.CompilerResult(
                output=err.args[0])
            return
        # Compile success
        return

    def judge(self, time_limit=0, memory_limit=0):
        # Checking pre-compile errors:
        if self.j_result.judge_result != 'AC':
            return self.j_result.clone()
        # Running standard input
        if self.seed:
            self.j_result.input_execute_result = self.input_handle.execute(additional_args=[
                                                                           self.seed])
        else:
            self.j_result.input_execute_result = self.input_handle.execute()
        if self.j_result.input_execute_result.return_code != 0:
            return self.j_result.clone(judge_result='IJI')
        # Running standard output
        self.j_result.stdout_execute_result = self.stdout_handle.execute(
            time_limit=time_limit,
            memory_limit=memory_limit,
            stdin=self.j_result.input_execute_result.stdout + '\n'
        )
        if self.j_result.stdout_execute_result.return_code != 0:
            return self.j_result.clone(judge_result='IJI')
        # Running user program
        self.j_result.out_execute_result = self.out_handle.execute(
            time_limit=time_limit,
            memory_limit=memory_limit,
            stdin=self.j_result.input_execute_result.stdout + '\n'
        )
        # Pretended delimitations
        expected_out = self.j_result.out_execute_result
        if expected_out.time == time_limit > 0:
            return self.j_result.clone(judge_result='TLE')
        if expected_out.memory == memory_limit > 0:
            return self.j_result.clone(judge_result='MLE')
        if len(expected_out.stdout) >= config.get_config('max_output'):
            return self.j_result.clone(judge_result='OLE')
        if len(expected_out.stderr) >= config.get_config('max_output'):
            return self.j_result.clone(judge_result='OLE')
        if expected_out.return_code != 0:
            return self.j_result.clone(judge_result='RE')
        # Done delimitating, now checking result

        def __strip_down(s_in, flag):
            lout = list()
            for i in s_in:
                if len(i) <= 0:
                    continue
                lin = i.split(flag)
                for j in lin:
                    if len(j) > 0:
                        lout.append(j)
                continue
            return lout

        def __strip_down_all(s_in):
            s_in = [s_in]
            for i in ' \t\r\n':
                s_in = __strip_down(s_in, i)
            return s_in
        out_s = self.j_result.out_execute_result.stdout
        stdout_s = self.j_result.stdout_execute_result.stdout
        out_l = __strip_down_all(out_s)
        stdout_l = __strip_down_all(stdout_s)
        if out_l != stdout_l:
            return self.j_result.clone(judge_result='WA')
        # Answer correct, checking presentation errors
        check_presentation_errors = False
        if check_presentation_errors:
            if out_s != stdout_s:
                return self.j_result.clone(judge_result='PE')
        return self.j_result.clone()

    def close(self):
        if not self.input_handle.closed() and self.input_handle_is_temp:
            self.input_handle.close()
        if not self.out_handle.closed() and self.out_handle_is_temp:
            self.out_handle.close()
        if not self.stdout_handle.closed() and self.stdout_handle_is_temp:
            self.stdout_handle.close()
        return
    pass
