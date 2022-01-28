import unittest

from shell import goals_command, match_condition, todo_command, query_nodes, format_node
from freemind import FreeMindNode

import re
from os.path import exists
from pprint import pprint


PATH_TO_TEST_FILE = './tests/TestFP.mm'

class ShellTestCase(unittest.TestCase):

    def test_filter(self):
        node = FreeMindNode(None)
        node.set_title('test node')
        node.add_attr('@ICON', 'button_ok')
        node.add_attr('Assigned', '@Denis')
        self.assertTrue(match_condition(node, ['title:test node']))
        self.assertFalse(match_condition(node, ['expired']))
        self.assertTrue(match_condition(node, ['icon-button_ok']))
        self.assertFalse(match_condition(node, ['!icon-button_ok']))
        self.assertTrue(match_condition(node, ['expired', '!icon-stop']))
        self.assertTrue(match_condition(node, ['assigned:@Denis']))
        self.assertTrue(match_condition(node, ['has-attr:Assigned']))

    def test_select(self):
        result = query_nodes(PATH_TO_TEST_FILE, select='id:ID_1232863674')
        self.assertEqual(1, len(result))
        self.assertEqual('New Mindmap', result[0].get_title())
        self.assertEqual('ID_1232863674', result[0].get_attr('@ID'))
        self.assertEqual(5, len(result[0]))

    def test_select_root(self):
        result = query_nodes(PATH_TO_TEST_FILE, select='root')
        self.assertEqual(1, len(result))
        self.assertEqual('root', result[0].get_title())
        self.assertEqual('New Mindmap', result[0][0].get_title())
        self.assertEqual('ID_1232863674', result[0][0].get_attr('@ID'))
        # self.assertEqual(4, len(result[0]))

    def test_format_node(self):
        result = query_nodes(PATH_TO_TEST_FILE, select='title:In progress')
        self.assertEqual(1, len(result))
        self.assertEqual('In progress', result[0].get_title())
        self.assertEqual(' New Mindmap / In progress [] ', format_node(result[0], '{flag} {parent} / {title} [{attrs}] {icon}'))
        self.assertEqual('In progress\n--\nabc\ndef\n--\n', format_node(result[0], '{title}\n{content}'))

    def test_cancel(self):
        result = query_nodes(PATH_TO_TEST_FILE, select='title:Canceled')
        self.assertEqual(1, len(result))
        self.assertTrue(result[0].has_attr('@ICON'))
        self.assertEqual(['button_cancel'], result[0].get_attr('@ICON'))

    def test_format_attr(self):
        result = query_nodes(PATH_TO_TEST_FILE, select='title:Task1')
        # print(format_node(result[0], 'title - [@Assigned]'))
        self.assertEqual('Task1 - [@Denis]', format_node(result[0], '{title} - [{@Assigned}]'))
        self.assertEqual('Task1 - [@Denis] - [Aug 1]', format_node(result[0], '{title} - [{@Assigned}] - [{@Started}]'))

        result = query_nodes(PATH_TO_TEST_FILE, select='title:Done')
        self.assertEqual('Done - []', format_node(result[0], '{title} - [{@Assigned}]'))


if __name__ == "__main__":
    unittest.main()
