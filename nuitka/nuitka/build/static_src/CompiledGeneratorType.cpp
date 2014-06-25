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

#include "nuitka/prelude.hpp"

static PyObject *Nuitka_Generator_tp_repr( Nuitka_GeneratorObject *generator )
{
#if PYTHON_VERSION < 300
    return PyString_FromFormat(
#else
    return PyUnicode_FromFormat(
#endif
        "<compiled generator object %s at %p>",
        Nuitka_String_AsString( generator->m_name ),
        generator
    );
}

static long Nuitka_Generator_tp_traverse( PyObject *function, visitproc visit, void *arg )
{
    // TODO: Identify the impact of not visiting owned objects and/or if it
    // could be NULL instead. The methodobject visits its self and module. I
    // understand this is probably so that back references of this function to
    // its upper do not make it stay in the memory. A specific test if that
    // works might be needed.
    return 0;
}


static PyObject *Nuitka_Generator_send( Nuitka_GeneratorObject *generator, PyObject *value )
{
    if ( generator->m_status == status_Unused && value != NULL && value != Py_None )
    {
        PyErr_Format( PyExc_TypeError, "can't send non-None value to a just-started generator" );
        return NULL;
    }

    if ( generator->m_status != status_Finished )
    {
        PyThreadState *thread_state = PyThreadState_GET();

#if PYTHON_VERSION < 300
        PyObject *saved_exception_type = INCREASE_REFCOUNT_X( thread_state->exc_type );
        PyObject *saved_exception_value = INCREASE_REFCOUNT_X( thread_state->exc_value );
        PyTracebackObject *saved_exception_traceback = INCREASE_REFCOUNT_X( (PyTracebackObject *)thread_state->exc_traceback );
#endif

        if ( generator->m_running )
        {
            PyErr_Format( PyExc_ValueError, "generator already executing" );
            return NULL;
        }

        if ( generator->m_status == status_Unused )
        {
            generator->m_status = status_Running;

            // Prepare the generator context to run. TODO: Make stack size
            // rational.
            prepareFiber( &generator->m_yielder_context, generator->m_code, (unsigned long)generator );
        }

        generator->m_yielded = value;

        // Put the generator back on the frame stack.
        PyFrameObject *return_frame = thread_state->frame;
#ifndef __NUITKA_NO_ASSERT__
        if ( return_frame )
        {
            assertFrameObject( return_frame );
        }
#endif

        if ( generator->m_frame )
        {
            // It would be nice if our frame were still alive. Nobody had the
            // right to release it.
            assertFrameObject( generator->m_frame );

            // It's not supposed to be on the top right now.
            assert( return_frame != generator->m_frame );

            Py_XINCREF( return_frame );
            generator->m_frame->f_back = return_frame;

            thread_state->frame = generator->m_frame;
        }

        // Continue the yielder function while preventing recursion.
        generator->m_running = true;

        swapFiber( &generator->m_caller_context, &generator->m_yielder_context );

        generator->m_running = false;

        thread_state = PyThreadState_GET();

        // Remove the generator from the frame stack.
        assert( thread_state->frame == generator->m_frame );
        assertFrameObject( generator->m_frame );

        thread_state->frame = return_frame;
        Py_CLEAR( generator->m_frame->f_back );

        if ( generator->m_yielded == NULL )
        {
            assert( ERROR_OCCURED() );

            generator->m_status = status_Finished;

            Py_XDECREF( generator->m_frame );
            generator->m_frame = NULL;

            if ( generator->m_context )
            {
                // Surpressing exception in cleanup, to restore later before
                // return.
                PythonException saved_exception;

                generator->m_cleanup( generator->m_context );
                generator->m_context = NULL;

                saved_exception.toPython();
            }

            assert( ERROR_OCCURED() );

#if PYTHON_VERSION < 300
            Py_XDECREF( saved_exception_type );
            Py_XDECREF( saved_exception_value );
            Py_XDECREF( saved_exception_traceback );
#endif
            return NULL;
        }
        else
        {
#if PYTHON_VERSION < 300
            _SET_CURRENT_EXCEPTION( saved_exception_type, saved_exception_value, saved_exception_traceback );

            Py_XDECREF( saved_exception_type );
            Py_XDECREF( saved_exception_value );
            Py_XDECREF( saved_exception_traceback );
#endif

            return generator->m_yielded;
        }
    }
    else
    {
        PyErr_SetObject( PyExc_StopIteration, (PyObject *)NULL );

        return NULL;
    }
}

static PyObject *Nuitka_Generator_tp_iternext( Nuitka_GeneratorObject *generator )
{
    return Nuitka_Generator_send( generator, Py_None );
}


static PyObject *Nuitka_Generator_close( Nuitka_GeneratorObject *generator, PyObject *args )
{
    if ( generator->m_status == status_Running )
    {
        generator->m_exception_type = PyExc_GeneratorExit;
        generator->m_exception_value = NULL;
        generator->m_exception_tb = NULL;

        PyObject *result = Nuitka_Generator_send( generator, Py_None );

        if (unlikely( result ))
        {
            Py_DECREF( result );

            PyErr_Format( PyExc_RuntimeError, "generator ignored GeneratorExit" );
            return NULL;
        }
        else if ( PyErr_ExceptionMatches( PyExc_StopIteration ) || PyErr_ExceptionMatches( PyExc_GeneratorExit ) )
        {
            PyErr_Clear();
            return INCREASE_REFCOUNT( Py_None );
        }
        else
        {
            assert( ERROR_OCCURED() );

            return NULL;
        }
    }

    return INCREASE_REFCOUNT( Py_None );
}

static void Nuitka_Generator_tp_dealloc( Nuitka_GeneratorObject *generator )
{
    assert( Py_REFCNT( generator ) == 0 );
    Py_REFCNT( generator ) = 1;

    PyObject *close_result = Nuitka_Generator_close( generator, NULL );

    if (unlikely( close_result == NULL ))
    {
        PyErr_WriteUnraisable( (PyObject *)generator );
    }
    else
    {
        Py_DECREF( close_result );
    }

    assert( Py_REFCNT( generator ) == 1 );
    Py_REFCNT( generator ) = 0;

    releaseFiber( &generator->m_yielder_context );

    // Now it is safe to release references and memory for it.
    Nuitka_GC_UnTrack( generator );

    if ( generator->m_weakrefs != NULL )
    {
        PyObject_ClearWeakRefs( (PyObject *)generator );
    }

    if ( generator->m_context )
    {
        generator->m_cleanup( generator->m_context );
    }

    Py_DECREF( generator->m_name );

    Py_XDECREF( generator->m_frame );

    PyObject_GC_Del( generator );
}

static PyObject *Nuitka_Generator_throw( Nuitka_GeneratorObject *generator, PyObject *args )
{
    generator->m_exception_value = NULL;
    generator->m_exception_tb = NULL;

    int res = PyArg_UnpackTuple( args, "throw", 1, 3, &generator->m_exception_type, &generator->m_exception_value, (PyObject **)&generator->m_exception_tb );

    if ( (PyObject *)generator->m_exception_tb == Py_None )
    {
        generator->m_exception_tb = NULL;
    }
    else if ( generator->m_exception_tb != NULL && !PyTraceBack_Check( generator->m_exception_tb ) )
    {
        PyErr_Format( PyExc_TypeError, "throw() third argument must be a traceback object" );
        return NULL;
    }

    if (unlikely( res == 0 ))
    {
        generator->m_exception_type = NULL;
        generator->m_exception_value = NULL;
        generator->m_exception_tb = NULL;

        return NULL;
    }

    Py_INCREF( generator->m_exception_type );
    Py_XINCREF( generator->m_exception_value );
    Py_XINCREF( generator->m_exception_tb );

    if ( PyExceptionClass_Check( generator->m_exception_type ))
    {
        NORMALIZE_EXCEPTION( &generator->m_exception_type, &generator->m_exception_value, &generator->m_exception_tb );
    }
    else if ( PyExceptionInstance_Check( generator->m_exception_type ) )
    {
        if ( generator->m_exception_value && generator->m_exception_value != Py_None )
        {
            PyErr_Format( PyExc_TypeError, "instance exception may not have a separate value" );
            return NULL;
        }

        Py_XDECREF( generator->m_exception_value );
        generator->m_exception_value = generator->m_exception_type;
        generator->m_exception_type = INCREASE_REFCOUNT( PyExceptionInstance_Class( generator->m_exception_type ) );
    }
    else
    {
        PyErr_Format(
            PyExc_TypeError,
#if PYTHON_VERSION < 300
            "exceptions must be classes, or instances, not %s",
#else
            "exceptions must be classes or instances deriving from BaseException, not %s",
#endif
            Py_TYPE( generator->m_exception_type )->tp_name
        );
        return NULL;
    }

    if ( ( generator->m_exception_tb != NULL ) && ( (PyObject *)generator->m_exception_tb != Py_None ) && ( !PyTraceBack_Check( generator->m_exception_tb ) ) )
    {
        PyErr_Format( PyExc_TypeError, "throw() third argument must be a traceback object" );
        return NULL;
    }

    PyObject *exception_type = generator->m_exception_type;
    PyObject *exception_value = generator->m_exception_value;
    PyTracebackObject *exception_tb = generator->m_exception_tb;

    if ( generator->m_status != status_Finished )
    {
        PyObject *result = Nuitka_Generator_send( generator, Py_None );

        Py_DECREF( exception_type );
        Py_XDECREF( exception_value );
        Py_XDECREF( exception_tb );

        return result;
    }
    else
    {
        PyErr_Restore( generator->m_exception_type, generator->m_exception_value, (PyObject *)generator->m_exception_tb );
        return NULL;
    }
}

static PyObject *Nuitka_Generator_get_name( Nuitka_GeneratorObject *generator )
{
    return INCREASE_REFCOUNT( generator->m_name );
}

static PyObject *Nuitka_Generator_get_code( Nuitka_GeneratorObject *object )
{
    return INCREASE_REFCOUNT( (PyObject *)object->m_code_object );
}

static int Nuitka_Generator_set_code( Nuitka_GeneratorObject *object, PyObject *value )
{
    PyErr_Format( PyExc_RuntimeError, "gi_code is not writable in Nuitka" );
    return -1;
}

static PyObject *Nuitka_Generator_get_frame( Nuitka_GeneratorObject *object )
{
    if ( object->m_frame )
    {
        return INCREASE_REFCOUNT( (PyObject *)object->m_frame );
    }
    else
    {
        return INCREASE_REFCOUNT( Py_None );
    }
}

static int Nuitka_Generator_set_frame( Nuitka_GeneratorObject *object, PyObject *value )
{
    PyErr_Format( PyExc_RuntimeError, "gi_frame is not writable in Nuitka" );
    return -1;
}

static PyGetSetDef Nuitka_Generator_getsetlist[] =
{
    { (char *)"__name__", (getter)Nuitka_Generator_get_name, NULL, NULL },
    { (char *)"gi_code",  (getter)Nuitka_Generator_get_code, (setter)Nuitka_Generator_set_code, NULL },
    { (char *)"gi_frame", (getter)Nuitka_Generator_get_frame, (setter)Nuitka_Generator_set_frame, NULL },

    { NULL }
};

static PyMethodDef Nuitka_Generator_methods[] =
{
    { "send",  (PyCFunction)Nuitka_Generator_send,  METH_O, NULL },
    { "throw", (PyCFunction)Nuitka_Generator_throw, METH_VARARGS, NULL },
    { "close", (PyCFunction)Nuitka_Generator_close, METH_NOARGS, NULL },
    { NULL }
};

#include <structmember.h>

static PyMemberDef Nuitka_Generator_members[] =
{
    { (char *)"gi_running", T_INT, offsetof( Nuitka_GeneratorObject, m_running ), READONLY },
    { NULL }
};


PyTypeObject Nuitka_Generator_Type =
{
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "compiled_generator",                            // tp_name
    sizeof(Nuitka_GeneratorObject),                  // tp_basicsize
    0,                                               // tp_itemsize
    (destructor)Nuitka_Generator_tp_dealloc,         // tp_dealloc
    0,                                               // tp_print
    0,                                               // tp_getattr
    0,                                               // tp_setattr
    0,                                               // tp_compare
    (reprfunc)Nuitka_Generator_tp_repr,              // tp_repr
    0,                                               // tp_as_number
    0,                                               // tp_as_sequence
    0,                                               // tp_as_mapping
    0,                                               // tp_hash
    0,                                               // tp_call
    0,                                               // tp_str
    PyObject_GenericGetAttr,                         // tp_getattro
    0,                                               // tp_setattro
    0,                                               // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
                                                     // tp_flags
    0,                                               // tp_doc
    (traverseproc)Nuitka_Generator_tp_traverse,      // tp_traverse
    0,                                               // tp_clear
    0,                                               // tp_richcompare
    offsetof( Nuitka_GeneratorObject, m_weakrefs ),  // tp_weaklistoffset
    PyObject_SelfIter,                               // tp_iter
    (iternextfunc)Nuitka_Generator_tp_iternext,      // tp_iternext
    Nuitka_Generator_methods,                        // tp_methods
    Nuitka_Generator_members,                        // tp_members
    Nuitka_Generator_getsetlist,                     // tp_getset
    0,                                               // tp_base
    0,                                               // tp_dict
    0,                                               // tp_descr_get
    0,                                               // tp_descr_set
    0,                                               // tp_dictoffset
    0,                                               // tp_init
    0,                                               // tp_alloc
    0,                                               // tp_new
    0,                                               // tp_free
    0,                                               // tp_is_gc
    0,                                               // tp_bases
    0,                                               // tp_mro
    0,                                               // tp_cache
    0,                                               // tp_subclasses
    0,                                               // tp_weaklist
    0                                                // tp_del
};

PyObject *Nuitka_Generator_New( yielder_func code, PyObject *name, PyCodeObject *code_object, void *context, releaser cleanup )
{
    Nuitka_GeneratorObject *result = PyObject_GC_New( Nuitka_GeneratorObject, &Nuitka_Generator_Type );

    if (unlikely( result == NULL ))
    {
        PyErr_Format(
            PyExc_RuntimeError,
            "cannot create genexpr %s",
            Nuitka_String_AsString( name )
        );

        throw PythonException();
    }

    result->m_code = (void *)code;

    result->m_name = INCREASE_REFCOUNT( name );

    result->m_context = context;
    result->m_cleanup = cleanup;

    result->m_weakrefs = NULL;

    result->m_status = status_Unused;
    result->m_running = false;

    initFiber( &result->m_yielder_context );

    result->m_exception_type = NULL;
    result->m_yielded = NULL;

    result->m_frame = NULL;
    result->m_code_object = code_object;

    Nuitka_GC_Track( result );
    return (PyObject *)result;
}

PyObject *Nuitka_Generator_New( yielder_func code, PyObject *name, PyCodeObject *code_object )
{
    return Nuitka_Generator_New( code, name, code_object, NULL, NULL );
}

#if PYTHON_VERSION >= 330

// This is for CPython iterator objects, the respective code is not exported as
// API, so we need to redo it. This is an re-implementation that closely follows
// what it does. It's unrelated to compiled generators.
PyObject *PyGen_Send( PyGenObject *generator, PyObject *arg )
{
    if (unlikely( generator->gi_running ))
    {
        PyErr_SetString( PyExc_ValueError, "generator already executing" );
        return NULL;
    }

    PyFrameObject *frame = generator->gi_frame;

    if ( frame == NULL || frame->f_stacktop == NULL )
    {
        // Set exception if called from send()
        if ( arg != NULL )
        {
            PyErr_SetNone( PyExc_StopIteration );
        }

        return NULL;
    }

    if ( frame->f_lasti == -1 )
    {
        if (unlikely( arg && arg != Py_None ))
        {
            PyErr_SetString(
                PyExc_TypeError,
                "can't send non-None value to a just-started generator"
            );

            return NULL;
        }
    }
    else
    {
        // Put arg on top of the value stack
        PyObject *tmp = arg ? arg : Py_None;
        *(frame->f_stacktop++) = INCREASE_REFCOUNT( tmp );
    }

    // Generators always return to their most recent caller, not necessarily
    // their creator.
    PyThreadState *tstate = PyThreadState_GET();
    Py_XINCREF( tstate->frame );

    assert( frame->f_back == NULL );
    frame->f_back = tstate->frame;

    generator->gi_running = 1;
    PyObject *result = PyEval_EvalFrameEx( frame, 0 );
    generator->gi_running = 0;

    // Don't keep the reference to f_back any longer than necessary.  It
    // may keep a chain of frames alive or it could create a reference
    // cycle.
    assert( frame->f_back == tstate->frame );
    Py_CLEAR( frame->f_back );

    // If the generator just returned (as opposed to yielding), signal that the
    // generator is exhausted.
    if ( result && frame->f_stacktop == NULL )
    {
        if ( result == Py_None )
        {
            PyErr_SetNone( PyExc_StopIteration );
        }
        else {
            PyObject *e = PyObject_CallFunctionObjArgs(
                PyExc_StopIteration,
                result,
                NULL
            );

            if ( e != NULL )
            {
                PyErr_SetObject( PyExc_StopIteration, e );
                Py_DECREF( e );
            }
        }

        Py_CLEAR( result );
    }

    if ( result == NULL || frame->f_stacktop == NULL )
    {
        // Generator is finished, remove exception from frame before releasing
        // it.
        PyObject *type = frame->f_exc_type;
        PyObject *value = frame->f_exc_value;
        PyObject *traceback = frame->f_exc_traceback;
        frame->f_exc_type = NULL;
        frame->f_exc_value = NULL;
        frame->f_exc_traceback = NULL;
        Py_XDECREF( type );
        Py_XDECREF( value );
        Py_XDECREF( traceback );

        // Now release frame.
        generator->gi_frame = NULL;
        Py_DECREF( frame );
    }

    return result;
}

PyObject *ERROR_GET_STOP_ITERATION_VALUE()
{
    assert ( PyErr_ExceptionMatches( PyExc_StopIteration ));

    PyObject *et, *ev, *tb;
    PyErr_Fetch( &et, &ev, &tb );

    Py_XDECREF(et);
    Py_XDECREF(tb);

    PyObject *value = NULL;

    if ( ev )
    {
        if ( PyErr_GivenExceptionMatches( ev, PyExc_StopIteration ) )
        {
            value = ((PyStopIterationObject *)ev)->value;
            Py_DECREF( ev );
        }
        else
        {
            value = ev;
        }
    }

    if ( value == NULL )
    {
        value = INCREASE_REFCOUNT( Py_None );
    }

    return value;
}
#endif
