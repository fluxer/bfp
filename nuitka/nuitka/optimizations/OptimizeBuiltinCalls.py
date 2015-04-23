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
""" Optimize calls to built-in references to specific built-in calls.

For built-in name references, we check if it's one of the supported built-in
types, and then specialize for the ones, where it makes sense.
"""

from logging import warning

from nuitka.Builtins import calledWithBuiltinArgumentNamesDecorator
from nuitka.nodes.AssignNodes import (
    StatementAssignmentVariable,
    StatementDelVariable
)
from nuitka.nodes.AttributeNodes import (
    ExpressionAttributeLookup,
    ExpressionBuiltinGetattr,
    ExpressionBuiltinHasattr,
    ExpressionBuiltinSetattr
)
from nuitka.nodes.BuiltinDecodingNodes import (
    ExpressionBuiltinChr,
    ExpressionBuiltinOrd,
    ExpressionBuiltinOrd0
)
from nuitka.nodes.BuiltinDictNodes import ExpressionBuiltinDict
from nuitka.nodes.BuiltinFormatNodes import (
    ExpressionBuiltinBin,
    ExpressionBuiltinHex,
    ExpressionBuiltinId,
    ExpressionBuiltinOct
)
from nuitka.nodes.BuiltinIteratorNodes import (
    ExpressionBuiltinIter1,
    ExpressionBuiltinIter2,
    ExpressionBuiltinLen,
    ExpressionBuiltinNext1,
    ExpressionBuiltinNext2
)
from nuitka.nodes.BuiltinOpenNodes import ExpressionBuiltinOpen
from nuitka.nodes.BuiltinRangeNodes import (
    ExpressionBuiltinRange0,
    ExpressionBuiltinRange1,
    ExpressionBuiltinRange2,
    ExpressionBuiltinRange3
)
from nuitka.nodes.BuiltinRefNodes import (
    ExpressionBuiltinAnonymousRef,
    ExpressionBuiltinOriginalRef,
    ExpressionBuiltinRef
)
from nuitka.nodes.BuiltinTypeNodes import (
    ExpressionBuiltinBool,
    ExpressionBuiltinBytearray,
    ExpressionBuiltinComplex,
    ExpressionBuiltinFloat,
    ExpressionBuiltinInt,
    ExpressionBuiltinList,
    ExpressionBuiltinSet,
    ExpressionBuiltinSlice,
    ExpressionBuiltinStr,
    ExpressionBuiltinTuple
)
from nuitka.nodes.BuiltinVarsNodes import ExpressionBuiltinVars
from nuitka.nodes.CallNodes import ExpressionCallEmpty, ExpressionCallNoKeywords
from nuitka.nodes.ClassNodes import ExpressionBuiltinType3
from nuitka.nodes.ComparisonNodes import ExpressionComparisonIs
from nuitka.nodes.ConditionalNodes import (
    ExpressionConditional,
    StatementConditional
)
from nuitka.nodes.ConstantRefNodes import ExpressionConstantRef
from nuitka.nodes.ExecEvalNodes import (
    ExpressionBuiltinCompile,
    ExpressionBuiltinEval
)
from nuitka.nodes.GlobalsLocalsNodes import (
    ExpressionBuiltinDir1,
    ExpressionBuiltinGlobals,
    ExpressionBuiltinLocals
)
from nuitka.nodes.ImportNodes import ExpressionBuiltinImport
from nuitka.nodes.OperatorNodes import (
    ExpressionOperationNOT,
    ExpressionOperationUnary
)
from nuitka.nodes.StatementNodes import StatementsSequence
from nuitka.nodes.TryFinallyNodes import ExpressionTryFinally
from nuitka.nodes.TypeNodes import (
    ExpressionBuiltinIsinstance,
    ExpressionBuiltinSuper,
    ExpressionBuiltinType1
)
from nuitka.nodes.VariableRefNodes import (
    ExpressionTargetTempVariableRef,
    ExpressionTempVariableRef,
    ExpressionVariableRef
)
from nuitka.Options import isDebug, shallMakeModule
from nuitka.tree.ReformulationExecStatements import wrapEvalGlobalsAndLocals
from nuitka.utils.Utils import python_version
from nuitka.VariableRegistry import addVariableUsage

from . import BuiltinOptimization


