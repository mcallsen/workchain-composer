from statement import Statement


class Component(object):
    """A Component, that can be added to a WorkChain."""

    def __init__(self, comp_type, statements=None):

        self.type = comp_type

        if statements is None:
            statements = []
        self._statements = statements

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


class ClassDefinitionComponent(Component):

    def __init__(self, comp_type, init):
        statements = []
        if init is None:
            init = dict()
            init['name'] = 'ExampleWorkChain'
            init['base_class'] = 'aiida.work.workchain.WorkChain'

        class_name = init['base_class'].split('.')[-1]

        statements.append(Statement('definition', comp_type, init={
            'keyword': 'class',
            'name': init['name'],
            'arguments': class_name,
        }))

        statements.append(init.get('import'))

        super(ClassDefinitionComponent, self).__init__(comp_type, statements)


class IOComponent(Component):

    def __init__(self, comp_type, init):

        arguments = []
        # Assemble the string, that will be passed as an argument
        # in spec.item(...).
        for item in ['name', 'valid_type']:
            if item in init:
                arguments.append('{0}={1}'.format(item, init.get(item)))

        inputs = {'item_type': comp_type, 'arguments': ', '.join(arguments)}
        block_type = 'define_' + comp_type + 's'

        statements = []
        if init.get('import'):
            statements.append(inputs.get('import'))

        statements.append(Statement('spec_item', block_type, init=inputs))

        super(IOComponent, self).__init__(comp_type, statements=statements)

    def add_link(self, keyword, value):
        pass


class OutlineComponent(Component):

    def __init__(self, comp_type, statements=None, outline_str=None):

        if outline_str is None:
            outline_str = ''
        self.outline_str = outline_str

        super(OutlineComponent, self).__init__(comp_type, statements)


class ClassMethodComponent(OutlineComponent):

    def __init__(self, comp_type, init):

        self.indent_modifier = [0, 0]

        name = init.get('name')
        block_type = 'class_methods'
        lines = init.get('_lines')

        statements = list()

        if init.get('import'):
            statements.append(init.get('import'))

        statements.append(Statement('definition', block_type, init={
            'keyword': 'def',
            'name': name,
            'arguments': lines[0],
        }))

        for line in lines[1:]:
            statements.append(Statement('line', block_type, line='${indent}' + line.rstrip()))

        super(ClassMethodComponent, self).__init__(
            comp_type,
            statements=statements,
            outline_str='cls.' + name + ','
        )


class BeginBlockComponent(OutlineComponent):

    def __init__(self, init):

        self.indent_modifier = [0, 1]

        name = init.get('name')
        argument = init.get('argument')

        statements = []
        if init.get('import'):
            statements.append(init.get('import'))

        super(BeginBlockComponent, self).__init__(
            'begin_block',
            statements=statements,
            outline_str=name+'({})('.format(argument)
        )


class EndBlockComponent(OutlineComponent):

    def __init__(self):

        self.indent_modifier = [-1, 0]

        super(EndBlockComponent, self).__init__(
            'end_block',
            outline_str='),'
        )
