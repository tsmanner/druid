from unittest import TestCase

import antlr4
import app


class TestLanguage(TestCase):
    def setUp(self):
        self.grammars = {
            "CPP14": {
                "file": "CPP14.g4",
                "rules": {
                    "class": "classname",
                    "attribute": "attributespecifierseq",
                    "operation": "functiondefinition"
                },
                "test_files": ["cpyswp.cpp", "dlgt.cpp"]
            }
        }

    def test_process(self):
        for grammar_enum in enumerate(self.grammars):
            gnum = grammar_enum[0]
            name = grammar_enum[1]
            grammar = self.grammars[name]
            lang = app.Language(grammar)
            for fl_enum in enumerate(grammar["test_files"]):
                tnum = gnum + fl_enum[0]
                fl = fl_enum[1]
                with self.subTest(i=tnum):
                    lang.process(fl)
