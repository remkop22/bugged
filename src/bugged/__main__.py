from bugged import GenericClient, BuggedAdapter
import sys

if __name__ == '__main__':

    arguments = {}

    for i, arg in enumerate(sys.argv):
        if arg[0] == '-':
            if len(sys.argv) == i - 1 or sys.argv[i + 1][0] == '-':
                arguments[arg[1:]] = True
            else:
                arguments[arg[1:]] = sys.argv[i + 1]

    client = GenericClient()
    adapter = BuggedAdapter((arguments['host'], int(arguments['port'])), client)
    adapter.connect()
    adapter.initialize()

