# workchain-composer

This is a tool for programmatically writing Aiida WorkChains by composing them from template components stored in a database
with the main goal of simplyfing the development of new and complex WorkChains. The idea behind it is to represent the 
WorkChain as a node graph of components that can then be implemented as a python script. 

## Components

A component in this node graph can 
have `inputs`, `outputs` and a method that will operate on the inputs and return the outputs. The inputs and outputs of the 
components have to be connected to let two components operate on the same object. The three types of components, that
a WorkChain can consist of, are:

- `Input`: the input of a WorkChain showing up as `spec.input(...)`. This type of node only has outputs. 
- `Output`: the output of WorkChain showing up as `spec.output(...)`. This type of node only has inputs.
- `Method`: one of the class methods comprising the outline of the WorkChain. These nodes will take their inputs from the context, do something with them and then put their outputs into the context. 

Note that a `Method` can be a whole WorkChain by itself, when taking it's inputs from the context and then submitting another
WorkChain with those inputs. Beyond these basic components there are two more required for the blocks in the outline:

- `Block` This can be any of the `_while`, `_if`, `_for` constructs taking a `Condition` as an input and iterating over all `Methods` inside the block.
- `Condition` A method that takes its inputs from the context but returns a bool.  

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
In [3]: wcc.create_new('AddAndMultiplyWorkChain')
```
Creating a new workChain requires a name for the new WorkChain sub class. By default it will inherit for `aiida.work.workchain.WorkChain`. 
How to inherit from another base class will be shown in the second example below. After this we can start adding a number of components. In this case the inputs and outputs for the WorkChain as well as the the two methods comprising the outline

```
In [4]: wcc.add_component('input', {'name': 'a', 'valid_type': 'Int'})

In [5]: wcc.add_component('input', {'name': 'b', 'valid_type': 'Int'})

In [6]: wcc.add_component('input', {'name': 'c', 'valid_type': 'Int'})

In [7]: wcc.add_component('output', {'name': 'result', 'valid_type': 'Int'})

In [8]: wcc.add_component('outline_method', {'name': 'add'})

In [9]: wcc.add_component('outline_method', {'name': 'multiply'})

In [10]: wcc.add_component('outline_method', {'name': 'result'})
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
