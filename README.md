# Workchain-composer

This is a tool for programmatically writing Aiida WorkChains by composing them from template components stored in a database
with the main goal of simplyfing the development of new and complex WorkChains. The idea behind it is to represent the 
WorkChain as a node graph of components that can then be implemented as a python script. This might ultimately allow people with only basic python or programming knowledge to develop WorkChains with a CLI or GUI.

## Components

A component in this node graph can have `inputs`, `outputs` and a method that will operate on the inputs and return the outputs.
The inputs and outputs of the components have to be connected to let two components operate on the same object. The three types of components, that a WorkChain can consist of, are:

- `Input`: the input of a WorkChain showing up as `spec.input(...)`. This type of node only has outputs. 
- `Output`: the output of WorkChain showing up as `spec.output(...)`. This type of node only has inputs.
- `Method`: one of the class methods comprising the outline of the WorkChain. These nodes will take their inputs from the context, do something with them and then put their outputs into the context. 

Note that a `Method` can be a whole WorkChain by itself, when taking it's inputs from the context and then submitting another
WorkChain with those inputs. Beyond these basic components there are two more required for the blocks in the outline:

- `Block` This can be any of the `_while`, `_if`, `_for` constructs taking a `Condition` as an input and iterating over all `Methods` inside the block.
- `Condition` A method that takes its inputs from the context but returns a bool.  

## Component database

While `Input`, `Output`, and `Block` components are generated programmatically, `Method` and `Condition` components or their templates
need to be stored in a database from where their behaviour can be copied. Currently the database consists of three python files 
- `methods.py`
- `conditions.py`
- `outline_methods.py`
in which all the methods are stored as templates like e.g.
```
def ExampleMethod(self):
    """
    Example method showcasing the general shape of outline method components:

    - Take inputs from the ctx.
    - Obtain outputs based on inputs.
    - put outputs into the context.
    """
    input1 = self.ctx.${input1}
    output1 = input1
    self.ctx.${output1} = input1
```
Each component can be retrieved from the database by their name, which also implies that method names should be unique. Note that the method templates make use of local variables `input1`, `output1` and variables that are stored in the context like `${input1}`. The latter represent the inputs and outputs of a component node and their name will be replaced, when linking two nodes.

__TODO:__ The database should be more modular allowing for loading different module files and retrieving components based on 
the path e.g. `example_module.example_omponent`.

__TODO:__ In a very far future the database could become part of the Aiida database, by storing compnent templates as nodes.

## Example usages

The first example will be creating the `AddAndMultiplyWorkChain` from the examples in the Aiida documentation. For this we
require the following template methods:
```
def add(self):
    self.ctx.${output1} = self.ctx.${input1} + self.ctx.${input2}

def multiply(self):
    self.ctx.${output1} = self.ctx.${input1} * self.ctx.${input2}

def result(self):
    self.out(${input1}, Int(self.ctx.${input1}))
```
These methods are stored in the database, which currently manifests as `outline_methods.py` in the repository. With these we 
can start creating our WorkChain:

```
In [1]: from composer import WorkChainComposer

In [2]: wcc = WorkChainComposer()
```
The constructor for the WorkChainComposer will load the component database and nothing more at the moment. In order to create a new
WorkChain we have to call
```
In [3]: wcc.create_new(name='AddAndMultiplyWorkChain')
```
Creating a new workChain requires a name for the new WorkChain sub class. By default it will inherit from `aiida.work.workchain.WorkChain`. 
How to inherit from another base class will be shown in the second example below. After this we can start adding a number of components. In this case the inputs and outputs for the WorkChain as well as the the two methods comprising the outline

