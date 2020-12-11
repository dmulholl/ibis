# Base class for all exception types raised by the template engine.
class TemplateError(Exception):
    pass


# This exception type may be raised while attempting to load a template file.
class TemplateLoadError(TemplateError):
    pass


# This exception type is raised if the lexer cannot tokenize a template string.
class TemplateLexingError(TemplateError):

    def __init__(self, msg, template_id):
        super().__init__(msg)
        self.template_id = template_id


# This exception type may be raised while a template is being compiled.
class TemplateSyntaxError(TemplateError):

    def __init__(self, msg, token):
        super().__init__(msg)
        self.token = token


# This exception type may be raised while a template is being rendered.
class TemplateRenderingError(TemplateError):

    def __init__(self, msg, token):
        super().__init__(msg)
        self.token = token


# This exception type is raised in strict mode if a variable cannot be resolved.
class UndefinedVariable(TemplateError):

    def __init__(self, msg, token):
        super().__init__(msg)
        self.token = token

