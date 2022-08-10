import json
from ansible.plugins.callback import CallbackBase

from suitable.results import RunnerResults


class SilentCallbackModule(CallbackBase):
    """
    A callback module that does not print anything, but keeps tabs
    on what's happening in an Ansible play.
    """

    def __init__(self):
        self.unreachable = {}
        self.contacted = {}

    def v2_runner_on_ok(self, result):
        # type: (RunnerResults) -> None
        self.contacted[result._host.name] = {"success": True, "result": result._result}

    def v2_runner_on_failed(self, result, ignore_errors=False):
        # type: (RunnerResults, bool) -> None
        self.contacted[result._host.name] = {"success": False, "result": result._result}

    def v2_runner_on_unreachable(self, result):
        # type: (RunnerResults) -> None
        self.unreachable[result._host.name] = result._result


class ResultsCollectorJSONCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in.

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin.
    """

    def __init__(self, *args, **kwargs):
        super(ResultsCollectorJSONCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.host_unreachable[host.get_name()] = result

    def v2_runner_on_ok(self, result, *args, **kwargs):
        """Print a json representation of the result.

        Also, store the result in an instance attribute for retrieval later
        """
        host = result._host
        self.host_ok[host.get_name()] = result
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        self.host_failed[host.get_name()] = result