```
In [4]: wcc.add_component(comp_type='input', init={'name': 'a', 'valid_type': 'Int'})

In [5]: wcc.add_component(comp_type='input', init={'name': 'b', 'valid_type': 'Int'})

In [6]: wcc.add_component(comp_type='input', init={'name': 'c', 'valid_type': 'Int'})

In [7]: wcc.add_component(comp_type='output', init={'name': 'result', 'valid_type': 'Int'})

In [8]: wcc.add_component(comp_type='outline_method', init={'name': 'add'})

In [9]: wcc.add_component(comp_type='outline_method', init={'name': 'multiply'})

In [10]: wcc.add_component(comp_type='outline_method', init={'name': 'result'})
```
Now that we have all the components, their inputs and outputs need to be connected. This can be done by using the
`link_components` method, that takes the index of the component with the outputs, the index of the specific output, the index of 
the component with the input, the index of the specific input as well as the name for the variable as a string.
```
In [11]: wcc.link_components(1, 1, 5, 1, 'a')

In [12]: wcc.link_components(2, 1, 5, 2, 'b')

In [13]: wcc.link_components(3, 1, 6, 2, 'c')

In [14]: wcc.link_components(5, 1, 6, 1, 'sum')

In [15]: wcc.link_components(6, 1, 7, 1, 'result')
```
Now that all the components are linked properly we can implement the WorkChain:
```
In [16]: wcc.implement()
from aiida.work.workchain import WorkChain

class AddAndMultiplyWorkChain(WorkChain):

    @classmethod
    def define(cls, spec):

        spec.input(name=a, valid_type=Int)
        spec.input(name=b, valid_type=Int)
        spec.input(name=c, valid_type=Int)

        spec.outline(
            cls.add,
            cls.multiply,
            cls.result,
        )

        spec.output(name=result, valid_type=Int)

    def add(self):
        self.ctx.sum = self.ctx.a + self.ctx.b
    
    def multiply(self):
        self.ctx.result = self.ctx.sum * self.ctx.c
    
    def result(self):
        self.out('result', Int(self.ctx.result))
```
__TODO:__ Advanced users may notice that the above `WorkChain` method is lacking a setup method putting the inputs of the WorkChain into the 
context and therefore would not actually work. This is a consequence of turning the methods into templates instead of just copying and 
pasting. Note that above `add` method would work for all objects with an overloaded '+' operator, only if those two objects can be
found in the context. The original add method from the Aiida example would take its inputs directly from 'WorkChain.inputs' instead.

The second example is a WorkChain with a slightly more complicated outline using a `_while_block`. Again we will start by loading the
the module and creating a new WorkChain this time inheriting from `another.workchain.BaseWorkChain`
```
In [1]: from composer import WorkChainComposer

In [2]: wcc = WorkChainComposer()

In [3]: wcc.create_new(name='ExampleWorkChain', base_class='another.workchain.BaseWorkChain')
```
Using the optional `base_class` argument will automatically create the correct `from ... import ...` statement. Next we will add two
components, one being a normal method and one being an outline block.

```
In [4]: wcc.add_component(comp_type='outline_method', init={'name': 'some_method'})

In [5]: wcc.add_component(comp_type='block', init={'name': '_while', 'argument': 'condition'})
```
The `argument` keyword tells the composer which condition to load from the database and pass as an argument to the `_while(...)`. 
```
In [6]: wcc.add_component(comp_type='outline_method', init={'name': 'another_method'})
```
A method (or even another block) can be inserted within a block by providing the index where the method should be inserted into the
list of components as additional argument. 
```
In [7]: wcc.add_component(comp_type='outline_method', init={'name': 'yet_another_method'}, 4)
```
In this case the relevant components are `1: some_method`, `2: condition`, `3: start while_block`, `4: end while_block`. So inserting 
at index 4 will put `yet_another_method` into the `_while` block, which we can check by implementing our WorkChain:
```
In [8]: wcc.implement()
from another.workchain import BaseWorkChain
from aiida.work.workchain import _while

class ExampleWorkChain(BaseWorkChain):

    @classmethod
    def define(cls, spec):

        spec.outline(
            cls.some_method,
            _while(cls.condition)(
                cls.yet_another_method,
            ),
            cls.another_method,
        )

    def some_method(self):
        pass
    
    def condition(self):
        return True
    
    def another_method(self):
        pass
    
    def yet_another_method(self):
        pass
```

__TODO:__ Currently there is no intuitive way to find out where a method can be inserted. `wcc.show_components` does only list all of the
components, but since there is no `__repr__` for the `Component` class, that print out is not that helpful.
