import shlex


class Plugin(object):
    """
    Help v1.0

    Use python's built in `help` function on Plugins.

    Invocation:

        help

    Commands:

        help -m                 -   Enter help mode.  Any plugin that is
                                    used will have `help` called on it.
                                    help - m must be called again to
                                    exit help mode.

        help -p {plugin}        -   Look for the given {plugin} and print
                                    the help on it.

        help -ps {plugin}       -   Look for the given shell {plugin} and
                                    print the help on it.

        help -po {plugin}       -   Look for the given outgoing {plugin}
                                    and print the help on it.

    Example:

        Here we will check out the Help module(that's this one!).

        Oyster> help -p Help
        # Too much output so I am not going to put it here
        Oyster> help -m
        < Help mode enabled. Run help -m to disable. >
    """

    version = 'v1.0'
    invocation = 'help'
    enabled = True

    @staticmethod
    def run(server, data):
        """
        Parse/Handle the command.

        :param server:
        :param data:
        :return:
        """

        args = shlex.split(data)

        if not args:
            print('< Expected some arguments. >')
            return

        if args[0] == '-m':
            server.help_mode = True if not server.help_mode else False
            print('< Help mode enabled. Run help -m to disable. >' if server.help_mode else '< Help mode disabled. >')
            return

        if args[0] == '-p':
            Plugin.plugin_help(server, args[1:])
            return

        if args[0] == '-ps':
            Plugin.shell_plugin_help(server, args[1:])
            return

        if args[0] == '-po':
            Plugin.outgoing_plugin_help(server, args[1:])
            return

        return

    @staticmethod
    def plugin_help(server, args):
        """
        Print the help for any server-side plugin.

        :param server:
        :param args:
        :return:
        """

        shp = server.get_shell_plugins()
        sp = server.get_outgoing_plugins()
        pl = shp + sp
        shp_names = [i.__name__ for i in pl]

        for i, name in enumerate(shp_names):
            if args[0] in name:
                help(pl[i].Plugin)
        return

    @staticmethod
    def outgoing_plugin_help(server, args):
        """
        Print the help for all outgoing plugins

        :param server:
        :param args:
        :return:
        """

        shp = server.get_outgoing_plugins()
        shp_names = [i.__name__ for i in shp]

        for i, name in enumerate(shp_names):
            if args[0] in name:
                help(shp[i].Plugin)
                return

    @staticmethod
    def shell_plugin_help(server, args):
        """
        Print the help for all shell plugins

        :param server:
        :param args:
        :return:
        """

        shp = server.get_shell_plugins()
        shp_names = [i.__name__ for i in shp]

        for i, name in enumerate(shp_names):
            if args[0] in name:
                help(shp[i].Plugin)
                return