def dir_extractor(node):
    def buildDirEmptyCase(source_ref):
        if node.getParentVariableProvider().isPythonModule():
            source = ExpressionBuiltinGlobals(
                source_ref = source_ref
            )
        else:
            source = ExpressionBuiltinLocals(
                source_ref = source_ref
            )

        result = ExpressionCallEmpty(
            called     = ExpressionAttributeLookup(
                source         = source,
                attribute_name = "keys",
                source_ref     = source_ref
            ),
            source_ref = source_ref
        )

        # For Python3, keys doesn't really return values, but instead a handle
        # only.
        if python_version >= 300:
            result = ExpressionBuiltinList(
                value      = result,
                source_ref = source_ref
            )

        return result


    return BuiltinOptimization.extractBuiltinArgs(
        node                = node,
        builtin_class       = ExpressionBuiltinDir1,
        builtin_spec        = BuiltinOptimization.builtin_dir_spec,
        empty_special_class = buildDirEmptyCase
    )

def vars_extractor(node):
    def selectVarsEmptyClass(source_ref):
        if node.getParentVariableProvider().isPythonModule():
            return ExpressionBuiltinGlobals(
                source_ref = source_ref
            )
        else:
            return ExpressionBuiltinLocals(
                source_ref = source_ref
            )

    return BuiltinOptimization.extractBuiltinArgs(
        node                = node,
        builtin_class       = ExpressionBuiltinVars,
        builtin_spec        = BuiltinOptimization.builtin_vars_spec,
        empty_special_class = selectVarsEmptyClass
    )

def import_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinImport,
        builtin_spec  = BuiltinOptimization.builtin_import_spec
    )

def type_extractor(node):
    args = node.getCallArgs()
    length = args.getIterationLength()

    if length == 1:
        return BuiltinOptimization.extractBuiltinArgs(
            node          = node,
            builtin_class = ExpressionBuiltinType1,
            builtin_spec  = BuiltinOptimization.builtin_type1_spec
        )

    else:
        return BuiltinOptimization.extractBuiltinArgs(
            node          = node,
            builtin_class = ExpressionBuiltinType3,
            builtin_spec  = BuiltinOptimization.builtin_type3_spec
        )

def iter_extractor(node):
    @calledWithBuiltinArgumentNamesDecorator
    def wrapIterCreation(callable_arg, sentinel, source_ref):
        if sentinel is None:
            return ExpressionBuiltinIter1(
                value      = callable_arg,
                source_ref = source_ref
            )
        else:
            return ExpressionBuiltinIter2(
                callable   = callable_arg,
                sentinel   = sentinel,
                source_ref = source_ref
            )

    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = wrapIterCreation,
        builtin_spec  = BuiltinOptimization.builtin_iter_spec
    )


def next_extractor(node):
    # Split up next with and without defaults, they are not going to behave
    # really very similar.
    def selectNextBuiltinClass(iterator, default, source_ref):
        if default is None:
            return ExpressionBuiltinNext1(
                value      = iterator,
                source_ref = source_ref
            )
        else:
            return ExpressionBuiltinNext2(
                iterator   = iterator,
                default    = default,
                source_ref = source_ref
            )

    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = selectNextBuiltinClass,
        builtin_spec  = BuiltinOptimization.builtin_iter_spec
    )


def dict_extractor(node):
    # The "dict" built-in is a bit strange in that it accepts a position
    # parameter, or not, but won't have a default value.
    def wrapExpressionBuiltinDictCreation(positional_args, dict_star_arg,
                                          source_ref):
        if len(positional_args) > 1:
            from nuitka.nodes.NodeMakingHelpers import (
                makeRaiseExceptionReplacementExpressionFromInstance,
                wrapExpressionWithSideEffects
            )

            result = makeRaiseExceptionReplacementExpressionFromInstance(
                expression = node,
                exception  = TypeError(
                    "dict expected at most 1 arguments, got %d" % (
                        len(positional_args)
                    )
                )
            )

            result = wrapExpressionWithSideEffects(
                side_effects = positional_args,
                old_node     = node,
                new_node     = result
            )

            if dict_star_arg:
                result = wrapExpressionWithSideEffects(
                    side_effects = dict_star_arg,
                    old_node     = node,
                    new_node     = result
                )

            return result

        return ExpressionBuiltinDict(
            pos_arg    = positional_args[0] if positional_args else None,
            pairs      = dict_star_arg,
            source_ref = source_ref
        )

    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = wrapExpressionBuiltinDictCreation,
        builtin_spec  = BuiltinOptimization.builtin_dict_spec
    )

