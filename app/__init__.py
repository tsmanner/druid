import antlr4
import importlib
import itertools
import os
import re
import subprocess


"""
Setup some module level information
"""
antlr_jar = ''
max_version = '0'
dirname = os.path.dirname(__file__)
for fl in os.listdir(dirname):
    match = re.match('antlr(-)?((\d+\.?)+)?(-\w+)?.jar', fl)
    if match:
        version = match.group(2)
        for tpl in itertools.zip_longest(version.split('.'), max_version.split('.')):
            if tpl[1] is None:
                max_version = version
                antlr_jar = fl
            elif tpl[0] is None:
                continue
            elif int(tpl[0]) > int(tpl[1]):
                max_version = version
                antlr_jar = fl
            else:
                continue
if antlr_jar == '':
    exit("No antlr jar found!")
antlr_jar = os.sep.join((dirname, antlr_jar))


class GenericListener:
    """
    Generic class that our language specific listeners can reference.
    """
    @staticmethod
    def print_node_context(listener, ctx):
        print(listener, ctx)


class Language:
    """
    Class representing a Language and all of it's Lexing, Parsing, and Listening classes
    """
    def __init__(self, grammar_config: dict, custom_listener):
        """
        Take some grammar configuration information and create a language out of it.
            1.  Make sure we have a valid grammar file
            2.  Run ANTLR to generate the lexer, parser, and listener python modules
            3.  Import the ANTLR generated code
            4.  Assign passthroughs from this instance's listener to the generic listener
        """
        assert grammar_config["file"].endswith(".g4")
        lib_path = os.path.dirname(__file__) + os.sep + 'lib'
        try:
            os.makedirs(lib_path)
        except OSError:
            if not os.path.isdir(lib_path):
                raise
        gencmd = ' '.join(['java', '-jar', antlr_jar,
                           '-Dlanguage=Python3',
                           '-o', lib_path,
                           grammar_config['file']])
        subprocess.call(gencmd, stdout=subprocess.PIPE)
        self.name = os.path.basename(grammar_config["file"])[:-3]
        importlib.invalidate_caches()  # Force new imports each time
        exec("import app.lib." + self.name + "Lexer")
        exec("import app.lib." + self.name + "Parser")
        exec("import app.lib." + self.name + "Listener")

        class Listener(eval("app.lib." + self.name + "Listener." + self.name + "Listener"), custom_listener):
            pass

        for rule in grammar_config["rules"]:
            entercmd = "Listener.enter" + grammar_config["rules"][rule].capitalize() +\
                       " = Listener.enter_" + rule
            print(entercmd)
            exec(entercmd)
            exitcmd = "Listener.exit" + grammar_config["rules"][rule].capitalize() + \
                      " = Listener.exit_" + rule
            print(exitcmd)
            exec(exitcmd)

        self.lexer_factory = eval("app.lib." + self.name + "Lexer." + self.name + "Lexer")
        self.parser_factory = eval("app.lib." + self.name + "Parser." + self.name + "Parser")
        exec("self.parser_factory.entry_point = self.parser_factory." + grammar_config["entry_point"])
        self.listener_factory = Listener

    def process(self, filename: str):
        lexer = self.lexer_factory(antlr4.FileStream(filename))
        tokens = antlr4.CommonTokenStream(lexer)
        parser = self.parser_factory(tokens)
        walker = antlr4.ParseTreeWalker()
        walker.walk(self.listener_factory(), parser.entry_point())
