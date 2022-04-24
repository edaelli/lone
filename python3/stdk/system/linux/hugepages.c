#include <Python.h>
#include <hugetlbfs.h>


static PyObject *method_hugepages_init(PyObject *self, PyObject *args) {

    // Return the current hugepages size
    PyObject *return_val = Py_BuildValue("");
    return return_val;
}


static PyObject *method_hugepages_get_size(PyObject *self, PyObject *args) {

    // Return the current hugepages size
    long hp_size = gethugepagesize();

    PyObject *return_val = Py_BuildValue("L", hp_size);
    return return_val;
}


static PyObject *method_hugepages_malloc(PyObject *self, PyObject *args) {

    size_t mem_size = 0;
    size_t align = 4096;
    uint64_t *virt_addr;

    // Parse args
    if (!PyArg_ParseTuple(args, "L|L", &mem_size, &align)) {
        return NULL;
    }

    // Allocate hugepages
    virt_addr = get_huge_pages(mem_size, GHP_DEFAULT);

    // Check and return
    if (virt_addr == NULL) {
        PyErr_SetString(PyExc_MemoryError, "Unable to allocate memory");
        return NULL;
    }
    else {
        PyObject *python_val = Py_BuildValue("L", virt_addr);
        return python_val;
    }
}


static PyObject *method_hugepages_free(PyObject *self, PyObject *args) {
    uint64_t *virt_addr;
    uint64_t size;

    // Parse args
    if (!PyArg_ParseTuple(args, "L|L", &virt_addr, &size)) {
        return NULL;
    }

    free_huge_pages(virt_addr);

    return Py_BuildValue("");
}


static PyObject *method_hugepages_finish(PyObject *self, PyObject *args) {

    // Nothing to finish yet
    return Py_BuildValue("");
}


static PyMethodDef HugepagesMethods[] = {
    {"init", method_hugepages_init, METH_VARARGS, "Python interface to init using linux hugepages"},
    {"get_size", method_hugepages_get_size, METH_VARARGS, "Python interface to get current hugepages size"},
    {"malloc", method_hugepages_malloc, METH_VARARGS, "Python interface to allocate hugepages"},
    {"free", method_hugepages_free, METH_VARARGS, "Python interface to free hugepages"},
    {"finish", method_hugepages_finish, METH_VARARGS, "Python interface to finish using hugepages"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef hugepages_module = {
    PyModuleDef_HEAD_INIT,
    "hugepages_ll",
    "Python interface into linux's hugepages memory interfaces",
    -1,
    HugepagesMethods
};


PyMODINIT_FUNC PyInit_hugepages(void) {
    return PyModule_Create(&hugepages_module);
}

