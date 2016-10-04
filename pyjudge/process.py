
import subprocess
import threading
import time

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
        self.stdin = stdin
        return
    def execute(self):
        # Starting process
        proc = subprocess.Popen(self.process_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        # Marking begin timestamp
        time_begin = time.time()
        # Writing input to process
        if len(stdin) > 0:
            proc.stdin.write(self.stdin)
        # Setting time limit
        if time_limit > 0:
            def time_delimiter(time_begin, time_limit, proc):
                while True:
                    time_cur = time.time()
                    if time_cur - time.begin >= time_limit:
                        proc.kill()
                        break
                        time.sleep(0.015)
                        continue
                        return
            threading.Thread(
                target=time_delimiter,
                args=(time_begin, self.time_limit, proc)
            ).start()
        # Waiting for process to terminate
        ret_code = proc.wait()
        # Retrieving process results
        stdout = proc.stdout.read()
        stderr = proc.stderr.read()
        # Retrieving process execution time
        time_final = time.time()
        time_delta = time_final - time_begin
        # Setting final results
        final_results = {
            'time': time_delta,
            'memory': 0,
            'return_code': ret_code,
            'stdout': stdout,
            'stderr': stderr,
        }
        return final_results
    pass
