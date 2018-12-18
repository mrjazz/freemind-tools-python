import inspect
import sys
from pprint import pprint
import re


def commandliner(scope):
    commands = [i[:-8] for i in scope if i[-8:] == '_command']

    arguments = sys.argv[1:]
    if len(arguments) == 0:
        print("Empty command passed\nExisting commands are: %s" % ", ".join(commands))
        return

    # validate command
    if arguments[0] not in commands:
        print("Unknown command\nExisting commands are:\n\t" + "\n\t".join(commands))
        return

    # validate arguments
    cmd = arguments[0] + '_command'
    command_args = [i for i in inspect.signature(scope[cmd]).parameters]
    params = {}
    for i in arguments[1:]:
        res = re.match(r"""--(.*)=(.*)""", i)
        if res is None:
            print("Wrong parameter format %s, should be --param=value" % i)
            return

        if res.group(1) not in command_args:
            print("Unknown parameter %s\nExisting parameters are: %s" % (i, ", ".join(command_args)))
            return
        params.setdefault(res.group(1), res.group(2))

    # run command
    scope[cmd](**params)


if __name__ == '__main__':
    def worklog_command(day_start=None, day_end=None, developer=None, project=None, limit=-1):
        print(day_start, day_end, developer, project, limit)

    commandliner()
