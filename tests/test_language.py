from unittest import TestCase

import app
import os


class TestLanguage(TestCase):

    class CustomListener:
        def enter_class(self, ctx):
            print("entering class", ctx)

        def exit_class(self, ctx):
            print("exiting class", ctx)

        def enter_attribute(self, ctx):
            print("entering attribute", ctx)

        def exit_attribute(self, ctx):
            print("exiting attribute", ctx)

        def enter_operation(self, ctx):
            print("entering operation", ctx)

        def exit_operation(self, ctx):
            print("exiting operation", ctx)

    def setUp(self):
        self.grammars = {
            "CPP14": {
                "file": os.path.dirname(__file__) + os.sep + "CPP14.g4",
                "rules": {
                    "class": "typeparameter",
                    "attribute": "attributespecifierseq",
                    "operation": "functiondefinition"
                },
                "entry_point": "typeparameter",
                "test_files": ["cpyswp.cpp", "dlgt.cpp"]
            }
        }

    def test_process(self):
        for grammar_enum in enumerate(self.grammars):
            gnum = grammar_enum[0]
            name = grammar_enum[1]
            grammar = self.grammars[name]
            lang = app.Language(grammar, TestLanguage.CustomListener)
            for fl_enum in enumerate(grammar["test_files"]):
                tnum = gnum + fl_enum[0]
                fl = fl_enum[1]
                with self.subTest(i=tnum):
                    print(fl)
                    lang.process(fl)
