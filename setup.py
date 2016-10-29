
from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name = 'pyjudge',
    version = '0.1.75',
    description = 'OI programs Judger in Python',
    long_description = 'Judge OI programs easily with pyJudge.',
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Intended Audience :: Education',
        'Programming Language :: C',
        'Programming Language :: C++',
        'Programming Language :: Pascal',
        'Programming Language :: Python',
        'Topic :: Education :: Testing',
    ],
    keywords = 'judge judger oi',
    url = 'https://github.com/ht35268/pyjudge',
    author = 'ht35268',
    author_email = '',
    license = 'GPLv3',
    packages = [
        'pyjudge',
        'pyjudge.visualize'
    ],
    install_requires = [
        'mako',
    ],
    entry_points = {
        'console_scripts': [
            'pyjudge = pyjudge.shell:main'
        ],
    },
)
