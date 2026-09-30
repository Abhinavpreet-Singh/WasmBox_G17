import extism

@extism.plugin_fn
def greet():
    extism.set_output("Hello from WasmBox!")