def chr_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinChr,
        builtin_spec  = BuiltinOptimization.builtin_chr_spec
    )

def ord_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node                = node,
        builtin_class       = ExpressionBuiltinOrd,
        builtin_spec        = BuiltinOptimization.builtin_ord_spec,
        empty_special_class = ExpressionBuiltinOrd0
    )

def bin_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinBin,
        builtin_spec  = BuiltinOptimization.builtin_bin_spec
    )

def oct_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinOct,
        builtin_spec  = BuiltinOptimization.builtin_oct_spec
    )

def hex_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinHex,
        builtin_spec  = BuiltinOptimization.builtin_hex_spec
    )

def id_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinId,
        builtin_spec  = BuiltinOptimization.builtin_id_spec
    )

def repr_extractor(node):
    def makeReprOperator(operand, source_ref):
        return ExpressionOperationUnary(
            operator   = "Repr",
            operand    = operand,
            source_ref = source_ref
        )

    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = makeReprOperator,
        builtin_spec  = BuiltinOptimization.builtin_repr_spec
    )

def range_extractor(node):
    def selectRangeBuiltin(low, high, step, source_ref):
        if high is None:
            return ExpressionBuiltinRange1(
                low        = low,
                source_ref = source_ref
            )
        elif step is None:
            return ExpressionBuiltinRange2(
                low        = low,
                high       = high,
                source_ref = source_ref
            )
        else:
            return ExpressionBuiltinRange3(
                low        = low,
                high       = high,
                step       = step,
                source_ref = source_ref
            )


    return BuiltinOptimization.extractBuiltinArgs(
        node                = node,
        builtin_class       = selectRangeBuiltin,
        builtin_spec        = BuiltinOptimization.builtin_range_spec,
        empty_special_class = ExpressionBuiltinRange0
    )

if python_version < 300:
    from nuitka.nodes.BuiltinRangeNodes import ExpressionBuiltinXrange

    def xrange_extractor(node):
        return BuiltinOptimization.extractBuiltinArgs(
            node          = node,
            builtin_class = ExpressionBuiltinXrange,
            builtin_spec  = BuiltinOptimization.builtin_xrange_spec
    )


def len_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinLen,
        builtin_spec  = BuiltinOptimization.builtin_len_spec
    )

def tuple_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinTuple,
        builtin_spec  = BuiltinOptimization.builtin_tuple_spec
    )

def list_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinList,
        builtin_spec  = BuiltinOptimization.builtin_list_spec
    )

def set_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinSet,
        builtin_spec  = BuiltinOptimization.builtin_set_spec
    )

def float_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinFloat,
        builtin_spec  = BuiltinOptimization.builtin_float_spec
    )

def complex_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinComplex,
        builtin_spec  = BuiltinOptimization.builtin_complex_spec
    )

def str_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinStr,
        builtin_spec  = BuiltinOptimization.builtin_str_spec
    )

if python_version < 300:
    from nuitka.nodes.BuiltinTypeNodes import ExpressionBuiltinUnicode

    def unicode_extractor(node):
        return BuiltinOptimization.extractBuiltinArgs(
            node          = node,
            builtin_class = ExpressionBuiltinUnicode,
            builtin_spec  = BuiltinOptimization.builtin_unicode_spec
        )


def bool_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinBool,
        builtin_spec  = BuiltinOptimization.builtin_bool_spec
    )

def int_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinInt,
        builtin_spec  = BuiltinOptimization.builtin_int_spec
    )

if python_version < 300:
    from nuitka.nodes.BuiltinTypeNodes import ExpressionBuiltinLong

    def long_extractor(node):
        return BuiltinOptimization.extractBuiltinArgs(
            node          = node,
            builtin_class = ExpressionBuiltinLong,
            builtin_spec  = BuiltinOptimization.builtin_long_spec
        )

def globals_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinGlobals,
        builtin_spec  = BuiltinOptimization.builtin_globals_spec
    )

def locals_extractor(node):
    # Note: Locals on the module level is really globals.
    provider = node.getParentVariableProvider()

    if provider.isPythonModule():
        return BuiltinOptimization.extractBuiltinArgs(
            node          = node,
            builtin_class = ExpressionBuiltinGlobals,
            builtin_spec  = BuiltinOptimization.builtin_globals_spec
        )
    else:
        return BuiltinOptimization.extractBuiltinArgs(
            node          = node,
            builtin_class = ExpressionBuiltinLocals,
            builtin_spec  = BuiltinOptimization.builtin_locals_spec
        )

