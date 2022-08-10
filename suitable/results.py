import typing as t


class RunnerResults(dict):
    """
    Wraps the results of parsed module_runner output. The result may
    be used just like it is in Ansible::
        
        >>> result['contacted']['server']['rc']

    Alternatively can be used accessing keys as methods::

        >>> result.contacted()
        >>> result.rc('server')

    """

    def __init__(self, results):
        #  type: (dict[t.Any, t.Any]) -> None
        """
        Initializes the class with a dictionary of results.

        Args:
            results (dict[t.Any, t.Any]): A dicionary.
        """        
        self.update(results)

    def __getattr__(self, key):
        #  type: (str) -> t.Any
        """
        Dunder method to make a dict behaviour as keys were methods.
        Allows for::

            >>> result['contacted']
            >>> result.contacted()

        Args:
            key (str): The key to get

        Returns:
            t.Any: ...
        """        
        return lambda server=None: self.acquire(server, key)

    def acquire(self, server, key):
        #  type: (t.Optional[str], t.Optional[str]) -> t.Any
        """
        Aquires the result for a given server and key. If no server is given,
        and exactly one contacted server exists return the value of said server directly.

        Args:
            server (t.Optional[str], optional): The server to acquire the value. Defaults to None.
            key (t.Optional[str], optional): The key to get. Defaults to None.

        Raises:
            KeyError: If no servers are contacted or if the server is not found.
            AttributeError: If key was not found

        Returns:
            t.Any: ...
        """
        contacted_servers = self['contacted'] # type: dict
        if server is None and len(contacted_servers) == 1:
            server = next((k for k in contacted_servers.keys()), None)

        if server not in contacted_servers:
            raise KeyError("{} could not be contacted".format(server))

        if key not in contacted_servers.get(server, {}):
            raise AttributeError

        return contacted_servers[server][key]
