from statement import Statement

INDENTATION_WIDTH = 4


class Block(object):

    def __init__(self, block_type, indent_level, init=None):

        self._type = block_type
        self._indent_level = indent_level

        self._statements = []

        # Add all the statements already contained in init.
        if init is None:
            init = []

        for statement_type, value in init:
            statement = Statement(statement_type, block_type, init=value)
            self.add_statement(statement)

    def add_statement(self, statement):
        """Add a statement of type statement_type to this block."""
        statement.add_to(self._statements)

    def remove(self, statement):
        """Remove a statement from this block."""
        statement.remove_from(self._statements)

    def write(self):
        """Write all the statement groups in this block."""
        if not self._statements:
            return
        for statement in self._statements:
            print statement.write(format_indent(self._indent_level + statement.indent_modifier))
        write_empty_line(1)

    @property
    def all_statements(self):
        """A list of all the statements in this block."""
        return self._statements

    def show_statements(self):
        """Show all the statements in this block."""
        for statement in self._statements:
            print '{0}{1}'.format(format_indent(1), statement)


def format_indent(level=0, width=INDENTATION_WIDTH):
    """
    Format the indentation for the given indentation level and indentation width
    :param level: the level of indentation
    :param width: the width in spaces of a single indentation
    :return: the indentation string
    """
    return ' ' * level * width


def write_empty_line(number=0):
    for i in range(0, number):
        print ""




