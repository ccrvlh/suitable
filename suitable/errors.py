import typing as t


class SuitableError(Exception):
    """Base exception class

    Args:
        Exception (Exception): Base exception.
    """

    pass


class ModuleError(SuitableError):
    def __init__(self, module, host, result):
        # type: (str, str, dict[t.Any, t.Any]) -> None
        """Module

        :param module (str): The module
        :param host (str): The host on which the module was run.
        :param result (RunnerResults): The results of the module run.
        """
        self.module = module
        self.host = host
        self.result = result

    def __str__(self):
        output = []

        if "msg" in self.result:
            output.append("Message: {}".format(self.result["msg"]))

        if "rc" in self.result:
            output.append("Returncode: {}".format(self.result["rc"]))

        if "stdout" in self.result:
            output.append("Stdout:\n{}".format(self.result["stdout"]))

        if "stderr" in self.result:
            output.append("Stderr:\n{}".format(self.result["stderr"]))

        return "Error running '{module}' on {host}\n{output}".format(
            module=self.module, host=self.host, output="\n".join(output)
        )


class UnreachableError(SuitableError):
    """Host could not be reached.

    Args:
        SuitableError (SuitableError): Suitable raised exception.
    """

    def __init__(self, module, host):
        self.module = module
        self.host = host

    def __str__(self):
        return "{host} could not be reached".format(host=self.host)
