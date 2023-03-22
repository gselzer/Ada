import cmd
from turtle import *

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
        

if __name__ == '__main__':
    AdaShell().cmdloop()