if python_version < 300:
    from nuitka.nodes.ExecEvalNodes import ExpressionBuiltinExecfile

    def execfile_extractor(node):
        @calledWithBuiltinArgumentNamesDecorator
        def wrapExpressionBuiltinExecfileCreation(filename, globals_arg,
                                                  locals_arg, source_ref):
            provider = node.getParentVariableProvider()

            temp_scope = provider.allocateTempScope("execfile")

            globals_ref, locals_ref, tried, final = wrapEvalGlobalsAndLocals(
                provider     = provider,
                globals_node = globals_arg,
                locals_node  = locals_arg,
                temp_scope   = temp_scope,
                source_ref   = source_ref
            )

            return ExpressionTryFinally(
                tried      = tried,
                final      = final,
                expression = ExpressionBuiltinExecfile(
                    source_code = ExpressionCallEmpty(
                        called     = ExpressionAttributeLookup(
                            source         = ExpressionBuiltinOpen(
                                filename   = filename,
                                mode       = ExpressionConstantRef(
                                    constant   = "rU",
                                    source_ref = source_ref
                                ),
                                buffering  = None,
                                source_ref = source_ref
                            ),
                            attribute_name = "read",
                            source_ref     = source_ref
                        ),
                        source_ref = source_ref
                    ),
                    globals_arg = globals_ref,
                    locals_arg  = locals_ref,
                    source_ref  = source_ref
                ),
                source_ref = source_ref
            )

        return BuiltinOptimization.extractBuiltinArgs(
            node          = node,
            builtin_class = wrapExpressionBuiltinExecfileCreation,
            builtin_spec  = BuiltinOptimization.builtin_execfile_spec
        )

def eval_extractor(node):
    @calledWithBuiltinArgumentNamesDecorator
    def wrapEvalBuiltin(source, globals_arg, locals_arg, source_ref):
        provider = node.getParentVariableProvider()

        temp_scope = provider.allocateTempScope("eval")

        globals_ref, locals_ref, tried, final = wrapEvalGlobalsAndLocals(
            provider     = provider,
            globals_node = globals_arg,
            locals_node  = locals_arg,
            temp_scope   = temp_scope,
            source_ref   = source_ref
        )

        # The wrapping should not relocate to the "source_ref".
        assert globals_arg is None or \
               globals_ref.getSourceReference() == \
               globals_arg.getSourceReference()
        assert locals_arg is None or \
               locals_ref.getSourceReference() == \
               locals_arg.getSourceReference()

        source_variable = provider.allocateTempVariable(
            temp_scope = temp_scope,
            name       = "source"
        )

        final.setStatements(
            final.getStatements() + (
                StatementDelVariable(
                    variable_ref = ExpressionTargetTempVariableRef(
                        variable   = source_variable,
                        source_ref = source_ref
                    ),
                    tolerant     = True,
                    source_ref   = source_ref
                ),
            )
        )

        strip_choice =  ExpressionConstantRef(
            constant   = (" \t",),
            source_ref = source_ref
        )

        if python_version >= 300:
            strip_choice = ExpressionConditional(
                condition      = ExpressionComparisonIs(
                    left       = ExpressionBuiltinType1(
                        value      = ExpressionTempVariableRef(
                            variable   = source_variable,
                            source_ref = source_ref
                        ),
                        source_ref = source_ref
                    ),
                    right      = ExpressionBuiltinRef(
                        builtin_name = "bytes",
                        source_ref   = source_ref
                    ),
                    source_ref = source_ref
                ),
                yes_expression = ExpressionConstantRef(
                    constant   = (b" \t",),
                    source_ref = source_ref
                ),
                no_expression  = strip_choice,
                source_ref     = source_ref
            )


        # Source needs some special treatment for eval, if it's a string, it
        # must be stripped.
        string_fixup = [
            StatementAssignmentVariable(
                variable_ref = ExpressionTargetTempVariableRef(
                    variable   = source_variable,
                    source_ref = source_ref
                ),
                source       = ExpressionCallNoKeywords(
                    called     = ExpressionAttributeLookup(
                        source         = ExpressionTempVariableRef(
                            variable   = source_variable,
                            source_ref = source_ref
                        ),
                        attribute_name = "strip",
                        source_ref     = source_ref
                    ),
                    args       = strip_choice,
                    source_ref = source_ref
                ),
                source_ref   = source_ref
            )
        ]

        statements = (
            StatementAssignmentVariable(
                variable_ref = ExpressionTargetTempVariableRef(
                    variable   = source_variable,
                    source_ref = source_ref
                ),
                source       = source,
                source_ref   = source_ref,
            ),
            StatementConditional(
                condition  = ExpressionOperationNOT(
                    operand    = ExpressionBuiltinIsinstance(
                        instance   = ExpressionTempVariableRef(
                            variable   = source_variable,
                            source_ref = source_ref
                        ),
                        classes    = ExpressionBuiltinAnonymousRef(
                            builtin_name = "code",
                            source_ref   = source_ref,
                        ),
                        source_ref = source_ref
                    ),
                    source_ref = source_ref
                ),
                yes_branch = StatementsSequence(
                    statements = string_fixup,
                    source_ref = source_ref
                ),
                no_branch  = None,
                source_ref = source_ref
            )
        )

        tried.setStatements(
            tried.getStatements() + statements
        )

        return ExpressionTryFinally(
            tried      = tried,
            expression = ExpressionBuiltinEval(
                source_code = ExpressionTempVariableRef(
                    variable   = source_variable,
                    source_ref = source_ref
                ),
                globals_arg = globals_ref,
                locals_arg  = locals_ref,
                source_ref  = source_ref
            ),
            final      = final,
            source_ref = source_ref
        )

    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = wrapEvalBuiltin,
        builtin_spec  = BuiltinOptimization.builtin_eval_spec
    )

