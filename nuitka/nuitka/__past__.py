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
"""
Module like __future__ for things that are no more in CPython3,

but provide compatible fallbacks.

This is required to run the same code easily with both CPython2 and CPython3.
"""


# pylint: disable=W0622,C0103

# Work around for CPython 3.x renaming long to int.
try:
    long = long  # lint:ok
except NameError:
    long = int  # lint:ok

# Work around for CPython 3.x renaming unicode to str.
try:
    unicode = unicode  # lint:ok
except NameError:
    unicode = str  # lint:ok

# Work around for CPython 3.x removal of commands
try:
    import commands
except ImportError:
    import subprocess as commands  # lint:ok

def iterItems(d):
    try:
        return d.iteritems()
    except AttributeError:
        return d.items()

if unicode is str:
    raw_input = input
else:
    raw_input = raw_input

# pylint: disable=E0611
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve
# pylint: enable=E0611

# For PyLint to be happy.
assert long
assert unicode
assert commands
assert urlretrieve
