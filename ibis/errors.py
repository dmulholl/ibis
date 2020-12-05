# Base class for all exception types raised by the template engine.
class TemplateError(Exception):

    def __init__(self, msg, template_id=None, line_number=None):
        super().__init__(msg)
        self.template_id = template_id
        self.line_number = line_number


# This exception type may be raised while a template is being compiled.
class TemplateSyntaxError(TemplateError):
    pass


# This exception type may be raised while a template is being rendered.
class TemplateRenderingError(TemplateError):
    pass


# This exception type may be raised while attempting to load a template file.
class TemplateLoadError(TemplateError):
    pass


# This exception type is raised in strict mode if a variable cannot be resolved.
class UndefinedVariable(TemplateError):
    pass
