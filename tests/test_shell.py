import unittest

from shell import goals_command, match_condition, todo_command, query_nodes
from freemind import FreeMindNode


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

    def test_select(self):
        result = query_nodes('Test.mm', select='id:ID_1232863674')
        self.assertEqual(1, len(result))
        self.assertEqual('New Mindmap', result[0].get_title())
        self.assertEqual('ID_1232863674', result[0].get_attr('@ID'))
        self.assertEqual(4, len(result[0]))

    def test_select_root(self):
        result = query_nodes('Test.mm', select='root')
        self.assertEqual(1, len(result))
        self.assertEqual('root', result[0].get_title())
        self.assertEqual('New Mindmap', result[0][0].get_title())
        self.assertEqual('ID_1232863674', result[0][0].get_attr('@ID'))
        # self.assertEqual(4, len(result[0]))


if __name__ == "__main__":
    unittest.main()
