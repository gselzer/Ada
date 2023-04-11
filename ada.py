<<<<<<< Updated upstream
from flask import Flask, render_template, jsonify, request
=======
from typing import List
from flask import Flask, render_template, jsonify, request, make_response
>>>>>>> Stashed changes
app = Flask(__name__)
import cmd, io, sys

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
            execution = str(line) + "\n"
            # Add new locals to globals so we can use them later - the only one we DON'T want is 'line'
            execution += """for k, v in locals().copy().items():
                if k != "line":
                    globals()[k] = v
            """
            def do_exec():
                # Finally, execute what we put together above
                exec(execution, globals(), dict(line = line))
            
            with CaptureStdout() as output:
                do_exec()
            out_dict["output"] = output
        except Exception as e:
            # The user failed - help them!
            out_dict["excepted"] = True
            out_dict["output"] = self._help_the_user(line, e)
        return out_dict
    
<<<<<<< Updated upstream
    def _help_the_user(self, line, e):
        return str(e)
=======
    def _help_the_user(self, line: str, e: Exception):
        # If the user hasn't 
        help_pattern = re.compile(r"\s\.\(")
        if not help_pattern.match(line):
            return self._help_api(line, e)

        return json.dumps(e, indent = 4) 
    
    def _help_api(self, line: str, e: Exception):
        results = {}
        for k, v in globals().items():
            if isinstance(v, ModuleType):
                for field in getattr(v, "__all__", []): 
                    if line in field:
                        metadata = {}
                        doc = getattr(v, field).__doc__
                        metadata["doc"] = doc
                        data = [s.strip() for s in re.split('\n\n\s*[a-zA-z ]+\n\s*[-]+\n\s*', getattr(v, field).__doc__)]
                        metadata["description"] = data[0]
                        metadata["parameters"] = self._split_section(data[1])
                        metadata["returns"] = self._split_section(data[2])
                        metadata["see_also"] = self._split_section(data[3])
                        metadata["Examples"] = self._split_examples(data[4])
                        # populate_examples(data[4])
                        results[f"{k}.{field}"] = metadata
        resultsjson = json.dumps(results, indent = 4)
        return resultsjson
    
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

    # def _split_examples(self, example_str: str) -> List:
    #     examples = []
    #     ex_docs = [s.strip() for s in re.split('(\n[^>]+\n)', example_str + "\n")]
    #     for i in range(0, len(ex_docs) - 1, 2):
    #         examples.append((ex_docs[i], ex_docs[i+1]))
    #     print(examples)
    #     return examples

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
>>>>>>> Stashed changes


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
            eval(line)
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

# Run example code
@app.route("/runExample", methods=["POST"])
def runExample():
    
    sh = ExampleShell()
    sh.process_line("import numpy as np") # NEED TO CHANGE HERE

    output = ""
    lineCount = request.form.get('lineCount')
    for i in range(int(lineCount)):
        temp = sh.process_line(request.form.get(str(i)))["output"]
        # print(temp)

    # print(output)
    response = make_response(output, 200)
    response.mimetype = "text/plain"
    return response


if __name__ == '__main__':
    AdaShell().cmdloop()
