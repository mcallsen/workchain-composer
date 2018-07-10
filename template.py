
from block import Block
from statement import Statement

# The blocks comprising the python script representing a WorkChain and their indentation level.
BLOCK_TYPES = [
    ('import_as', 0),
    ('from_import', 0),
    ('methods', 0),
    ('class_definition', 0),
    ('define', 1),
    ('define_inputs', 2),
    ('define_outline', 2),
    ('define_outputs', 2),
    ('class_methods', 1),
]

BLOCK_TEMPLATES = {
    'define': [
        ('decorator', {'name': 'classmethod'}),
        ('definition', {'keyword': 'def', 'name': 'define', 'arguments': 'cls, spec'})
    ]
}

# These are the indent modifiers for the special components in the outline.
OUTLINE_COMPONENTS = {
    'begin_block': 1,
    'outline_method': 0,
    'end_block': -1,
}


class WorkChainTemplate(object):
    """The template for a WorkChain."""

    def __init__(self, init=None):

        self._components = []
        self.blocks = {}
        self.outline = []

        for block_type, indent in BLOCK_TYPES:
            self.blocks[block_type] = Block(block_type, indent, BLOCK_TEMPLATES.get(block_type, []))

        if init is not None:
            self.blocks.update(init)

    def add_components(self, components, index=None):
        """Add a list of components to this WorkChain."""
        for i, component in enumerate(components):
            component.implement(self)
            if index is None:
                index = len(self._components) - i

            self._components.insert(index + i, component)

    def remove_component(self, index):
        """Remove a component at index."""
        if index > len(self._components):
            return
        self._components[index].remove(self)

    def link_components(self, output_node, output_index, input_node, input_index, value):
        """Link two components by setting the identifier of their input and output to a common value."""
        self._components[output_node].add_link('output' + str(output_index), value)
        self._components[input_node].add_link('input' + str(input_index), value)

    def show_components(self):
        """Show all components of this WorkChainTemplate."""
        for block_type, _ in BLOCK_TYPES:
            print '{0}:'.format(block_type)
            self.blocks[block_type].show_statements()

        print ''
        print 'Components:'
        print ''

        for component in self._components:
            print component

    def write(self):
        """Write the python script representation of the WorkChain."""

        # Create the outline first, since it has to be updated every time.
        self.create_outline()

        for block_type, _ in BLOCK_TYPES:
            self.blocks[block_type].write()

    def show_outline(self):
        """Print the outline of the WorkChain."""
        self.create_outline()
        self.blocks['define_outline'].write()

    def create_outline(self):
        """Create the outline of the WorkChain."""
        block = Block('define_outline', 2)
        indent = 1

        block.add_statement(Statement('comment', 'define_outline', init={'comment': 'spec.outline('}))

        for component in self._components:
            if component.type not in OUTLINE_COMPONENTS:
                # Component, that does not belong in the outline.
                continue

            indent += OUTLINE_COMPONENTS[component.type]

            # Add the components outline string to the outline.
            block.add_statement(Statement('comment',
                                          'define_outline',
                                          indent=indent,
                                          init={'comment': component.outline_str}
                                          ))

        block.add_statement(Statement('comment', 'define_outline', init={'comment': ')'}))

        self.blocks['define_outline'] = block






