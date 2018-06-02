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
    FONTS                   = [ # FONTS[0] is the default, the rest are alts
        b'10;', b'11;', b'12;', b'13;', b'14;', b'15;', b'16;', b'17;', b'18;',
        b'19;'
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
        'BRIGHT_GREEN':     '32;1;'
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
        'BRIGHT_GREEN':     '102;'
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
