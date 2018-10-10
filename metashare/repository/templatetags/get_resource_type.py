from django import template
from metashare.settings import STATIC_URL

class GetResourceType(template.Node):
    """
    Template tag that allows to display a resource type icon or text in result page template.
    """
    
    def __init__(self, context_var):
        """
        Initialises this template tag.
        """
        super(GetResourceType, self).__init__()
        self.context_var = template.Variable(context_var)
        self.types = {
            "corpus": ("Corpus", "database_yellow"),
            "toolService": ("Tool / Service", "page_white_gear"),
            "lexicalConceptualResource": ("Lexical / Conceptual", "text_ab"),
            "languageDescription": ("Language Description", "script"),
        }

    def render(self, context):
        result = self.context_var.resolve(context)
        if result not in self.types:
            return ''
        return self.types[result][0]


def get_resource_type(parser, token):
    """
    Use it like this: {% get_resource_type variable %}
    """
    tokens = token.contents.split()
    if len(tokens) != 2:
        _msg = "%r tag accepts exactly two arguments" % tokens[0]
        raise template.TemplateSyntaxError(_msg)
    
    return GetResourceType(tokens[1])
    

register = template.Library()

register.tag('get_resource_type', get_resource_type)
