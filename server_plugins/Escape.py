import shlex


class Plugin(object):
    """
    Escape commands with a \ if you have a plugin that would
    normally override a
    """
    version = 'v1.0'
    invocation = '\\'
    enabled = True

    def run(self, server, data):
        args = shlex.split(data)

        if not args:
            pass

        try:
            response = server.send_command('\\' + data)
        except BrokenPipeError as err:
            print(err)
            return
        print(response, end='')
        return
