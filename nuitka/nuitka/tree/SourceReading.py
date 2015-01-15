#     Copyright 2015, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
""" Read source code from files.

This is tremendously more complex than one might think, due to encoding issues
and version differences of Python.
"""

import re

from nuitka import (
    Options,
    PythonVersions,
    SourceCodeReferences,
    SyntaxErrors,
    Utils
)


def _readSourceCodeFromFilename3(source_filename):
    import tokenize

    try:
        with open(source_filename, "rb") as source_file:
            encoding = tokenize.detect_encoding(source_file.readline)[0]

            # Rewind to get the whole file.
            source_file.seek(0)

            source_code = source_file.read()

        return source_code.decode(encoding)
    except SyntaxError as e:
        if Options.isFullCompat():
            if PythonVersions.doShowUnknownEncodingName():
                match = re.match("unknown encoding for '.*?': (.*)", e.args[0])
                complaint = match.group(1)
            else:
                complaint = "with BOM"

            e.args = (
                "encoding problem: %s" % complaint,
                (source_filename, 1, None, None)
            )

            if hasattr(e, "msg"):
                e.msg = e.args[0]

        raise

def _detectEncoding2(source_file):
    # Detect the encoding.
    encoding = "ascii"

    line1 = source_file.readline()

    if line1.startswith(b'\xef\xbb\xbf'):
        encoding = "utf-8"
    else:
        line1_match = re.search(b"coding[:=]\\s*([-\\w.]+)", line1)

        if line1_match:
            encoding = line1_match.group(1)
        else:
            line2 = source_file.readline()

            line2_match = re.search(b"coding[:=]\\s*([-\\w.]+)", line2)

            if line2_match:
                encoding = line2_match.group(1)

    source_file.seek(0)

    return encoding

def _readSourceCodeFromFilename2(source_filename):
    # Detect the encoding.
    with open(source_filename, "rU") as source_file:
        encoding = _detectEncoding2(source_file)

        source_code = source_file.read()

        # Try and detect SyntaxError from missing or wrong encodings.
        if type(source_code) is not unicode and encoding == "ascii":
            try:
                _source_code = source_code.decode(encoding)
            except UnicodeDecodeError as e:
                lines = source_code.split('\n')
                so_far = 0

                for count, line in enumerate(lines):
                    so_far += len(line) + 1

                    if so_far > e.args[2]:
                        break
                else:
                    # Cannot happen, decode error implies non-empty.
                    count = -1

                wrong_byte = re.search(
                    "byte 0x([a-f0-9]{2}) in position",
                    str(e)
                ).group(1)

                SyntaxErrors.raiseSyntaxError(
                    reason       = """\
Non-ASCII character '\\x%s' in file %s on line %d, but no encoding declared; \
see http://python.org/dev/peps/pep-0263/ for details""" % (
                        wrong_byte,
                        source_filename,
                        count+1,
                    ),
                    source_ref   = SourceCodeReferences.fromFilename(
                        source_filename,
                        None
                    ).atLineNumber(count+1),
                    display_line = False
                )

    return source_code

def readSourceCodeFromFilename(source_filename):
    if Utils.python_version < 300:
        return _readSourceCodeFromFilename2(source_filename)
    else:
        return _readSourceCodeFromFilename3(source_filename)
