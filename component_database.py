from component import Component, IOComponent
from statement import Statement


def read_database(file_name):
    """
    Read the method templates from a file.

    The first line contains the arguments for this method. All other lines
    contain the methods body.
    """
    with open(file_name, 'r') as file_obj:
        lines = file_obj.readlines()

    methods = {}
    name = ''
    for line in lines:
        if 'def' in line.split():
            # found the start of a new method
            name = line.split()[1].split('(')[0]
            arguments = line.split()[1].split('(')[1].split(')')[0]
            methods[name] = [arguments]
            continue

        # This is a line that is not part of a definition.
        methods[name].append(line)

    return methods


class ComponentDatabase(object):
    """Provide an interface to get components from a database"""

    def __init__(self, file_names):
        self._methods = {}
        for file_name in file_names:
            name = file_name.split('.')[0]
            self._methods[name] = read_database(file_name)

    def get_component(self, comp_type, init):
        """
        Get a component from the database.

        :param comp_type: Type of the Component. Must be in COMPONENT_TYPES.
        :param init: Name of the Component.

        This method will call the specialised version of _get_component based
        on the components type.
        """

        add_import = init.get('import')
        if add_import:
            init['import'] = create_import_statement(add_import)

        return getattr(self, '_get_component_' + comp_type)(comp_type, init)

    def _get_component_input(self, comp_type, init):
        """Input component spec.input(...)."""
        return self._get_component_io(comp_type, init)

    def _get_component_output(self, comp_type, init):
        """Output component spec.output(...)."""
        return self._get_component_io(comp_type, init)

    @staticmethod
    def _get_component_io(comp_type, inputs):
        """Generic get for both types of spec_items."""

        arguments = []
        # Assemble the string, that will be passed as an argument
        # in spec.item(...).
        for item in ['name', 'valid_type']:
            if item in inputs:
                arguments.append('{0}={1}'.format(item, inputs.get(item)))

        init = {'item_type': comp_type, 'arguments': ', '.join(arguments)}
        block_type = 'define_' + comp_type + 's'

        statements = []
        if inputs.get('import'):
            statements.append(inputs.get('import'))

        statements.append(Statement('spec_item', block_type, init=init))

        return [IOComponent(comp_type, statements)]

    def _get_component_condition(self, comp_type, init):
        """
        Get a condition type method from the database.
        """
        if init is None:
            init = {}
        init['block_type'] = 'class_methods'

        return self._get_component_method(comp_type, init)

    def _get_component_outline_method(self, comp_type, init):

        if init is None:
            init = {}
        init['block_type'] = 'class_methods'

        return self._get_component_method(comp_type, init)

    def _get_component_method(self, comp_type, init):
        """Get a method type component."""

        name = init.get('name')
        block_type = init.get('block_type', 'methods')

        lines = self._methods[comp_type + 's'].get(name)
        if lines is None:
            return None

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

        return [Component(comp_type, statements=statements, outline_str='cls.' + name + ',')]

    @staticmethod
    def _get_component_class_definition(comp_type, init):
        """Get a class definition component."""

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

        statements.append(create_import_statement(init['base_class']))

        return [Component(comp_type, statements)]

    def _get_component_block(self, comp_type, init):
        """
        Add a block of components to the outline.

        If the condition is in the methods database it will also add the condition
        as component to the WorkChainTemplate. The import for the outline block
        (_while, _for, _if ...) will be created if `add_import`: ... is in init.
        """
        components = []
        condition = init.get('argument')

        if condition in self._methods['conditions']:
            init.update({'argument': 'cls.' + condition})
            components += self._get_component_condition('condition', {'name': condition})

        components += ComponentDatabase._get_component_start_block('begin_block', init)
        components += ComponentDatabase._get_component_end_block('end_block', init)
        return components

    @staticmethod
    def _get_component_start_block(comp_type, init):
        """Get a start_block component."""

        name = init.get('name')
        argument = init.get('argument')

        statements = []
        if init.get('import'):
            statements.append(init.get('import'))

        return [Component(comp_type, statements=statements, outline_str=name+'({})('.format(argument))]

    @staticmethod
    def _get_component_end_block(comp_type, init):
        """Get an end_block component."""
        return [Component(comp_type, outline_str='),')]


def create_import_statement(import_str):
    """Create an import statement."""
    class_path = '.'.join(import_str.split('.')[:-1])
    class_name = import_str.split('.')[-1]
    return Statement('from_import', 'from_import', init={
            'path': class_path,
            'items': class_name
        })
