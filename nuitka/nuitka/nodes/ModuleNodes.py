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
""" Module/Package nodes

The top of the tree. Packages are also modules. Modules are what hold a program
together and cross-module optimizations are the most difficult to tackle.
"""

from .NodeBases import (
    ClosureGiverNodeBase,
    ChildrenHavingMixin,
    NodeBase
)

from .IndicatorMixins import MarkContainsTryExceptIndicator
from nuitka.SourceCodeReferences import SourceCodeReference
from nuitka.nodes.FutureSpecs import FutureSpec

from nuitka import Variables, Importing, Utils

from nuitka.oset import OrderedSet

import re


class PythonModuleMixin:
    def __init__(self, name, package_name):
        assert type(name) is str, type(name)
        assert "." not in name, name
        assert package_name is None or \
               (type( package_name ) is str and package_name != "")

        self.name = name
        self.package_name = package_name
        self.package = None

    def getName(self):
        return self.name

    def getPackage(self):
        return self.package_name

    def getFullName(self):
        if self.package_name:
            return self.package_name + "." + self.getName()
        else:
            return self.getName()

    def isMainModule(self):
        return False

    def isInternalModule(self):
        return False

    def attemptRecursion(self):
        # Make sure the package is recursed to.
        from nuitka.tree import Recursion
        from nuitka import Importing

        # Return the list of newly added modules.
        result = []

        if self.package_name is not None and self.package is None:
            package_package, _package_module_name, package_filename = \
              Importing.findModule(
                source_ref     = self.getSourceReference(),
                module_name    = self.package_name,
                parent_package = None,
                level          = 1,
                warn           = Utils.python_version < 330
            )

            # TODO: Temporary, if we can't find the package for Python3.3 that
            # is semi-OK, maybe.
            if Utils.python_version >= 330 and not package_filename:
                return []

            imported_module, is_added = Recursion.recurseTo(
                module_package  = package_package,
                module_filename = package_filename,
                module_relpath  = Utils.relpath(package_filename),
                module_kind     = "py",
                reason          = "Containing package of recursed module.",
            )

            self.package = imported_module

            if is_added:
                result.append(imported_module)

        if self.package:
            from nuitka.ModuleRegistry import addUsedModule

            addUsedModule(self.package)

#            print "Recursed to package", self.package_name
            result.extend(self.package.attemptRecursion())

        return result

def checkModuleBody(value):
    assert value is None or value.isStatementsSequence()

    return value

class PythonModule(PythonModuleMixin, ChildrenHavingMixin,
                   ClosureGiverNodeBase, MarkContainsTryExceptIndicator):
    """ Module

        The module is the only possible root of a tree. When there are many
        modules they form a forrest.
    """

    kind = "PYTHON_MODULE"

    named_children = (
        "body",
    )

    checkers = {
        "body": checkModuleBody
    }

    def __init__(self, name, package_name, source_ref):
        ClosureGiverNodeBase.__init__(
            self,
            name        = name,
            code_prefix = "module",
            source_ref  = source_ref
        )

        ChildrenHavingMixin.__init__(
            self,
            values = {},
        )

        MarkContainsTryExceptIndicator.__init__( self )

        PythonModuleMixin.__init__(
            self,
            name         = name,
            package_name = package_name
        )

        self.variables = set()

        # The list functions contained in that module.
        self.functions = OrderedSet()

        self.active_functions = OrderedSet()

        # SSA trace based information about the module.
        self.collection = None

    def getDetails(self):
        return {
            "filename" : self.source_ref.getFilename(),
            "package"  : self.package_name,
            "name"     : self.name
        }

    def asXml(self):
        # The class is new style, false alarm: pylint: disable=E1002
        result = super( PythonModule, self ).asXml()

        for function_body in self.functions:
            result.append( function_body.asXml() )

        return result

    getBody = ChildrenHavingMixin.childGetter("body")
    setBody = ChildrenHavingMixin.childSetter("body")

    def isPythonModule(self):
        return True

    def getParent(self):
        assert False

    def getParentVariableProvider(self):
        return None

    def getVariables(self):
        return self.variables

    def getFilename(self):
        return self.source_ref.getFilename()

    def getVariableForAssignment(self, variable_name):
        result = self.getProvidedVariable(variable_name)

        return result.makeReference(self)

    def getVariableForReference(self, variable_name):
        result = self.getProvidedVariable(variable_name)

        return result.makeReference(self)

    def getVariableForClosure(self, variable_name):
        return self.getProvidedVariable(
            variable_name = variable_name
        )

    def createProvidedVariable(self, variable_name):
        result = Variables.ModuleVariable(
            module        = self,
            variable_name = variable_name
        )

        assert result not in self.variables
        self.variables.add(result)

        return result

    def isEarlyClosure(self):
        # Modules should immediately closure variables on use.
        # pylint: disable=R0201
        return True

    def getCodeName(self):
        def r(match):
            c = match.group()
            if c == '.':
                return "$"
            else:
                return "$$%d$" % ord(c)

        return "module_" + \
          "".join(re.sub("[^a-zA-Z0-9_]", r ,c) for c in self.getFullName())

    def addFunction(self, function_body):
        assert function_body not in self.functions

        self.functions.add( function_body )

    def getFunctions(self):
        return self.functions

    def startTraversal(self):
        self.active_functions = OrderedSet()

    def addUsedFunction(self, function_body):
        assert function_body in self.functions

        assert function_body.isExpressionFunctionBody()

        if function_body not in self.active_functions:
            self.active_functions.add(function_body)

    def getUsedFunctions(self):
        return self.active_functions

    def getOutputFilename(self):
        main_filename = self.getFilename()

        if main_filename.endswith(".py"):
            return main_filename[:-3]
        else:
            return main_filename


