''' Tools to make using ctypes.struct easier
'''
import ctypes


class ComparableStruct(ctypes.Structure):
    ''' Base class to override __eq__ and __ne__ so that
        2 ctypes.Structure's can be compared basd on whether
        all their fields contain the same values. Note that
        all subfield classes in a Structure must also have this
        class as a base for "nested struct" comparisons to work.
    '''
    def __eq__(self, other):
        for f in self._fields_:
            # Special checking for array types
            if isinstance(getattr(self, f[0]), ctypes.Array):
                for i, j in zip(getattr(self, f[0]), getattr(other, f[0])):
                    if i != j:
                        return False
            elif getattr(self, f[0]) != getattr(other, f[0]):
                return False
        return True

    def __ne__(self, other):
        for f in self._fields_:
            # Special checking for array types
            if isinstance(getattr(self, f[0]), ctypes.Array):
                for i, j in zip(getattr(self, f[0]), getattr(other, f[0])):
                    if i != j:
                        return True
            elif getattr(self, f[0]) != getattr(other, f[0]):
                return True
        return False


class StructFieldsIterator:
    ''' Iterates through a ctypes structure and
        returns each field as a string in the format:
        type.subtype. ... . = value
    '''

    def __init__(self, struct_obj):
        self.values = []
        self.next_value(struct_obj)
        self.i = 0

    def __iter__(self):
        return self

    def next_value(self, obj, base_obj_string=None):

        # Initialize base_obj_string to the top base_obj_string structure name
        if not base_obj_string:
            base_obj_string = obj.__class__.__name__

        if issubclass(type(obj), ctypes.Array):
            # This is an array. Add [i] to the base string and recursively
            #   call ourselves again to keep going

            # Save (and later restore the base) before recursing
            old_base_obj_string = base_obj_string

            # Recurse for every nested object in the structure
            for i, nested_obj in enumerate(obj):
                self.next_value(nested_obj, '{}[{}]'.format(base_obj_string, i))

            # Restore the base before the array
            base_obj_string = old_base_obj_string

        elif hasattr(obj, '_fields_'):
            # This is a nested structure. Recurse into ourselves for
            #   every nested structure

            for field_desc in obj._fields_:
                field_name = field_desc[0]
                # field_type = field_desc[1]
                nested_obj = getattr(obj, field_name)

                self.next_value(nested_obj, '{}.{}'.format(base_obj_string, field_name))

        else:
            # Here we have the base_obj_string for a value, add it to the
            #  tracking list
            self.values.append((base_obj_string, obj))

    def __next__(self):
        try:
            ret = self.values[self.i]
            self.i += 1
            return ret
        except IndexError:
            raise StopIteration
