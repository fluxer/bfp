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
""" Finalizations. Last steps directly before code creation is called.

Here the final tasks are executed. Things normally volatile during optimization
can be computed here, so the code generation can be quick and doesn't have to
check it many times.

"""
from .FinalizeMarkups import FinalizeMarkups
from .FinalizeClosureTaking import FinalizeClosureTaking
from .FinalizeVariableVisibility import FinalizeVariableVisibility

# Bug of pylint, it's there but it reports it wrongly, pylint: disable=E0611
from nuitka.tree import Operations

def prepareCodeGeneration(tree):
    visitor = FinalizeMarkups()
    Operations.visitTree( tree, visitor )
    for function in tree.getUsedFunctions():
        Operations.visitTree( function, visitor )

    visitor = FinalizeClosureTaking()
    for function in tree.getUsedFunctions():
        Operations.visitFunction( function, visitor )

    visitor = FinalizeVariableVisibility()
    Operations.visitFunction( tree, visitor )
    for function in tree.getUsedFunctions():
        Operations.visitFunction( function, visitor )
