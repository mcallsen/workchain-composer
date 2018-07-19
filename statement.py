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

        self.arguments = {}

        if line is None:
            line = TEMPLATES.get(statement_type)

        self._template = Template(line)

        # Set all potential keywords for this template. The list that
        # is created here contains all keys this template would accept.
        self.keywords = get_keywords(line)
        for keyword in self.keywords:
            self.arguments[keyword] = ""

        if init is None:
            init = dict()

        self.arguments.update(init)

    def write(self, indent):
        """Write the line represented by this statement by substituting all keys in the template."""
        self.arguments['indent'] = indent
        return self._template.substitute(**self.arguments)

    def modify(self, argument, value):
        """Modify one argument for the template substitution."""
        self.arguments[argument] = value

    def add_to(self, statement_list):
        """Add this statement to a list of statements."""
        if self not in statement_list:
            statement_list.append(self)

    def remove_from(self, statement_list):
        """Remove this statement from a list of statements."""
        if self in statement_list:
            statement_list.remove(self)


class FromImportStatement(Statement):

    def __init__(self, statement_type, block_type, indent=0, init=None, line=None):
        super(FromImportStatement, self).__init__(statement_type, block_type, indent, init, line)
        self.count = 0

    def add_to(self, statement_list):

        # This is an import statement, check wether we can concatenate it with
        # an already existing statement.
        for statement in statement_list:
            if statement.arguments.get('path') == self.arguments.get('path'):
                # There is already a statement with this path in the block. Add this import.
                statement.arguments['items'] = ', '.join([statement.arguments['items'], self.arguments['items']])
                statement.count += 1
                return

        statement_list.append(self)

    def remove_from(self, statement_list):
        """
        Remove this statement from a list of statements.

        For 'FromImport' statements, the arguments might have been concatenated into just
        a single statement. Therefore we have to check first, whether there is an import
        statement for the same path.
        """

        for statement in statement_list:
            if statement.arguments.get('path') == self.arguments.get('path'):
                # There is a statement with this path in the block.
                arguments = statement.arguments['items'].split(', ')
                if self.arguments['items'] in arguments:
                    if statement.count > 0:
                        # There is one more component importing this item. Just reduce the count.
                        statement.coun -= 1
                    # This is the only component requiring this import.
                    arguments.remove(self.arguments['items'])
                    if not arguments:
                        # arguments are empty, remove this statement completely.
                        statement_list.remove(statement)
                        return
                    statement.arguments['items'] = ', '.join(arguments)
                    return


