
# pyJudge

Input and output judger for OIers and *For Humans™*.

This project aims at creating an extensible interface for judging OI programs
with Python, universally compatible at all platforms, i.e. Linux and Windows
<del>and macOS</del>. All interfaces should be reusable and universally
compatible, emulating down to simple functions.

A command line interface is provided for rapid invocation of this module, while
a Python library is also made available to those who wish to create Online
Judges or Offline Judges with this module.

## Installation

Copy the `pyjudge` folder to `%PYTHON3_PATH%/Lib/site-packages`.

Copy the content inside `Scripts` folder to `%PYTHON3_PATH%/Scripts`, if you are
a Windows user. Otherwise think of a way to invoke `pyjudge.shell.main()` with
a bash script or cmdlet.

We haven't generated a Python wheel by now, so only manual installation is
possible until now.

## Configuring

Users may set the configurations manually through editing the source code, they
may also change the configuration through the following snippet or similar:

```Python
import pyjudge
import pyjudge.config

pyjudge.config.set_config('gcc_args', None) # Disable GCC
```

These are a list of available configurations that may be used throughout the
execution of pyJudge:

| Parameter           | Purpose                                                                       |
|:--------------------|:------------------------------------------------------------------------------|
| tmp_dir             | Temporary directory for storing one-off files, e.g. G++ compiled executables. |
| max_output          | Maximum allowed output size, not implemented yet.                             |
| table_max_lines     | Maximum allowed lines in `table.Table` display, truncated when exceeded.      |
| table_max_linewidth | Maximum allowed line width in `table.Table` display, truncated when exceeded. |
| gcc_args            | Arguments to invoke GCC Compiler, given in `list()`.                          |
| g++_args            | Arguments to invoke G++ Compiler, given in `list()`.                          |
| fpc_args            | Arguments passed to Free Pascal Compiler, given in `list()`.                  |
| python2_args        | Arguments to invoke Python 2 intepreter, given in `list()`.                   |
| python3_args        | Arguments to invoke Python 3 intepreter, given in `list()`.                   |
| javac_args          | Arguments to invoke Java Compiler, given in `list()`.                         |

## Compiler interface

The following code describes a basic compiler, where people are suggested to use
the decorator `@pyjudge.compiler.wrap_compiler`. This would take care of
sequential disorder (e.g. Executing before compiling), repeated compiling and
status checks. Inherit your compiler under this base compiler.

```Python
@wrap_compiler
class Compiler:
    def __init__(self, source_path):
        return
    def compile(self, override_command=None):
        """ compile() -- Compile the source code into executable. """
    def execute(self, additional_args=[], **kwargs):
        """ execute() -- Execute compiled executable. """
    def close(self):
        """ close() -- Remove compiled executable. """
    pass
```

There are also a few compilers ready to use, while they are all callable through
the combinative compiler `AdaptiveCompiler`, that automatically detects the
input and sends it to the corresponding compiler.

  * **FileHandleCompiler**: Reads files. Commonly used in de-facto CCF standard
    `.in` and `.out` files.
  * **DirectoryFilesCompiler**: Reads typical `.in` and `.out` files inside
    large directories, where the files follow the `problem1.in` format.
  * **Python2Compiler**, **Python3Compiler**: Interprets Python code according
    to language version. Version is not detected automatically, and has to be
    specified forcefully by the user.
  * **CCompiler**, **CppCompiler**: Compiles C/C++ code with GCC/G++ according
    to language type. Detects language through file extensions.
  * **ExecutableCompiler**: Wraps an executable like a compiler.
  * **AdaptiveCompiler**: Wraps all known compilers (must be specified) with
    automatic language detection upon initialization.

Users may define new compilers by their own. These are unimplemented compilers
that awaits implementation:

  * **JavaCompiler**: Compiles Java code and executes bytecode.
  * **PascalCompiler**: Compiles PASCAL code and executes. This is deprecated
    as support for PASCAL would be dropped officially by CCF around 2018.

Compilers also have their specific return values. They should use CompilerResult
as their results. Detailed information should be looked up in Python `help()`.

## Judger Interface

