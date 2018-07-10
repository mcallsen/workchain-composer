from string import Template

TEMPLATES = {
    'import_as': '${indent}import ${module_path} as ${alias}',
    'from_import': '${indent}from ${path} import ${items}',
    'spec_item': '${indent}spec.${item_type}(${arguments})',
    'definition': '${indent}${keyword} ${name}(${arguments}):',
    'decorator': '${indent}@${name}',
    'comment': '${indent}${comment}',
}


def get_keywords(line):
    """Return all the <braced> keywords within a line."""

    keywords = list()
    for result in Template.pattern.findall(line):
        if result[2] != '':
            keywords.append(result[2])

    return keywords


class Statement(object):
    """
    A statement in a python script.

    Represents a line of a python script as a string.Template with methods
    to write the corresponding line and to modify the arguments that will
    be used for substitution. Maybe a better name for this class would be
    'Line'.
    """

    def __init__(self, statement_type, block_type, indent=0, init=None, line=None):

        self.type = statement_type
        self.block_type = block_type
        self.indent_modifier = indent

        self._arguments = {}

        if line is None:
            line = TEMPLATES.get(statement_type)

        self._template = Template(line)

        # Set all potential keywords for this template. The list that
        # is created here contains all keys this template would accept.
        self.keywords = get_keywords(line)
        for keyword in self.keywords:
            self._arguments[keyword] = ""

        if init is None:
            init = dict()

        self._arguments.update(init)

    def write(self, indent):
        """Write the line represented by this statement by substituting all keys in the template."""
        self._arguments['indent'] = indent
        return self._template.substitute(**self._arguments)

    def modify(self, argument, value):
        """Modify one argument for the template substitution."""
        self._arguments[argument] = value


