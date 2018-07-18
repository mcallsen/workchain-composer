from component import IOComponent, ClassMethodComponent, ClassDefinitionComponent, BeginBlockComponent, EndBlockComponent
from statement import Statement

WORKCHAIN_IMPORT='aiida.work.workchain.'

COMPONENT_TYPES = {
    'outline_method': ClassMethodComponent,
    'condition': ClassMethodComponent,
    'input': IOComponent,
    'output': IOComponent,
    'class_definition': ClassDefinitionComponent,
}


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

        """

        # Setup additional imports if required.
        add_import = init.get('import')

        if add_import:
            init['base_class'] = add_import
            init['import'] = create_import_statement(add_import)

        if comp_type == 'block':
            init['import'] = create_import_statement(WORKCHAIN_IMPORT + init.get('name'))
            return self._get_component_block(init)

        init['_lines'] = self._get_from_database(comp_type + 's', init['name'])

        return [COMPONENT_TYPES[comp_type](comp_type, init)]

    def _get_from_database(self, comp_type, name):
        """Get an item from the database."""
        if comp_type not in self._methods:
            return None
        return self._methods[comp_type].get(name)

    def _get_component_block(self, init):
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
            components += self.get_component('condition', {'name': condition})

        components += [BeginBlockComponent(init)]
        components += [EndBlockComponent()]
        return components


def create_import_statement(import_str):
    """Create an import statement."""
    class_path = '.'.join(import_str.split('.')[:-1])
    class_name = import_str.split('.')[-1]
    return Statement('from_import', 'from_import', init={
            'path': class_path,
            'items': class_name
        })