These status codes are standards in the OI realm:

  * AC: Accepted
  * CE: Compile Error
  * WA: Wrong Answer
  * RE: Runtime Error
  * TLE: Time Limit Exceeded
  * MLE: Memory Limit Exceeded
  * OLE: Output Limit Exceeded
  * PE: Presentation Error

These status codes are defined in pyJudge for ease of coding:

  * IJI: Invalid Judger Input

Judgers should return those values as results inside their JudgerResult. These
return values seem more compilicated than regular functions, but are sufficient
to contain hierarchical information with clarity. Details could be found in
Python `help()`.

Implementations must be taken care of. This is a base judger, of which all
other judgers derive from. `@pyjudge.judger.wrap_judger` is encouraged to be
used at all judgers due to its automatic management on sequential disorders
and invalid input. Inherit your judger from the base judger when creating new
classes.

```Python
@wrap_judger
class Judger:
    def __init__(self):
        return
    def judge(self, *args, **kwargs):
        """ judge(...) -- Get judger result """
    def close(self):
        """ close() -- Closes all handles this judger owns executively. """
        raise NotImplementedError()
    pass
```

These judgers have been implemented, and more are either under development or
under consideration.

  * **DataComparisonJudger**: Compares data between standard output and user
    output. Differences between whitespaces are ignored, and will not invoke
    a *Presentation Error*.

## JSON Output

The command line utility can create JSON output, from which you can visualize
the output in HTML, through the same command line utility. The hierarchy works
as follows:

```JSON
{
    "compiler-output": {
        "input": {
            "output": "g++: fatal error: no input files\ncompilation terminated.",
            "return-code": 1
        },
        "output": {
            "output": "Traceback (most recent call last):\n  File \"<stdin>\", line 2, in <module>\nKeyboardInterrupt",
            "return-code": 1
        },
        "user-code": {
            "output": "",
            "return-code": 0
        }
    },
    "judger-output": [
        {
            "display-output": false,
            "execution-status": {
                "input": {
                    "memory": 0,
                    "return-code": 0,
                    "stderr": "",
                    "stdout": "",
                    "time": 0
                },
                "output": {
                    "memory": 0,
                    "return-code": 0,
                    "stderr": "",
                    "stdout": "",
                    "time": 0
                },
                "user-code": {
                    "memory": 0,
                    "return-code": 0,
                    "stderr": "",
                    "stdout": "",
                    "time": 0.0
                }
            },
            "hash": "dabc6798ad0687fc7edca2c30fb43ec9a047a201e2d4cef21d367351242b249e",
            "judge-id": 0,
            "judge-result": "AC",
            "judge-result-str": "Accepted"
        },
    ],
    "pyjudge-version": "20161005-dev"
}
```

Specific code could be viewed inside the codes.

## HTML Visualization

Currently, this could be done in only two ways, and is not encouraged. Only
when you are lack of time and resources you are suggested to do it this way.
The following shell script could help you visualize a JSON output in no time.

```sh
pyjudge -v results.json
```

And this would output a `results.html` at the current working directory.
Nevertheless, it would also open the page for you in the browser. Screenshot
as follows:

![Visualization]('./docs/html_visualization.png')

## Command Line Interface

Use `-h` junction could invoke this:

```
Usage: pyjudge [OPTIONS]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -i INPUT, --input=INPUT
                        Standard input to code
  --input-type=INPUT_TYPE
                        Force type of the standard input (Python/File...)
  -o OUTPUT, --output=OUTPUT
                        Standard output to be compared
  --output-type=OUTPUT_TYPE
                        Force type of the standard output (C++/Python/File...)
  -c CODE, --code=CODE  File of the user's code
  --code-type=CODE_TYPE
                        Type of the user's code (C/C++/Python...)
  -x COUNT, --count=COUNT
                        Iterations of judging
  -t TIME_LIMIT, --time-limit=TIME_LIMIT
                        Time limit of execution
  -m MEMORY_LIMIT, --memory-limit=MEMORY_LIMIT
                        Memory limit of execution
  -s SEED, --seed=SEED  Force random seed
  -j JSON_OUTPUT_FILE, --json-output=JSON_OUTPUT_FILE
                        Output location of exact results in JSON
  --json-no-io          Do not export Input/Output data in JSON
  -v JSON_FILE, --visualize=JSON_FILE
                        Visualize JSON output in HTML
```
