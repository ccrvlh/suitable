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
        self.contacted[result._host.name] = {
            'success': True,
            'result': result._result
        }

    def v2_runner_on_failed(self, result, ignore_errors=False):
        # type: (RunnerResults, bool) -> None
        self.contacted[result._host.name] = {
            'success': False,
            'result': result._result
        }

    def v2_runner_on_unreachable(self, result):
        # type: (RunnerResults) -> None
        self.unreachable[result._host.name] = result._result
