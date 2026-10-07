# Benign hello-world plugin template (Extism PDK — compile in Week 2)

import extism

@extism.plugin_fn
def greet():
    extism.output_str("Hello from WasmBox!")