if python_version >= 300:
    from nuitka.nodes.ExecEvalNodes import ExpressionBuiltinExec

    def exec_extractor(node):
        @calledWithBuiltinArgumentNamesDecorator
        def wrapExpressionBuiltinExecCreation(source, globals_arg, locals_arg,
                                              source_ref):
            provider = node.getParentVariableProvider()

            # TODO: Can't really be true, can it?
            if provider.isExpressionFunctionBody():
                provider.markAsExecContaining()

                if provider.isClassDictCreation():
                    provider.markAsUnqualifiedExecContaining(source_ref)

            temp_scope = provider.allocateTempScope("exec")

            globals_ref, locals_ref, tried, final = wrapEvalGlobalsAndLocals(
                provider     = provider,
                globals_node = globals_arg,
                locals_node  = locals_arg,
                temp_scope   = temp_scope,
                source_ref   = source_ref
            )

            return ExpressionTryFinally(
                tried      = tried,
                final      = final,
                expression = ExpressionBuiltinExec(
                    source_code = source,
                    globals_arg = globals_ref,
                    locals_arg  = locals_ref,
                    source_ref  = source_ref
                ),
                source_ref = source_ref
            )

        return BuiltinOptimization.extractBuiltinArgs(
            node          = node,
            builtin_class = wrapExpressionBuiltinExecCreation,
            builtin_spec  = BuiltinOptimization.builtin_eval_spec
        )

def compile_extractor(node):
    def wrapExpressionBuiltinCompileCreation(source_code, filename, mode, flags,
                                             dont_inherit, optimize = None,
                                             source_ref = None):
        return ExpressionBuiltinCompile(
            source_code  = source_code,
            filename     = filename,
            mode         = mode,
            flags        = flags,
            dont_inherit = dont_inherit,
            optimize     = optimize,
            source_ref   = source_ref
        )

    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = wrapExpressionBuiltinCompileCreation,
        builtin_spec  = BuiltinOptimization.builtin_compile_spec
    )


def open_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinOpen,
        builtin_spec  = BuiltinOptimization.builtin_open_spec
    )

