//     Copyright 2014, Kay Hayen, mailto:kay.hayen@gmail.com
//
//     Part of "Nuitka", an optimizing Python compiler that is compatible and
//     integrates with CPython, but also works on its own.
//
//     Licensed under the Apache License, Version 2.0 (the "License");
//     you may not use this file except in compliance with the License.
//     You may obtain a copy of the License at
//
//        http://www.apache.org/licenses/LICENSE-2.0
//
//     Unless required by applicable law or agreed to in writing, software
//     distributed under the License is distributed on an "AS IS" BASIS,
//     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//     See the License for the specific language governing permissions and
//     limitations under the License.
//
#ifndef __NUITKA_BUILTINS_H__
#define __NUITKA_BUILTINS_H__

#include "__helpers.hpp"

extern PyModuleObject *module_builtin;
extern PyDictObject *dict_builtin;

#include "nuitka/calling.hpp"

NUITKA_MAY_BE_UNUSED static PyObject *LOOKUP_BUILTIN( PyObject *name )
{
    assertObject( (PyObject *)dict_builtin );
    assertObject( name );
    assert( Nuitka_String_Check( name ) );

    PyObject *result = GET_STRING_DICT_VALUE(
        dict_builtin,
        (Nuitka_StringObject *)name
    );

    assertObject( result );

    return result;
}

class PythonBuiltin
{
public:
    explicit PythonBuiltin( PyObject **name )
    {
        this->name = (Nuitka_StringObject **)name;
        this->value = NULL;
    }

    PyObject *asObject0()
    {
        if ( this->value == NULL )
        {
            this->value = LOOKUP_BUILTIN( (PyObject *)*this->name );
        }

        assertObject( this->value );

        return this->value;
    }

    void update( PyObject *new_value )
    {
        assertObject( new_value );

        this->value = new_value;
    }

    PyObject *call()
    {
        return CALL_FUNCTION_NO_ARGS(
            this->asObject0()
        );
    }


    PyObject *call1( PyObject *arg )
    {
        return CALL_FUNCTION_WITH_ARGS1(
            this->asObject0(),
            arg
        );
    }

    PyObject *call2( PyObject *arg1, PyObject *arg2 )
    {
        return CALL_FUNCTION_WITH_ARGS2(
            this->asObject0(),
            arg1,
            arg2
        );
    }

    PyObject *call3( PyObject *arg1, PyObject *arg2, PyObject *arg3 )
    {
        return CALL_FUNCTION_WITH_ARGS3(
            this->asObject0(),
            arg1,
            arg2,
            arg3
        );
    }

    PyObject *call_args( PyObject *args )
    {
        return CALL_FUNCTION_WITH_POSARGS(
            this->asObject0(),
            PyObjectTemporary( args ).asObject0()
        );
    }

    PyObject *call_kw( PyObject *kw )
    {
        return CALL_FUNCTION_WITH_KEYARGS(
            this->asObject0(),
            kw
        );
    }

    PyObject *call_args_kw( PyObject *args, PyObject *kw )
    {
        return CALL_FUNCTION(
            this->asObject0(),
            args,
            kw
        );
    }


private:

    PythonBuiltin( PythonBuiltin const &  ) { assert( false );  }

    Nuitka_StringObject **name;
    PyObject *value;
};

extern void _initBuiltinModule();

#ifdef _NUITKA_EXE
// Original builtin values, currently only used for assertions.
extern PyObject *_python_original_builtin_value_type;
extern PyObject *_python_original_builtin_value_len;
extern PyObject *_python_original_builtin_value_range;
extern PyObject *_python_original_builtin_value_repr;
extern PyObject *_python_original_builtin_value_int;
extern PyObject *_python_original_builtin_value_iter;
extern PyObject *_python_original_builtin_value_long;

extern void _initBuiltinOriginalValues();
#endif

#endif
