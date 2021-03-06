from pathlib import Path
from unittest import TestCase

from barentsz._discover import (
    discover_attributes,
    _match_attribute,
    _find_attribute_docstring,
)
from test_resources.examples_for_tests import module1


class TestDiscoverClasses(TestCase):

    def test_match_attribute(self):
        # EXECUTE
        match1 = _match_attribute('  some_attr   =     2  ')
        match2 = _match_attribute('  some_attr  :  int  =   2  ')
        match3 = _match_attribute(
            '  some_attr  :  int  =   2  #   bla bla bla!   ')
        match4 = _match_attribute(
            '  some_attr    int  =   2  #   bla bla bla!   ')
        match5 = _match_attribute(
            '  some attr     =   2  #   bla bla bla!   ')
        match6 = _match_attribute(
            'some attr == 2')

        # VERIFY
        self.assertTupleEqual(('some_attr', None, '2', None), match1)
        self.assertTupleEqual(('some_attr', 'int', '2', None), match2)
        self.assertTupleEqual(('some_attr', 'int', '2', 'bla bla bla!'), match3)
        self.assertEqual(None, match4)
        self.assertEqual(None, match5)
        self.assertEqual(None, match6)

    def test_discover_attributes_in_path(self):
        # SETUP
        path_to_resources = (Path(__file__).parent.parent / 'test_resources'
                             / 'examples_for_tests')

        # EXECUTE
        attributes = discover_attributes(path_to_resources)
        attribute_names = [attribute.name for attribute in attributes]

        # VERIFY
        self.assertEqual(2, len(attributes))
        self.assertListEqual(['ATTR1', 'ATTR1'], attribute_names)

    def test_discover_attributes_in_module(self):
        # EXECUTE
        attributes = discover_attributes(module1)

        # VERIFY
        self.assertEqual(1, len(attributes))
        self.assertEqual('ATTR1', attributes[0].name)
        self.assertEqual(int, attributes[0].type_)
        self.assertEqual(42, attributes[0].value)
        self.assertEqual('Lets put some\ncomments for ATTR1 here\n\nwith '
                         'multiple lines...', attributes[0].doc)
        self.assertEqual('And some more comments here...', attributes[0].comment)

    def test_discover_attributes_in_private_modules(self):
        # SETUP
        path_to_resources = (Path(__file__).parent.parent / 'test_resources'
                             / 'examples_for_tests')

        # EXECUTE
        attributes = discover_attributes(path_to_resources, in_private_modules=True)

        # VERIFY
        self.assertEqual(3, len(attributes))
        self.assertTrue(all([attribute.is_public for attribute in attributes]))

    def test_discover_private_attributes(self):
        # SETUP
        path_to_resources = (Path(__file__).parent.parent / 'test_resources'
                             / 'examples_for_tests')

        # EXECUTE
        attributes = discover_attributes(path_to_resources, include_privates=True)

        # VERIFY
        self.assertEqual(4, len(attributes))
        self.assertTrue(any([attribute.is_private for attribute in attributes]))

    def test_discover_attributes_with_signature(self):
        # SETUP
        path_to_resources = (Path(__file__).parent.parent / 'test_resources'
                             / 'examples_for_tests')

        # EXECUTE
        attributes_str = discover_attributes(path_to_resources, signature=str)
        attributes_int = discover_attributes(path_to_resources, signature=int)

        # VERIFY
        self.assertEqual(1, len(attributes_str))
        self.assertEqual(1, len(attributes_int))
        self.assertEqual(str, attributes_str[0].type_)
        self.assertEqual(int, attributes_int[0].type_)

    def test_discover_attributes_with_wrong_argument(self):
        # EXECUTE & VALIDATE
        with self.assertRaises(ValueError):
            discover_attributes(123)

    def test_find_docstring(self):
        # SETUP
        expected1 = 'Some\ndocstring...'
        lines1 = [
            '    """   \n',
            '\n',
            'Some\n'
            'docstring...\n',
            '   """     \n',
        ]
        expected2 = 'Another\ndocstring...'
        lines2 = [
            "    '''   Another\n",
            'docstring...\n',
            "   '''     \n",
        ]
        expected3 = 'A\ndocstring, that\nhovers a bit'
        lines3 = [
            '"""A\n',
            'docstring, that\n',
            'hovers a bit"""\n',
            ' \n',
            ' \n',
        ]
        expected4 = None
        lines4 = [
            '""Almost a docstring"""'
        ]
        expected5 = None
        lines5 = [
            '"""Also almost..."""\n# Nope'
        ]

        # EXECUTE
        docstring1 = _find_attribute_docstring(lines1)
        docstring2 = _find_attribute_docstring(lines2)
        docstring3 = _find_attribute_docstring(lines3)
        docstring4 = _find_attribute_docstring(lines4)
        docstring5 = _find_attribute_docstring(lines5)

        # VERIFY
        self.assertEqual(expected1, docstring1)
        self.assertEqual(expected2, docstring2)
        self.assertEqual(expected3, docstring3)
        self.assertEqual(expected4, docstring4)
        self.assertEqual(expected5, docstring5)
