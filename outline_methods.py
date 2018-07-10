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


def some_method(self):
    pass

def another_method(self):
    pass

def yet_another_method(self):
    pass

def add(self):
    self.ctx.${output1} = self.ctx.${input1} + self.ctx.${input2}

def multiply(self):
    self.ctx.${output1} = self.ctx.${input1} * self.ctx.${input2}

def result(self):
    self.out(${input1}, Int(self.ctx.${input1}))
