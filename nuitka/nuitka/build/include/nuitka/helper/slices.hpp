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
#ifndef __NUITKA_HELPER_SLICES_H__
#define __NUITKA_HELPER_SLICES_H__

static inline bool IS_INDEXABLE( PyObject *value )
{
    return
        value == Py_None ||
#if PYTHON_VERSION < 300
        PyInt_Check( value ) ||
#endif
        PyLong_Check( value ) ||
        PyIndex_Check( value );
}

#if PYTHON_VERSION < 300
// Note: It appears that Python3 has no index slicing operations anymore, but
// uses slice objects all the time. That's fine and make sure we adhere to it by
// guarding the presence of the helpers.

NUITKA_MAY_BE_UNUSED static PyObject *LOOKUP_SLICE( PyObject *source, PyObject *lower, PyObject *upper )
{
    assertObject( source );
    assertObject( lower );
    assertObject( upper );

    PySequenceMethods *tp_as_sequence = Py_TYPE( source )->tp_as_sequence;

    if ( tp_as_sequence && tp_as_sequence->sq_slice && IS_INDEXABLE( lower ) && IS_INDEXABLE( upper ) )
    {
        Py_ssize_t ilow = 0;

        if ( lower != Py_None )
        {
            ilow = CONVERT_TO_INDEX( lower );
        }

        Py_ssize_t ihigh = PY_SSIZE_T_MAX;

        if ( upper != Py_None )
        {
            ihigh = CONVERT_TO_INDEX( upper );
        }

        PyObject *result = PySequence_GetSlice( source, ilow, ihigh );

        if (unlikely( result == NULL ))
        {
            throw PythonException();
        }

        return result;
    }
    else
    {
        PyObject *slice = PySlice_New( lower, upper, NULL );

        if (unlikely( slice == NULL ))
        {
            throw PythonException();
        }

        PyObject *result = PyObject_GetItem( source, slice );
        Py_DECREF( slice );

        if (unlikely( result == NULL ))
        {
            throw PythonException();
        }

        return result;
    }
}

NUITKA_MAY_BE_UNUSED static PyObject *LOOKUP_INDEX_SLICE( PyObject *source, Py_ssize_t lower, Py_ssize_t upper )
{
    assertObject( source );

    PyObject *result = PySequence_GetSlice( source, lower, upper );

    if (unlikely( result == NULL ))
    {
        throw PythonException();
    }

    return result;
}

NUITKA_MAY_BE_UNUSED static void SET_SLICE( PyObject *value, PyObject *target, PyObject *lower, PyObject *upper )
{
    assertObject( target );
    assertObject( lower );
    assertObject( upper );
    assertObject( value );

    PySequenceMethods *tp_as_sequence = Py_TYPE( target )->tp_as_sequence;

    if ( tp_as_sequence && tp_as_sequence->sq_ass_slice && IS_INDEXABLE( lower ) && IS_INDEXABLE( upper ) )
    {
        Py_ssize_t lower_int = 0;

        if ( lower != Py_None )
        {
            lower_int = CONVERT_TO_INDEX( lower );
        }

        Py_ssize_t upper_int = PY_SSIZE_T_MAX;

        if ( upper != Py_None )
        {
            upper_int = CONVERT_TO_INDEX( upper );
        }

        int status = PySequence_SetSlice( target, lower_int, upper_int, value );

        if (unlikely( status == -1 ))
        {
            throw PythonException();
        }
    }
    else
    {
        PyObject *slice = PySlice_New( lower, upper, NULL );

        if (unlikely( slice == NULL ))
        {
            throw PythonException();
        }

        int status = PyObject_SetItem( target, slice, value );
        Py_DECREF( slice );

        if (unlikely( status == -1 ))
        {
            throw PythonException();
        }
    }
}

NUITKA_MAY_BE_UNUSED static void SET_INDEX_SLICE( PyObject *target, Py_ssize_t lower, Py_ssize_t upper, PyObject *value )
{
    assertObject( target );
    assertObject( value );

    int status = PySequence_SetSlice( target, lower, upper, value );

    if (unlikely( status == -1 ))
    {
        throw PythonException();
    }
}

NUITKA_MAY_BE_UNUSED static void DEL_SLICE( PyObject *target, Py_ssize_t lower, Py_ssize_t upper )
{
    assertObject( target );

    if ( Py_TYPE( target )->tp_as_sequence && Py_TYPE( target )->tp_as_sequence->sq_ass_slice )
    {
        int status = PySequence_DelSlice( target, lower, upper );

        if (unlikely( status == -1 ))
        {
            throw PythonException();
        }
    }
    else
    {
        PyObjectTemporary lower_obj( PyInt_FromSsize_t( lower ) );
        PyObjectTemporary upper_obj( PyInt_FromSsize_t( upper ) );

        PyObject *slice = PySlice_New( lower_obj.asObject0(), upper_obj.asObject0(), NULL );

        if (unlikely( slice == NULL ))
        {
            throw PythonException();
        }

        int status = PyObject_DelItem( target, slice );

        Py_DECREF( slice );

        if (unlikely( status == -1 ))
        {
            throw PythonException();
        }
    }
}

#endif

NUITKA_MAY_BE_UNUSED static PyObject *MAKE_SLICEOBJ( PyObject *start, PyObject *stop, PyObject *step )
{
    assertObject( start );
    assertObject( stop );
    assertObject( step );

    PyObject *result = PySlice_New( start, stop, step );

    if (unlikely( result == NULL ))
    {
        throw PythonException();
    }

    return result;
}

#endif
