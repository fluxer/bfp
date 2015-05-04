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
""" Reformulation of try/finally statements.

Consult the developer manual for information. TODO: Add ability to sync
source code comments with developer manual sections.

"""

from nuitka.nodes.AssignNodes import (
    StatementAssignmentVariable,
    StatementReleaseVariable
)
from nuitka.nodes.ComparisonNodes import ExpressionComparisonIs
from nuitka.nodes.ConditionalNodes import StatementConditional
from nuitka.nodes.ConstantRefNodes import ExpressionConstantRef
from nuitka.nodes.StatementNodes import (
    StatementPreserveFrameException,
    StatementPublishException,
    StatementReraiseFrameException,
    StatementsSequence
)
from nuitka.nodes.TryFinallyNodes import StatementTryFinally
from nuitka.nodes.VariableRefNodes import (
    ExpressionTargetTempVariableRef,
    ExpressionTempVariableRef
)
from nuitka.utils import Utils

from .Helpers import (
    buildStatementsNode,
    getIndicatorVariables,
    makeTryFinallyStatement,
    mergeStatements,
    popBuildContext,
    popIndicatorVariable,
    pushBuildContext,
    pushIndicatorVariable
)


def buildTryFinallyNode(provider, build_tried, node, source_ref):

    if Utils.python_version < 300:
        # Prevent "continue" statements in the final blocks
        pushBuildContext("finally")
        final = buildStatementsNode(
            provider   = provider,
            nodes      = node.finalbody,
            source_ref = source_ref
        )
        popBuildContext()

        return StatementTryFinally(
            tried      = build_tried(),
            final      = final,
            public_exc = Utils.python_version >= 300, # TODO: Use below code
            source_ref = source_ref
        )
    else:
        temp_scope = provider.allocateTempScope("try_finally")

        tmp_indicator_var = provider.allocateTempVariable(
            temp_scope = temp_scope,
            name       = "unhandled_indicator"
        )

        # This makes sure, we set the indicator variables for "break",
        # "continue" and "return" exits as well to true, so we can
        # know if an exception occurred or not.
        pushIndicatorVariable(tmp_indicator_var)

        statements = (
            StatementAssignmentVariable(
                variable_ref = ExpressionTargetTempVariableRef(
                    variable   = tmp_indicator_var,
                    source_ref = source_ref.atInternal()
                ),
                source       = ExpressionConstantRef(
                    constant   = False,
                    source_ref = source_ref
                ),
                source_ref   = source_ref.atInternal()
            ),
            build_tried(),
            StatementAssignmentVariable(
                variable_ref = ExpressionTargetTempVariableRef(
                    variable   = tmp_indicator_var,
                    source_ref = source_ref.atInternal()
                ),
                source       = ExpressionConstantRef(
                    constant   = True,
                    source_ref = source_ref.atLineNumber(99)
                ),
                source_ref   = source_ref.atInternal()
            )
        )

        # Prevent "continue" statements in the final blocks, these have to
        # become "SyntaxError".
        pushBuildContext("finally")
        final = buildStatementsNode(
            provider   = provider,
            nodes      = node.finalbody,
            source_ref = source_ref
        )
        popBuildContext()

        popIndicatorVariable()

        tried = StatementsSequence(
            statements = mergeStatements(statements, allow_none = True),
            source_ref = source_ref
        )

        prelude = StatementConditional(
            condition  = ExpressionComparisonIs(
                left       = ExpressionTempVariableRef(
                    variable   = tmp_indicator_var,
                    source_ref = source_ref.atInternal()
                ),
                right      = ExpressionConstantRef(
                    constant   = False,
                    source_ref = source_ref
                ),
                source_ref = source_ref
            ),
            yes_branch = StatementsSequence(
                statements = (
                    StatementPreserveFrameException(
                        source_ref = source_ref.atInternal()
                    ),
                    StatementPublishException(
                        source_ref = source_ref.atInternal()
                    )
                ),
                source_ref = source_ref.atInternal()
            ),
            no_branch  = None,
            source_ref = source_ref.atInternal()
        )

        postlude = (
            StatementConditional(
                condition  = ExpressionComparisonIs(
                    left       = ExpressionTempVariableRef(
                        variable   = tmp_indicator_var,
                        source_ref = source_ref.atInternal()
                    ),
                    right      = ExpressionConstantRef(
                        constant   = False,
                        source_ref = source_ref
                    ),
                    source_ref = source_ref
                ),
                yes_branch = StatementsSequence(
                    statements = (
                        StatementReleaseVariable(
                            variable   = tmp_indicator_var,
                            tolerant   = False,
                            source_ref = source_ref.atInternal()
                        ),
                        StatementReraiseFrameException(
                            source_ref = source_ref.atInternal()
                        ),
                    ),
                    source_ref = source_ref.atInternal()
                ),
                no_branch  = StatementsSequence(
                    statements = (
                        StatementReleaseVariable(
                            variable   = tmp_indicator_var,
                            tolerant   = False,
                            source_ref = source_ref.atInternal()
                        ),
                    ),
                    source_ref = source_ref.atInternal()
                ),
                source_ref = source_ref.atInternal()
            ),
        )

        final = StatementsSequence(
            statements = mergeStatements(
                (
                    prelude,
                    makeTryFinallyStatement(
                        tried      = final,
                        final      = postlude,
                        source_ref = source_ref.atInternal()
                    ),
                )
            ),
            source_ref = source_ref.atInternal()
        )

        return StatementTryFinally(
            tried      = tried,
            final      = final,
            public_exc = True,
            source_ref = source_ref
        )


def makeTryFinallyIndicatorStatements(is_loop_exit, source_ref):
    statements = []

    indicator_variables = getIndicatorVariables()


    indicator_value = True

    for indicator_variable in reversed(indicator_variables):
        if indicator_variable is Ellipsis:
            break
        elif indicator_variable is not None:
            statements.append(
                StatementAssignmentVariable(
                    variable_ref = ExpressionTargetTempVariableRef(
                        variable   = indicator_variable,
                        source_ref = source_ref.atInternal()
                    ),
                    source       = ExpressionConstantRef(
                        constant   = indicator_value,
                        source_ref = source_ref
                    ),
                    source_ref   = source_ref.atInternal().atLineNumber(55)
                )
            )
        elif is_loop_exit:
            indicator_value = False

    return statements
