class Component(object):
    """A Component, that can be added to a WorkChain."""

    def __init__(self, comp_type, statements=None, outline_str=None):

        self.type = comp_type

        if statements is None:
            statements = []
        self._statements = statements

        if outline_str is None:
            outline_str = ''
        self.outline_str = outline_str

    def implement(self, workchain):
        """Add the statements comprising this component to the WorkChainTemplate."""
        for statement in self._statements:
            workchain.blocks[statement.block_type].add_statement(statement)

    def remove(self, workchain):
        """Remove all statements from their respective list."""
        for statement in self._statements:
            workchain.blocks[statement.block_type].remove(statement)

    def add_link(self, keyword, value):
        """Create a link to another component by setting the keyword in a statement to a common value."""
        for statement in self._statements:
            if keyword in statement.keywords:
                statement.modify(keyword, value)


class IOComponent(Component):

    def add_link(self, keyword, value):
        pass

