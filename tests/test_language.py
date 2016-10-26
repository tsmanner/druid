from unittest import TestCase

import app


class TestLanguage(TestCase):
    def test_process(self):
        grammars = {
            "CPP14": {
                "file": "CPP14.g4",
                "rules": {
                    "class": "classname",
                    "attribute": "attributespecifierseq",
                    "operation": "functiondefinition"
                }
            }
        }
        for grammar in grammars:
            l = app.Language(grammars[grammar])
            l.process("cpyswp.cpp")
