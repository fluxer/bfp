#     Copyright 2014, Kay Hayen, mailto:kay.hayen@gmail.com
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
""" Globals/locals/dir0/dir1 nodes

These nodes give access to variables, highly problematic, because using them,
the code may change or access anything about them, so nothing can be trusted
anymore, if we start to not know where their value goes.

"""


from .NodeBases import (
    ExpressionBuiltinSingleArgBase,
    StatementChildrenHavingBase,
    ExpressionMixin,
    NodeBase
)


class ExpressionBuiltinGlobals(NodeBase, ExpressionMixin):
    kind = "EXPRESSION_BUILTIN_GLOBALS"

    def __init__(self, source_ref):
        NodeBase.__init__( self, source_ref = source_ref )

    def computeExpression(self, constraint_collection):
        return self, None, None


class ExpressionBuiltinLocals(NodeBase, ExpressionMixin):
    kind = "EXPRESSION_BUILTIN_LOCALS"

    def __init__(self, source_ref):
        NodeBase.__init__( self, source_ref = source_ref )

    def computeExpression(self, constraint_collection):
        # Just inform the collection that all escaped.
        for variable_ref in constraint_collection.getActiveVariables():
            variable = variable_ref

            while variable.isReference():
                variable = variable.getReferenced()

            # TODO: Currently this is a bit difficult to express in a positive
            # way
            if not variable.isTempKeeperVariable() and not variable.isTempVariable():
                variable_trace = constraint_collection.getVariableCurrentTrace(
                    variable_ref
                )

                variable_trace.addUsage( self )

        return self, None, None

    def needsLocalsDict(self):
        return self.getParentVariableProvider().isEarlyClosure() and \
               ( not self.getParent().isStatementReturn() or self.getParent().isExceptionDriven() )


class StatementSetLocals(StatementChildrenHavingBase):
    kind = "STATEMENT_SET_LOCALS"

    named_children = ( "new_locals", )

    def __init__(self, new_locals, source_ref):
        StatementChildrenHavingBase.__init__(
            self,
            values     = {
                "new_locals" : new_locals,
            },
            source_ref = source_ref
        )

    def needsLocalsDict(self):
        return True

    getNewLocals = StatementChildrenHavingBase.childGetter( "new_locals" )

    def computeStatement(self, constraint_collection):
        # Make sure that we don't even assume "unset" of things not set yet for anything.
        constraint_collection.removeAllKnowledge()

        constraint_collection.onExpression( self.getNewLocals() )
        new_locals = self.getNewLocals()

        if new_locals.willRaiseException( BaseException ):
            from .NodeMakingHelpers import makeStatementExpressionOnlyReplacementNode

            result = makeStatementExpressionOnlyReplacementNode(
                expression = new_locals,
                node       = self
            )

            return result, "new_raise", "Setting locals already raises implicitely building new locals."

        return self, None, None



class ExpressionBuiltinDir0(NodeBase, ExpressionMixin):
    kind = "EXPRESSION_BUILTIN_DIR0"

    def __init__(self, source_ref):
        NodeBase.__init__( self, source_ref = source_ref )

    def computeExpression(self, constraint_collection):
        return self, None, None


class ExpressionBuiltinDir1(ExpressionBuiltinSingleArgBase):
    kind = "EXPRESSION_BUILTIN_DIR1"

    def computeExpression(self, constraint_collection):
        # TODO: Quite some cases should be possible to predict.
        return self, None, None
