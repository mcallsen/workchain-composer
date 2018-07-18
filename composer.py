from template import WorkChainTemplate
from component_database import ComponentDatabase


class WorkChainComposer(object):

    def __init__(self):
        self._workchain_template = None
        self._database = ComponentDatabase(['methods.py', 'conditions.py', 'outline_methods.py'])

    def create_new(self, name, base_class=None):
        """
        Create a new empty WorkChainTemplate.

        :param name: Name of the new WorkChain class.
        :param base_class: The base class for this WorkChain.

        If base_class is not provided 'aiida.work.workchain.WorkChain' will
        be used by default.
        """

        if base_class is None:
            base_class = 'aiida.work.workchain.WorkChain'

        if not self._workchain_template:
            self._workchain_template = WorkChainTemplate()

        self.add_component('class_definition', {'name': name, 'import': base_class})

    def implement(self):
        """Implement the python script representation of the WorkChain."""
        self._workchain_template.write()

    def add_component(self, comp_type, init, index=None):
        """
        Add a component to WorkChainTemplate.

        :param comp_type: The type of the component to add. Valid options are:
                          `input`, `output`, `method`, `condition`, `block`.
        :param init: Dictionary containing key, value pairs required for initialising the component.
        :param index: Index at which to insert the component into the outline. By default it will be
                      appended at the end.
        """
        new_components = self._database.get_component(comp_type, init)
        if new_components:
            self._workchain_template.add_components(new_components, index)

    def remove_component(self, index):
        """Remove the component at index from the WorkChainTemplate."""
        self._workchain_template.remove_component(index)

    def link_components(self, output_node, output_index, input_node, input_index, name):
        """
        Link two components by using the same variable from the context.

        :param output_node: Index of the output node.
        :param output_index: Index of the output on the output node.
        :param input_node: Index of the input node.
        :param input_index: Index of the input on the input node.
        :param name: The name for the common variable.
        """
        self._workchain_template.link_components(output_node, output_index, input_node, input_index, name)

    def show_outline(self):
        """Show the current outline of the WorkChain."""
        self._workchain_template.show_outline()