class SingleCreationMixin:
    created = set()

    def __init__(self):
        assert self.__class__ not in self.created
        self.created.add( self.__class__ )


class PythonMainModule(PythonModule, SingleCreationMixin):
    kind = "PYTHON_MAIN_MODULE"

    def __init__(self, main_added, source_ref):
        PythonModule.__init__(
            self,
            name         = "__main__",
            package_name = None,
            source_ref   = source_ref
        )

        SingleCreationMixin.__init__( self )

        self.main_added = main_added

    def isMainModule(self):
        return True

    def getOutputFilename(self):
        if self.main_added:
            return Utils.dirname(self.getFilename())
        else:
            return PythonModule.getOutputFilename(self)


class PythonInternalModule(PythonModule, SingleCreationMixin):
    kind = "PYTHON_INTERNAL_MODULE"

    def __init__(self):
        PythonModule.__init__(
            self,
            name         = "__internal__",
            package_name = None,
            source_ref   = SourceCodeReference.fromFilenameAndLine(
                filename    = "internal",
                line        = 0,
                future_spec = FutureSpec(),
                inside_exec = False
            )
        )

        SingleCreationMixin.__init__( self )

    def isInternalModule(self):
        return True

    def getOutputFilename(self):
        return "__internal"


class PythonPackage(PythonModule):
    kind = "PYTHON_PACKAGE"

    def __init__(self, name, package_name, source_ref):
        assert name

        PythonModule.__init__(
            self,
            name         = name,
            package_name = package_name,
            source_ref   = source_ref
        )

    def getOutputFilename(self):
        return Utils.dirname( self.getFilename() )


class PythonShlibModule(PythonModuleMixin, NodeBase):
    kind = "PYTHON_SHLIB_MODULE"

    def __init__(self, name, package_name, source_ref):
        NodeBase.__init__(
            self,
            source_ref = source_ref
        )

        PythonModuleMixin.__init__(
            self,
            name         = name,
            package_name = package_name
        )

        assert Utils.basename(source_ref.getFilename()) != "<frozen>"

    def getDetails(self):
        return {
            "name"         : self.name,
            "package_name" : self.package_name
        }

    def getFilename(self):
        return self.getSourceReference().getFilename()

    def startTraversal(self):
        pass

    def getImplicitImports(self):
        full_name = self.getFullName()

        if full_name == "PyQt4.QtCore":
            return (
                ("atexit", None),
                ("sip", None)
            )
        elif full_name == "lxml.etree":
            return (
                ("gzip", None),
            )
        elif full_name == "gtk._gtk":
            return (
                ("pangocairo", None),
                ("pango", None),
                ("cairo", None),
                ("gio", None),
                ("atk", None),
            )
        else:
            return ()

    def considerImplicitImports(self, signal_change):
        for module_name, module_package in self.getImplicitImports():
            _module_package, _module_name, module_filename = \
              Importing.findModule(
                source_ref     = self.source_ref,
                module_name    = module_name,
                parent_package = module_package,
                level          = -1,
                warn           = True
            )

            if Utils.isDir(module_filename):
                module_kind = "py"
            elif module_filename.endswith(".py"):
                module_kind = "py"
            elif module_filename.endswith(".so"):
                module_kind = "shlib"
            elif module_filename.endswith(".pyd"):
                module_kind = "shlib"
            else:
                assert False, module_filename

            from nuitka.tree import Recursion

            decision, reason = Recursion.decideRecursion(
                module_filename = module_filename,
                module_name     = module_name,
                module_package  = module_package,
                module_kind     = module_kind
            )

            assert decision or reason == "Module is frozen."

            if decision:
                module_relpath = Utils.relpath(module_filename)

                imported_module, added_flag = Recursion.recurseTo(
                    module_package  = module_package,
                    module_filename = module_filename,
                    module_relpath  = module_relpath,
                    module_kind     = module_kind,
                    reason          = reason
                )

                from nuitka.ModuleRegistry import addUsedModule
                addUsedModule(imported_module)

                if added_flag:
                    signal_change(
                        "new_code",
                        imported_module.getSourceReference(),
                        "Recursed to module."
                    )
