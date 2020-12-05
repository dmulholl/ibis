import datetime
from . import errors


# User-configurable functions and variables available in all contexts.
builtins = {
    'now': datetime.datetime.now,
    'range': range,
}


# A Context object is a wrapper around the user's input data. Its `.resolve()` method contains
# the lookup-logic for resolving dotted variable names.
class Context:

    def __init__(self, data_dict, template, strict_mode):
        self.stack = []

        # Standard builtins.
        self.stack.append({
            'context': self,
            'is_defined': self.is_defined,
        })

        # User-configurable builtins.
        self.stack.append(builtins)

        # Instance-specific data.
        self.stack.append(data_dict)

        # Nodes can store state information here to avoid threading issues.
        self.stash = {}

        # This reference gives nodes access to their parent template object.
        self.template = template

        # In strict mode undefined variables raise an UndefinedVariable exception.
        self.strict_mode = strict_mode

    def __setitem__(self, key, value):
        self.stack[-1][key] = value

    def __getitem__(self, key):
        for d in reversed(self.stack):
            if key in d:
                return d[key]
        raise KeyError(key)

    def __delitem__(self, key):
        del self.stack[-1][key]

    def __contains__(self, key):
        for d in self.stack:
            if key in d:
                return True
        return False

    def resolve(self, varstring, template_id, line_number):
        tokens = []
        result = self
        for token in varstring.split('.'):
            tokens.append(token)
            try:
                result = result[token]
            except:
                try:
                    result = getattr(result, token)
                except:
                    if self.strict_mode:
                        msg = f"Cannot resolve the variable '{'.'.join(tokens)}' "
                        msg += f"in template '{template_id}', line {line_number}."
                        raise errors.UndefinedVariable(msg, template_id, line_number) from None
                    return Undefined()
        return result

    def is_defined(self, varstring):
        current = self
        for token in varstring.split('.'):
            try:
                current = current[token]
            except:
                try:
                    current = getattr(current, token)
                except:
                    return False
        return True

    def push(self, data=None):
        self.stack.append(data or {})

    def pop(self):
        self.stack.pop()

    def get(self, key, default=None):
        for d in reversed(self.stack):
            if key in d:
                return d[key]
        return default

    def update(self, data):
        self.stack[-1].update(data)


# Null type returned when a context lookup fails.
class Undefined:

    def __str__(self):
        return ''

    def __bool__(self):
        return False

    def __len__(self):
        return 0

    def __contains__(self, key):
        return False

    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return True