def super_extractor(node):
    @calledWithBuiltinArgumentNamesDecorator
    def wrapSuperBuiltin(type_arg, object_arg, source_ref):
        if type_arg is None and python_version >= 300:
            provider = node.getParentVariableProvider()

            if python_version < 340 or True: # TODO: Temporarily reverted:
                type_arg = ExpressionVariableRef(
                    variable_name = "__class__",
                    source_ref    = source_ref
                )

                # Ought to be already closure taken.
                type_arg.setVariable(
                    provider.getVariableForClosure(
                        variable_name = "__class__"
                    )
                )

                # If we already have this as a local variable, then use that
                # instead.
                if type_arg.getVariable().getOwner() is provider:
                    type_arg = None
                else:
                    addVariableUsage(type_arg.getVariable(), provider)
            else:
                parent_provider = provider.getParentVariableProvider()

                class_var = parent_provider.getTempVariable(
                    temp_scope = None,
                    name       = "__class__"
                )

                type_arg = ExpressionTempVariableRef(
                    variable   = class_var,
                    source_ref = source_ref
                )
                addVariableUsage(type_arg.getVariable(), provider)

            from nuitka.nodes.NodeMakingHelpers import \
                makeRaiseExceptionReplacementExpression

            if type_arg is None:
                return makeRaiseExceptionReplacementExpression(
                    expression      = node,
                    exception_type  = "SystemError"
                                        if python_version < 331 else
                                      "RuntimeError",
                    exception_value = "super(): __class__ cell not found",
                )

            if object_arg is None:
                if provider.getParameters().getArgumentCount() > 0:
                    par1_name = provider.getParameters().getArgumentNames()[0]
                    # TODO: Nested first argument would kill us here, need a
                    # test for that.

                    object_arg = ExpressionVariableRef(
                        variable_name = par1_name,
                        source_ref    = source_ref
                    )

                    object_arg.setVariable(
                        provider.getVariableForReference(
                            variable_name = par1_name
                        )
                    )

                    if not object_arg.getVariable().isParameterVariable():
                        return makeRaiseExceptionReplacementExpression(
                            expression      = node,
                            exception_type  = "SystemError"
                                                if python_version < 330 else
                                              "RuntimeError",
                            exception_value = "super(): __class__ cell not found",
                        )
                else:
                    return makeRaiseExceptionReplacementExpression(
                        expression      = node,
                        exception_type  = "RuntimeError",
                        exception_value = "super(): no arguments"
                    )

        return ExpressionBuiltinSuper(
            super_type   = type_arg,
            super_object = object_arg,
            source_ref   = source_ref
        )

    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = wrapSuperBuiltin,
        builtin_spec  = BuiltinOptimization.builtin_super_spec
    )

def hasattr_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinHasattr,
        builtin_spec  = BuiltinOptimization.builtin_hasattr_spec
    )

def getattr_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinGetattr,
        builtin_spec  = BuiltinOptimization.builtin_getattr_spec
    )

def setattr_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinSetattr,
        builtin_spec  = BuiltinOptimization.builtin_setattr_spec
    )

def isinstance_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinIsinstance,
        builtin_spec  = BuiltinOptimization.builtin_isinstance_spec
    )

def bytearray_extractor(node):
    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = ExpressionBuiltinBytearray,
        builtin_spec  = BuiltinOptimization.builtin_bytearray_spec
    )


def slice_extractor(node):
    def wrapSlice(start, stop, step, source_ref):
        if start is not None and stop is None:
            # Default rules are strange. If one argument is given, it's the
            # second one then.
            stop = start
            start = None

        return ExpressionBuiltinSlice(
            start      = start,
            stop       = stop,
            step       = step,
            source_ref = source_ref
        )

    return BuiltinOptimization.extractBuiltinArgs(
        node          = node,
        builtin_class = wrapSlice,
        builtin_spec  = BuiltinOptimization.builtin_slice_spec
    )


_dispatch_dict = {
    "compile"    : compile_extractor,
    "globals"    : globals_extractor,
    "locals"     : locals_extractor,
    "eval"       : eval_extractor,
    "dir"        : dir_extractor,
    "vars"       : vars_extractor,
    "__import__" : import_extractor,
    "chr"        : chr_extractor,
    "ord"        : ord_extractor,
    "bin"        : bin_extractor,
    "oct"        : oct_extractor,
    "hex"        : hex_extractor,
    "id"         : id_extractor,
    "type"       : type_extractor,
    "iter"       : iter_extractor,
    "next"       : next_extractor,
    "range"      : range_extractor,
    "tuple"      : tuple_extractor,
    "list"       : list_extractor,
    "dict"       : dict_extractor,
    "set"        : set_extractor,
    "float"      : float_extractor,
    "complex"    : complex_extractor,
    "str"        : str_extractor,
    "bool"       : bool_extractor,
    "int"        : int_extractor,
    "repr"       : repr_extractor,
    "len"        : len_extractor,
    "super"      : super_extractor,
    "hasattr"    : hasattr_extractor,
    "getattr"    : getattr_extractor,
    "setattr"    : setattr_extractor,
    "isinstance" : isinstance_extractor,
    # TODO: Disabled for now, not handling all cases.
    # "bytearray"  : bytearray_extractor,
    "slice"      : slice_extractor
}

