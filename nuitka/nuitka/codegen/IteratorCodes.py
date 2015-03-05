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
""" Iteration related codes.

Next variants and unpacking with related checks.
"""

from . import CodeTemplates
from .ErrorCodes import (
    getErrorExitCode,
    getErrorExitReleaseCode,
    getReleaseCode
)
from .Indentation import indented
from .LineNumberCodes import getLineNumberUpdateCode


def getBuiltinNext1Code(to_name, value, emit, context):
    emit(
        "%s = %s;" % (
            to_name,
            "ITERATOR_NEXT( %s )" % value,
        )
    )

    getReleaseCode(
        release_name = value,
        emit         = emit,
        context      = context
    )

    getErrorExitCode(
        check_name      = to_name,
        quick_exception = "StopIteration",
        emit            = emit,
        context         = context
    )

    context.addCleanupTempName(to_name)


def getBuiltinLoopBreakNextCode(to_name, value, emit, context):
    emit(
        "%s = %s;" % (
            to_name,
            "ITERATOR_NEXT( %s )" % value,
        )
    )

    getReleaseCode(
        release_name = value,
        emit         = emit,
        context      = context
    )

    break_target = context.getLoopBreakTarget()
    if type(break_target) is tuple:
        break_indicator_code = "%s = true;" % break_target[1]
        break_target = break_target[0]
    else:
        break_indicator_code = ""

    emit(
        CodeTemplates.template_loop_break_next % {
            "to_name" : to_name,
            "break_indicator_code" : break_indicator_code,
            "break_target" : break_target,
            "release_temps"    : indented(
                getErrorExitReleaseCode(context),
                2
            ),
            "line_number_code" : indented(
                getLineNumberUpdateCode(context),
                2
            ),
            "exception_target" : context.getExceptionEscape()
        }
    )

    context.addCleanupTempName(to_name)


def getUnpackNextCode(to_name, value, count, emit, context):
    emit(
        "%s = UNPACK_NEXT( %s, %s );" % (
            to_name,
            value,
            count - 1
        )
    )

    getErrorExitCode(
        check_name      = to_name,
        quick_exception = "StopIteration",
        emit            = emit,
        context         = context
    )

    getReleaseCode(
        release_name = value,
        emit         = emit,
        context      = context
    )

    context.addCleanupTempName(to_name)


def getUnpackCheckCode(iterator_name, count, emit, context):
    # These variable cannot collide, as it's used very locally.
    attempt_name = context.allocateTempName("iterator_attempt", unique = True)

    release_code = getErrorExitReleaseCode(context)

    emit(
        CodeTemplates.template_iterator_check % {
            "iterator_name"   : iterator_name,
            "attempt_name"    : attempt_name,
            "count"           : count,
            "exception_exit"  : context.getExceptionEscape(),
            "release_temps_1" : indented(release_code, 2),
            "release_temps_2" : indented(release_code),
        }
    )

    getReleaseCode(
        release_name = iterator_name,
        emit         = emit,
        context      = context
    )
