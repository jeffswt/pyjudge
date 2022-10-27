import concurrent.futures
import subprocess
import psutil
import time
import sys
import os

from . import table

# http://stackoverflow.com/questions/24130623/using-python-subprocess-popen-cant-prevent-exe-stopped-working-prompt
if sys.platform.startswith('win'):
    import ctypes
    SEM_NOGPFAULTERRORBOX = 0x0002  # From MSDN
    ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
    CREATE_NO_WINDOW = 0x08000000  # From Windows API
    platform_subprocess_flags = CREATE_NO_WINDOW
else:
    platform_subprocess_flags = 0


class ProcessResult:
    """ Result of process execution. """

    def __init__(self,
                 time=0,
                 memory=0,
                 return_code=1,
                 stdout='',
                 stderr=''):
        self.time = time
        self.memory = memory
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        return

    def __repr__(self):
        return repr(table.Table('Process Execution Results', [
            ('Execution Time', self.time),
            ('Memory Cost', self.memory),
            ('Return Code', self.return_code),
            ('STDOUT Output', self.stdout),
            ('STDERR Output', self.stderr),
        ]))
    pass


class Process:
    """ One-off process execution, when invoked with the following arguments,
    it returns the execution results in corresponding relevances.

        time_limit: Execution time limit in seconds. If set to zero, this means
                that there will be no time limit.
        memory_limit: Memory limit of execution in bytes. If set to zero, this
                means that there will be no memory limit.
        process_args: Arguments to be passed to process creation.
        stdin: The standard input to be injected to subprocess, default to none.

    The return value should be a dictionary, containing the following elements:

        time: Cost of time of execution in seconds.
        memory: Cost of memory in bytes.
        return_code: The return code of the program. 0 if succeeded.
        stdout: Standard output.
        stderr: Error output.

    The process would **NOT** be called interactively. """

    def __init__(self,
                 time_limit=0,
                 memory_limit=64*1024*1024*1024,
                 process_args=[],
                 stdin=''):
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.process_args = process_args
        if type(stdin) == bytes:
            self.stdin = stdin
        else:
            self.stdin = stdin.encode('utf-8')
        return

    def execute(self):
        # Starting process
        proc = subprocess.Popen(self.process_args,
                                creationflags=platform_subprocess_flags,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        # Marking begin timestamp
        time_begin = time.perf_counter_ns()
        # Setting time limit and memory limit
        thread_kill = [False, None]
        total_memory = 0

        def delimiter(time_begin, time_limit, memory_limit, proc, thread_kill):
            ps_proc = psutil.Process(proc.pid)
            total_memory = 0
            while True:
                time_cur = time.perf_counter_ns()
                try:
                    total_memory = max(total_memory, ps_proc.memory_info().rss)
                except(psutil.NoSuchProcess):
                    break
                # time.sleep(0.015)
                # This might delay a few seconds...
                if time_limit > 0 and time_cur - time_begin >= time_limit * 1000000:
                    thread_kill[1] = 'TLE'
                    proc.kill()
                    break
                if memory_limit > 0 and total_memory >= memory_limit:
                    thread_kill[1] = 'MLE'
                    proc.kill()
                    break
                # Force termination
                if thread_kill[0]:
                    break
                continue
            return total_memory

        future = concurrent.futures.ThreadPoolExecutor(max_workers=1).submit(delimiter, time_begin, self.time_limit,
                                                                             self.memory_limit, proc, thread_kill)
       # Inputting and waiting for process to terminate
        try:
            stdout, stderr = proc.communicate(input=self.stdin)
        except Exception:
            stdout = b''
            stderr = b''
        ret_code = proc.wait()
        thread_kill[0] = True
        total_memory = future.result()
        # Retrieving process execution time
        time_final = time.perf_counter_ns()
        time_delta = (time_final - time_begin) // 1000000
        # Exceptions on runtime...
        if thread_kill[1] == 'TLE':
            time_delta = self.time_limit
        if thread_kill[1] == 'MLE':
            total_memory = self.memory_limit
        # Retrieving process results (BINARY!)
        # Setting final results
        final_results = ProcessResult(
            time=time_delta,
            memory=total_memory,
            return_code=ret_code,
            stdout=stdout.decode('utf-8', 'ignore'),
            stderr=stderr.decode('utf-8', 'ignore'),
        )
        return final_results
    pass
