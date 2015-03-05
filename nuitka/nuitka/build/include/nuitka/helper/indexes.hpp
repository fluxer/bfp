//     Copyright 2015, Kay Hayen, mailto:kay.hayen@gmail.com
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
#ifndef __NUITKA_HELPER_INDEXES_H__
#define __NUITKA_HELPER_INDEXES_H__

#include "nuitka/helper/raising.hpp"

NUITKA_MAY_BE_UNUSED static Py_ssize_t CONVERT_TO_INDEX( PyObject *value )
{
    CHECK_OBJECT( value );

#if PYTHON_VERSION < 300
    if ( PyInt_Check( value ) )
    {
        return PyInt_AS_LONG( value );
    }
    else
#endif
    if ( PyIndex_Check( value ) )
    {
        return PyNumber_AsSsize_t( value, NULL );
    }
    else
    {
        PyErr_Format( PyExc_TypeError, "slice indices must be integers or None or have an __index__ method" );
        return -1;
    }
}

#endif
