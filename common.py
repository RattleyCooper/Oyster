

def safe_input(display_string):
    """
    Get input from user.  Should work with python 2.7 and 3.x

    :param display_string:
    :return:
    """

    try:
        x = raw_input(display_string)
    except NameError:
        x = input(display_string)

    return x


class LoopEvent(object):
    """
    Factory for LoopEvent objects.  LoopEvent objects are used to control the main
    loop of a shell(Oyster or client) from with a Plugin.  Just return one of the
    LoopEvent objects(LoopContinueEvent, LoopReturnEvent(data), LoopBreakEvent).

    This example will do everything necessary to make the Oyster shell loop stop:

        from common import LoopEvent

        class Plugin(object):
            invocation = 'test'
            version = 'v1.0'
            enabled = True

            def run(server, data):
                print('< Shutting down. >')

                # Boot up a client in order to stop the server's listener thread's
                # self.sock.accept() call from blocking and allow the ShutdownEvent
                # to be processed.
                Client(port=server.port, echo=False)

                # Tell the listener to shutdown
                server.shutdown_event.set()

                # Tell the Oyster shell's main loop it should `break`.
                return LoopEvent.should_break()
    """

    @staticmethod
    def should_break():
        """
        Return a breaking loop event.

        :return:
        """

        return LoopBreakEvent()

    @staticmethod
    def should_continue():
        """
        Return a continuing loop event

        :return:
        """

        return LoopContinueEvent()

    @staticmethod
    def should_return(value):
        """
        Return a returning loop event.

        :param value:
        :return:
        """

        return LoopReturnEvent(value)


class LoopContinueEvent(LoopEvent):
    pass


class LoopBreakEvent(LoopEvent):
    pass


class LoopReturnEvent(LoopEvent):
    def __init__(self, value):
        self.value = value


class PluginRunner(object):
    def run_plugin(self, module, data, invocation_length):
        """
        Run the plugin in the given module.

        :param self:
        :param module:
        :param data:
        :param invocation_length:
        :return:
        """

        try:
            plugin = module.Plugin
        except AttributeError:
            return False

        # Remove the invocation command from the rest of the data.
        command = data[invocation_length:]
        try:
            result = plugin.run(self, command)
        except TypeError:
            result = plugin().run(self, command)
        plugin_ran = True
        return plugin_ran, result

    def process_plugins(self, plugin_list, data, help_mode_on=False):
        """
        Process plugins to see if the data should be intercepted.

        :param self:
        :param plugin_list:
        :param data:
        :param help_mode_on:
        :return:
        """

        if plugin_list:
            plugin_ran = False
            result = False
            for module in plugin_list:
                results = False

                invocation_length = len(module.Plugin.invocation)
                invocation_type = type(module.Plugin.invocation)

                if not module.Plugin.enabled and not hasattr(module.Plugin, 'required'):
                    continue

                if hasattr(module.Plugin, 'required') and not module.Plugin.required:
                    continue

                if invocation_type == list or invocation_type == tuple:
                    invocations = list(module.Plugin.invocation)
                    invocations.sort(key=len)
                    invocations.reverse()
                    for invocation in invocations:
                        invocation_length = len(invocation)
                        if data[:invocation_length] == invocation:
                            if help_mode_on:
                                help(module.Plugin)
                            results = self.run_plugin(module, data, invocation_length)
                            break

                elif data[:invocation_length] == module.Plugin.invocation:
                    if help_mode_on:
                        help(module.Plugin)
                    results = self.run_plugin(module, data, invocation_length)

                if not results:
                    continue
                plugin_ran, result = results

            return plugin_ran, result

