from flask import Flask, render_template, jsonify, request
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
        try:
            execution: str = ""
            # Save the locals so we can find the difference after executing the user's line
            execution += "globals()['_locals'] = {k:v for k, v in locals().items()};"
            execution += str(line) + ";"
            # Fancy way of finding the difference in the local variables
            execution += "new_keys = {k: v for k, v in set(locals().items()) ^ set(globals()['_locals'].items())};"
            # Add all of the locals into the globals
            execution += "globals().update(new_keys);"
            # Remove the tracked old locals
            execution += "globals().pop('_locals');"
            
            # Finally, execute what we put together above
            exec(execution, globals(), locals())
        except Exception as e:
            # The user failed - help them!
            self._help_the_user(line, e)
    
    def _help_the_user(self, line, e):
        print(e)

# Static shell instance
ada = AdaShell()

@app.route('/')
def hello_world():
    return render_template("foo.html")

@app.route("/process", methods=["POST"])
def process():
    # Run the line through Ada
    with CaptureStdout() as ada_output:
        ada.process_line(request.form['lineEdit'])

    # Send back output string
    json_kwargs = dict(
        output=ada_output
    )
    return jsonify(**json_kwargs)

if __name__ == '__main__':
    AdaShell().cmdloop()
