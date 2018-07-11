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
The constructor for the WorkChainComposer will load the component database. 
```
In [3]: wcc.create_new('AddAndMultiplyWorkChain')
```
Creating a new workChain requires a name for the new WorkChain sub class. By default it will inherit for `aiida.work.workchain.WorkChain`. 
How to inherit from another base class will be shown in the second example blow.
