from docstring_parser import DocstringMeta, parse
from typing import List
from flask import Flask, render_template, jsonify, request, make_response

app = Flask(__name__)
import atexit, cmd, io, sys, tempfile, re, os
from types import ModuleType
import json

# Do some flask app config
temp_upload_dir = tempfile.TemporaryDirectory(dir='.') # Create temp folder at webroot
app.config['upload_folder'] = temp_upload_dir.name

def on_exit():
    temp_upload_dir.cleanup()
atexit.register(on_exit)

class CaptureStdout(list):
    """
        Stolen from [here](https://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call)
    """
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = io.StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout   

class AdaShell(cmd.Cmd):
    intro = 'Ada Shell is happy to help!.   Type help or ? to list commands.\n'
    prompt = '(ada) '
    file = None

    def default(self, line):
        """
        Default Ada routine. 

        Each line is evaluated within the interpreter, along with some pre- and post-processing to update the global variables

        :param line: The line to execute
        """
        self.process_line(line)
    
    def process_line(self, line):
        """
        Processes a single command, returning a dictionary to be passed to the webpage.

        :para line: The line to execute
        :returns: A dictionary
        """
        # Apparently defining this locally really screws with the exec call below?
        out_dict = {
            "excepted": False,  # Did the input result in an exception?
            "output": None      # Output string to display for the user
        }
        try:
            execution = f"{line}\n"
            # Add new locals to globals so we can use them later - the only one we DON'T want is 'line'
            execution += """for k, v in locals().copy().items():
                if k != "line":
                    globals()[k] = v
            """
            execution += f"\n{line}\n"
            def do_exec():
                # Finally, execute what we put together above
                # exec(execution, globals(), dict(line = line))
                # result = eval(compile(execution, '<string>', 'exec'), globals(), dict(line = line))
                try: 
                    new_vars = {}
                    print(eval(compile(line, '<string>', 'eval'), globals(), new_vars))
                    globals().update(new_vars)
                except SyntaxError as e:
                    new_vars = {}
                    exec(compile(line, '<string>', 'exec'), globals(), new_vars)
                    globals().update(new_vars)
            
            with CaptureStdout() as output:
                do_exec()
            out_dict["output"] = output
        except Exception as e:
            # The user failed - help them!
            out_dict["excepted"] = True
            print(e)
            out_dict["output"] = self._help_the_user(line, e)
        return out_dict
    
    def _help_the_user(self, line: str, e: Exception):
        # If the user hasn't 
        help_pattern = re.compile("^[\s\(]")
        if not help_pattern.search(line):
            return self._help_api(line, e)

        return json.dumps(e, indent = 4) 
    
    def _help_api(self, line: str, e: Exception):
        results = {}
        parts = line.split('.')
        if len(parts) == 1:
            # look through all modules
            modules = [v for k, v in globals().items() if isinstance(v, ModuleType)]
        else:
            module = globals()
            try:
                for part in parts[:-1]:
                    module = module[part]
                    # TODO: Another place to help
            except Exception as e:
                return ""
            modules = [module]
        for module in modules:
            for field in getattr(module, "__all__", []): 
                if parts[-1] in field:
                    metadata = {}
                    doc = getattr(module, field).__doc__
                    metadata["doc"] = doc
                    data = parse(doc)
                    try:
                        metadata["description"] = data.short_description
                    except Exception:
                        metadata["description"] = ""
                    try:
                        metadata["parameters"] = [(param.arg_name, param.description) for param in data.params]
                    except Exception:
                        metadata["parameters"] = ""
                    try:
                        metadata["returns"] = [(data.returns.return_name, data.returns.description)]
                    except Exception:
                        metadata["returns"] = ""
                    try:
                        metadata["see_also"] = self._split_section(next((item.description for item in data.meta if item.args == ["see_also"]), ""))
                    except Exception:
                        metadata["see_also"] = ""
                    try:
                        metadata["Examples"] = [e.snippet.split("\n") for e in data.examples]
                    except Exception:
                        metadata["Examples"] = ""
                    results[f"{module.__name__}.{field}"] = metadata
        return json.dumps(results, indent = 4)
    
    def _get_see_also(self, data):
        for item in data.meta:
            if isinstance(item, DocstringMeta):
                return item
        return None
    
    def _split_section(self, section: str) -> List:
        """
        Partitions sections formatted along the following sytax:

        key: type<, optional>`
            description
        
        Returns a list of tuples, where each element describes an element that was documented like the above
        """
        section_elements = []
        section_split = [s.strip() for s in re.split('([a-zA-Z_]*) :', section.strip())]
        for i in range(1, len(section_split), 2):
            section_elements.append((section_split[i], section_split[i+1]))
        return section_elements

    def _split_examples(self, example_str):
        examples = example_str.split('\n\n')
        examples = [example.split('\n') for example in examples]
        # Split examples into blocks
        # Delete output strings
        for example in examples:
            idxToRemove = []
            for i in range(len(example)):
                example[i] = example[i].strip()
                if not example[i].startswith(">>>"):
                    idxToRemove.append(i)
            idxToRemove.reverse()
            for idx in idxToRemove:
                example.pop(idx)
        return examples

# Simple shell used for running example code snippets
class ExampleShell(cmd.Cmd):
    def default(self, line):
        self.process_line(line)
    
    def process_line(self, line):
        out_dict = {
            "excepted": False, 
            "output": None    
        }
        execution = str(line) + "\n"
        execution += """for k, v in locals().copy().items():
            if k != "line":
                globals()[k] = v
        """
        try:
            out_dict["output"] = eval(line, globals())
        except:
            exec(execution, globals(), dict(line = line))
        
        # with CaptureStdout() as output:

        # print(f'output: {output}')
        # out_dict["output"] = output
        return out_dict

# Static shell instance
ada = AdaShell()

@app.route('/')
def hello_world():
    return render_template("foo.html")

@app.route("/somesupersneakyprocessurlplsdontchange", methods=["POST"])
def somesupersneakyprocessurlplsdontchange():
    # Run the line through Ada
    ada_dict = ada.process_line(request.form['lineEdit'])

    # Send back output
    return jsonify(**ada_dict)

@app.route("/somesupersneakyuploadplsdontchange", methods=["POST"])
def somesupersneakyuploadplsdontchange():
    file = request.files['image']

    # Find filename to save as
    filename = file.filename # Technically should validate this for security purposes
    
    # Save image
    save_path = os.path.join(app.config['upload_folder'], filename)
    file.save(save_path)

    response = {
        "filename": filename,
        "image_path": save_path
    }
    return jsonify(**response)

# Run example code
@app.route("/somesupersneakyrunexampleplsdontchange", methods=["POST"])
def somesupersneakyrunexampleplsdontchange():
    sh = ExampleShell()
    sh.process_line("import numpy as np") # NEED TO CHANGE HERE

    output = []
    lineCount = request.form.get('lineCount')
    for i in range(int(lineCount)):
        temp = sh.process_line(request.form.get(str(i)))["output"]
        if temp is not None:
            output.append(repr(temp))
    return jsonify(output = output)


if __name__ == '__main__':
    AdaShell().cmdloop()
