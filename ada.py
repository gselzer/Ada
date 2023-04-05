from flask import Flask, render_template, jsonify, request
app = Flask(__name__)
import cmd, io, sys, re
from types import ModuleType

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
    
    def _help_the_user(self, line: str, e: Exception):
        # If the user hasn't 
        help_pattern = re.compile(r"\s\.\(")
        if not help_pattern.match(line):
            return self._help_api(line, e)

        return str(e)
    
    def _help_api(self, line: str, e: Exception):
        results = {}
        for k, v in globals().items():
            if isinstance(v, ModuleType):
                for field in getattr(v, "__all__", []): 
                    if line in field:
                        metadata = {}
                        metadata["doc"] = getattr(v, field).__doc__
                        results[f"{k}.{field}"] = metadata
        return str(results)

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

if __name__ == '__main__':
    AdaShell().cmdloop()
