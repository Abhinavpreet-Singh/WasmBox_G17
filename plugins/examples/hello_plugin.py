# Benign hello-world plugin template (Extism PDK — compile in Week 2)

from extism import plugin_fn, Host

@plugin_fn
def greet():
    return "Hello from WasmBox!"
