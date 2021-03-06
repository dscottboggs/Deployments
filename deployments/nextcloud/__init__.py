"""The deploy_nextcloud package in Deployments a nextcloud deployment.

See README for usage.
"""
from deployments    import client


def occ(environment, *cmdargs):
    """Execute the `php occ` command in the container.

    Arguments should be specified as strings passed to this function,
    for example:
        occ("user:add", "--display-name", "Scott", "scott@tams.tech")

    If environment is specified it should be a list of "ENV=value" or
    a dict mapping the environment variable to its value. If you don't
    want to specify an environment, you have to specify a falsey value,
    like None, or the empty string ('').

    Commands are run as the www-data user.
    """
    def get_environ():
        cmd = ''
        if environment:
            if isinstance(environment, dict):
                for k, v in environment.items():
                    cmd += "%s=%s" % (k, v)
                return cmd
            elif isinstance(environment, list):
                for env in environment:
                    cmd += env
                return cmd
            else:
                raise TypeError(
                    "Environment must be a list or dict, got %s of type %s."
                    % (environment, type(environment))
                )
        else:
            return ''
    container = client.containers.list(
        filters={"name": "nextcloud_frontend_1"})[0]
    cmd = get_environ() + " php occ"
    for arg in cmdargs:
        if isinstance(arg, str):
            cmd += ' ' + arg
        else:
            raise TypeError(
                "Each argument must be a string, got %s of type %s." % (
                    arg, type(arg)
                )
            )
    result = container.exec_run(cmd, user="www-data")
    if result.exit_code:
        print(
            "ERROR while running the following command in the",
            "nextcloud container:",
            cmd,
            "The command output the following:",
            result.output,
            "and executed with the code %d." % result.exit_code,
            sep='\n'
        )
        return False
    else:
        return result.output