if python_version < 300:
    _dispatch_dict["long"] = long_extractor
    _dispatch_dict["unicode"] = unicode_extractor
    _dispatch_dict["execfile"] = execfile_extractor

    # The handling of 'open' built-in for Python3 is not yet correct.
    _dispatch_dict["open"] = open_extractor
else:
    _dispatch_dict["exec"] = exec_extractor

def check():
    from nuitka.Builtins import builtin_names

    for builtin_name in _dispatch_dict:
        assert builtin_name in builtin_names, builtin_name

check()

_builtin_white_list = (
    # Not supporting 'print', because it could be replaced, and is not
    # worth the effort yet.
    "print",

    # TODO: This could, and should be supported, as we could e.g. lower
    # types easily for it.
    "sorted",
)

def computeBuiltinCall(call_node, called):
    # There is some dispatching for how to output various types of changes,
    # with lots of cases, pylint: disable=R0912

    builtin_name = called.getBuiltinName()

    if builtin_name in _dispatch_dict:
        new_node = _dispatch_dict[builtin_name](call_node)

        # Lets just have this contract to return "None" when no change is meant
        # to be done.
        assert new_node is not call_node
        if new_node is None:
            return call_node, None, None

        # For traces, we are going to ignore side effects, and output traces
        # only based on the basis of it.
        inspect_node = new_node
        if inspect_node.isExpressionSideEffects():
            inspect_node = inspect_node.getExpression()

        if inspect_node.isExpressionBuiltinImport():
            tags    = "new_import"
            message = """\
Replaced dynamic __import__ %s with static module import.""" % (
                inspect_node.kind,
            )
        elif inspect_node.isExpressionBuiltin() or \
             inspect_node.isStatementExec():
            tags = "new_builtin"
            message = "Replaced call to built-in '%s' with built-in call '%s'." % (
                builtin_name,
                inspect_node.kind,
            )
        elif inspect_node.isExpressionRaiseException():
            tags = "new_raise"
            message = """\
Replaced call to built-in '%s' with exception raising call.""" % (
                inspect_node.kind,
            )
        elif inspect_node.isExpressionOperationUnary():
            tags = "new_expression"
            message = """\
Replaced call to built-in '%s' with unary operation '%s'.""" % (
                inspect_node.kind,
                inspect_node.getOperator()
            )
        elif inspect_node.isExpressionCall():
            tags = "new_expression"
            message = """\
Replaced call to built-in '%s' with call.""" % (
                inspect_node.kind,
            )
        elif inspect_node.isExpressionTryFinally():
            tags = "new_expression"
            message = """\
Replaced call to built-in '%s' with try/finally guarded call.""" % (
                inspect_node.getExpression().kind,
            )
        else:

            assert False, (builtin_name, "->", inspect_node)

        # TODO: One day, this should be enabled by default and call either the
        # original built-in or the optimized above one. That should be done,
        # once we can eliminate the condition for most cases.
        if False and isDebug() and not shallMakeModule() and builtin_name:
            from nuitka.nodes.NodeMakingHelpers import \
              makeRaiseExceptionReplacementExpression

            source_ref = called.getSourceReference()

            new_node = ExpressionConditional(
                condition      = ExpressionComparisonIs(
                    left       = ExpressionBuiltinRef(
                        builtin_name = builtin_name,
                        source_ref   = source_ref
                    ),
                    right      = ExpressionBuiltinOriginalRef(
                        builtin_name = builtin_name,
                        source_ref   = source_ref
                    ),
                    source_ref = source_ref
                ),
                yes_expression = new_node,
                no_expression  = makeRaiseExceptionReplacementExpression(
                    exception_type  = "RuntimeError",
                    exception_value = "Built-in '%s' cannot be replaced." % (
                        builtin_name
                    ),
                    expression      = call_node
                ),
                source_ref     = source_ref
            )

        assert tags != ""

        return new_node, tags, message
    else:
        if False and isDebug() and builtin_name not in _builtin_white_list:
            warning(
                "Not handling built-in '%s', consider support." % builtin_name
            )

        return call_node, None, None
