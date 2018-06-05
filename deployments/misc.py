from docker     import DockerClient
from os.path    import join, abspath, dirname
from requests   import get
from random     import randrange
client = DockerClient(u"unix://var/run/docker.sock", version=u"1.30")

class TerminalOutputModifiers:
    """ANSI codes for terminal output colors and effects."""
    START                   = b"\033[;"
    RESET                   = b'0;'
    WEIGHT                  = {
        b'BOLD': b'1;', b'FAINT': '2;', b'NORMAL': '22;'}
    ITALIC                  = {b'ON': b'3;', b'OFF': b'23;'}
    UNDERLINE               = b'4;'
    BLINK                   = {b'FAST': b'6;', b'SLOW': b'5;'}
    INVERSE_COLOR           = {b'ON': b'7;', b'OFF': b'27;'}
    STRIKETHROUGH           = {b'ON': b'9;', b'OFF': b'29;'}
    # ^^ probably won't work
    FONTS                   = [
        # FONTS[0] is the default, the rest are alternatives
        b'10;', b'11;', b'12;', b'13;', b'14;', b'15;', b'16;', b'17;',
        b'18;', b'19;'
    ]
    FOREGROUND_COLOR        = {
        'RED':              '31;',
        'GREEN':            '32;',
        'YELLOW':           '33;',
        'BLUE':             '34;',
        'MAGENTA':          '35;',
        'CYAN':             '36;',
        'WHITE':            '37;',
        'BLACK':            '30;',
        'BRIGHT_RED':       '31;1;',
        'BRIGHT_GREEN':     '32;1;',
        'BRIGHT_YELLOW':    '33;1;',
        'BRIGHT_BLUE':      '34;1;',
        'BRIGHT_MAGENTA':   '35;1;',
        'BRIGHT_CYAN':      '36;1;',
        'LIGHT_GREY':       '37;1;',
        'DARK_GREY':        '30;1;',
        'LIGHT_GRAY':       '37;1',
        'DARK_GRAY':        '30;1;'
    }
    BACKGROUND_COLOR        = {
        'RED':              '41;',
        'GREEN':            '42;',
        'YELLOW':           '43;',
        'BLUE':             '44;',
        'MAGENTA':          '45;',
        'CYAN':             '46;',
        'WHITE':            '47;',
        'BLACK':            '40;',
        'BRIGHT_RED':       '101;',
        'BRIGHT_GREEN':     '102;',
        'BRIGHT_YELLOW':    '103;',
        'BRIGHT_BLUE':      '104;',
        'BRIGHT_MAGENTA':   '105;',
        'BRIGHT_CYAN':      '106;',
        'LIGHT_GREY':       '107;',
        'DARK_GREY':        '100;',
        'LIGHT_GRAY':       '107;',
        'DARK_GRAY':        '100;'
    }
    FRAMED                  = '51;'
    ENCIRCLED               = '52;'
    OVERLINED               = {b'ON': '53;', b'OFF': b'54;'}

    def build(self, *effects, **kweffects):
        """Build an effects string.

        Top-level values should be specified as strings, and effects that have
        more than one choice should be specified as keyword arguments.

        For example:
            TerminalOutputModifiers.build("FRAMED", FOREGROUND_COLOR="MAGENTA")
        """
        out = self.START
        for effect in effects:
            if effect in self.__dict__:
                out += self.__dict__.get(effect)
            else:
                print("Effect %s not found." % effect)
        for effect, value in kweffects.items():
            if effect in self.__dict__.keys():
                if value in self.__dict__.get(effect):
                    out += self.__dict__[effect][value]
                else:
                    print("Effect %s has no %s value" % (effect, value))
            else:
                print("Effect %s not found" % effect)
        return out

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
        print "ERROR while running the following command in the"
        print "nextcloud container:"
        print cmd
        print "The command output the following:"
        print result.output
        print "and executed with the code %d." % result.exit_code
        return False
    else:
        return result.output


def _get_wordlist():
    """Internal function, for random_words()

    Returns a list of words, gathered form words.txt or freebsd.org"""
    wordlist = []
    try:
        with open(
                    join(abspath(dirname(__file__)), "list_of_words.txt"),
                    'r'
                ) as wordlistfile:
            wordlist = map(
                lambda word: word.strip('\n'),
                wordlistfile.readlines()
            )
    except IOError:
        response = get("http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain")
        wordlist = response.text.split('\n')
        with open("words.txt", 'w') as wordlistfile:
            wordlistfile.writelines(
                map(lambda word: word + '\n', wordlist)
            )
    return wordlist


def random_words(num, sep="_"):
    """
    Generate `num` random words, separated by `sep`.

    sep defaults to _
    """
    result = ""

    wordlist = _get_wordlist()
    while num:
        num -= 1
        result += wordlist[randrange(len(wordlist))]
        if num:
            result += sep
    return result
