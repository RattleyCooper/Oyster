

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


class ThreadControl(object):
    def __init__(self):
        self.control_dictionary = {}
        self.loop_control = None


class LoopController(object):
    def __init__(self):
        self.should_break = False
        self.should_return = False
        self.should_continue = False
        self.return_value = None


class LoopControl(object):
    """
    Factory for LoopController objects.  Makes it easier to write code that uses a loop controller.

    Usage changes from:

        lc = LoopController()
        lc.should_break = True
        return lc

    to:

        lc = LoopControl()
        return lc.should_break()
    """

    def should_break(self):
        """
        Return a breaking loop controller.

        :return:
        """

        lc = LoopController()
        lc.should_break = True
        return lc

    def should_continue(self):
        """
        Return a continuing loop controller

        :return:
        """

        lc = LoopController()
        lc.should_continue = True
        return lc

    def should_return(self, value):
        """
        Return a returning loop controller.

        :param value:
        :return:
        """

        lc = LoopController()
        lc.should_return = True
        lc.return_value = value
        return lc


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
            plugin = module.Plugin()
        except AttributeError:
            return False

        # Remove the invocation command from the rest of the data.
        command = data[invocation_length:]
        result = plugin.run(self, command)
        plugin_ran = True
        return plugin_ran, result

    def process_plugins(self, plugin_list, data):
        """
        Process plugins to see if the data should be intercepted.

        :param self:
        :param plugin_list:
        :param data:
        :return:
        """

        if plugin_list:
            plugin_ran = False
            result = False
            for module in plugin_list:
                results = False

                invocation_length = len(module.Plugin.invocation)
                invocation_type = type(module.Plugin.invocation)

                if invocation_type == list or invocation_type == tuple:
                    invocations = list(module.Plugin.invocation)
                    invocations.sort(key=len)
                    invocations.reverse()
                    for invocation in invocations:
                        invocation_length = len(invocation)
                        if data[:invocation_length] == invocation:
                            results = self.run_plugin(module, data, invocation_length)
                            break

                elif data[:invocation_length] == module.Plugin.invocation:
                    if module.Plugin.enabled or (hasattr(module.Plugin, 'required') and module.Plugin.required):
                        results = self.run_plugin(module, data, invocation_length)

                if not results:
                    continue
                plugin_ran, result = results

            return plugin_ran, result

