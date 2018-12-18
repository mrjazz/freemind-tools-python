# -*- coding: utf-8 -*-

# import os
# os.chdir('D:/Denis/python/freemind-tools')

import sys
sys.path.append('D:/Denis/python/freemind-tools')

from datetime import date, datetime
import freemind
import os.path

from pprint import pprint


# def print_as_tree(node, level):
#     for key in node.keys():
#         if key == '@TEXT':
#             print(level * '  '  + node[key])


def check_path(path=None):        
    if path is None or not os.path.isfile(path):
        print("Please define valid path")
        exit()


def display_command(path=None):
    check_path(path)
    doc = freemind.read_xml(path)
    freemind.traverse_xml(doc, freemind.print_as_tree)


def dict_set(props, name, value):
    if name in props:
        props[name].append(value)
    else:
        props.setdefault(name, [value])


def node_is_expired(node):
    return node.has_attr('Due') and node.get_attr('Due') < datetime.now()


def format_icon(icon):
    if icon == 'button_ok':
        return 'DONE'
    elif icon == 'stop-sign':
        return 'STOP'
    else:
        return icon


def format_icons(icons):
    if icons is None:
        return []
    return [format_icon(i) for i in icons]


def format_node(node: freemind.FreeMindNode, format="flag parent / title {attrs} icon") -> str:
    """
    Format: parent, flag, title, icon, attrs

    :param node: some node
    :param format: use format
    :return: formatted string
    """
    attrs = []

    for i in ["Due", "Start"]:
        if node.has_attr(i):
            attrs.append("%s: %s" % (i, date.strftime(node.get_attr(i), "%d.%m.%Y")))
    if node.has_attr("Assigned"):
        attrs.append(node.get_attr("Assigned"))

    flag = ''
    if node_is_expired(node):
        flag += '[EXPIRED] '

    parent = ''
    if node.get_parent() is not None:
        parent = node.get_parent().get_title()

    icon = ", ".join(format_icons(node.get_attr('@ICON')))

    # return "%s%s / %s {%s} %s" % (flag, parent, node.get_title(), ", ".join(attrs), node.get_attr('@ICON'))
    # print(format.replace('icon', node.get_attr('@ICON')))
    return format\
        .replace('parent', parent)\
        .replace('flag', flag)\
        .replace('title', node.get_title())\
        .replace('attrs', ", ".join(attrs))\
        .replace('icon', icon)


def match_condition(node, filter_rules):
    conditions = []
    for i in filter_rules:
        if i == '':  # if empty condition passed
            conditions.append(False)
        elif i == '*':
            conditions.append(True)
        elif i[:5] == 'title' and node.get_title() == i[6:]:
            conditions.append(True)
        elif i == 'root' and node.get_parent() is None:
            conditions.append(True)
        elif i[:3] == 'id:' and node.has_attr("@ID") and i[3:] == node.get_attr("@ID"):
            conditions.append(True)
        elif i[:4] == 'icon' and node.has_attr("@ICON") and i[5:] in node.get_attr("@ICON"):
            conditions.append(True)
        elif i[:5] == '!icon' and node.has_attr("@ICON") and i[6:] not in node.get_attr("@ICON"):
            conditions.append(True)
        elif i == 'expired' and node_is_expired(node):
            conditions.append(True)
        elif i == 'not-expired' and not node_is_expired(node):
            conditions.append(True)
        elif i.lower() == 'not-assigned' and not node.has_attr("Assigned"):
            conditions.append(True)
        elif i.lower()[:8] == 'assigned' and node.has_attr("Assigned"):
            if len(i) == 8:
                conditions.append(True)  # just assigned
            elif node.get_attr("Assigned") == i[9:]:
                conditions.append(True)  # assigned and has passed employee
        else:
            conditions.append(False)
    # TODO : simplify it later
    # print(node)
    # print(conditions)
    return len([i for i in conditions if i]) > 0


def nodes_select(doc, rules: str):
    conditions = rules.split(',')
    return [i for i in freemind.traverse(doc, lambda n: match_condition(n, conditions))]


def nodes_filter(nodes: list, rules: str):
    conditions = rules.split(',')
    return [i for i in nodes if not match_condition(i, conditions)]


def query_nodes(path=None, select='', filter=''):
    check_path(path)
    doc = freemind.freemind_load(path)
    result = nodes_select(doc, select)
    result = nodes_filter(result, filter)
    return result


def todo_command(path=None, select='', filter='', group=''):
    result = query_nodes(path, select=select, filter=filter)

    # for i in result:
    #     print(i)
    # exit()

    if group == '':
        for i in result:
            print(format_node(i))
    else:
        groups = {}
        for i in result:
            if i.has_attr(group):
                dict_set(groups, i.get_attr(group), i)
            else:
                dict_set(groups, 'None', i)
        for i in sorted(groups.keys()):
            # sys.stdout.buffer.write(i)
            # print(i)
            print(i)
            print("\n".join(["\t%s" % format_node(i) for i in sorted(groups[i], key=lambda x: x.get_title())]))


def process_goals(nodes:list, filter:list, description='yes', level=0):
    if type(nodes) is freemind.FreeMindNode:
        format = "flag title {attrs} icon"
        print(level * '  ' + format_node(nodes, format))
        if nodes.has_content():
            content = nodes.get_content()
            l = level + 1
            if description == 'yes':
                print(l * '  ' + '---')
                delim = l * '  '
                print(delim + ('\n' + delim).join(content.split("\n")))
                print(l * '  ' + '---')
    if len(nodes) > 0:
        for node in nodes:
            if not match_condition(node, filter):
                process_goals(node, filter, description, level + 1)


def goals_command(path=None, select='', filter='', description='no'):
    result = query_nodes(path, select, filter)

    if not result:
        print("%s not found" % select)
    else:
        # then process only first node cause we don't expect find more
        process_goals(result, filter.split(','), description)


def stat_command(path=None):
    check_path(path)
    print("Goals count: %s" % len(query_nodes(path, '*', '')))
    print("Goals done: %s" % len(query_nodes(path, 'icon-button_ok', '')))

    node = freemind.freemind_load(path)
    print("Goals in progress: %s" % len(freemind.select_bottom(node)))


if __name__ == '__main__':
    # shell.py search --path=Goals.mm --icon=stop-sign // nodes on hold
    # shell.py search --path=Goals.mm --icon=yes // important nodes
    # shell.py search --path=Goals.mm // all nodes
    # shell.py group --path=Goals.mm --by=resource // actual tasks by resource
    # shell.py group --path=Goals.mm --by=expired // expired tasks
    # mm todo --path=Goals.mm --filter=not-assigned --group=Assigned
    # mm todo --path=Goals.mm --filter=expired

    # node = freemind.FreeMindNode(None)
    # node.set_title('test')
    # node.add_attr('@ICON', 'stop-sign')
    # print(should_filter(node, ['icon-stop-sign']))

    # goals_command('Goals.mm', select='title:Ilya Levoshko (QA)', filter='icon-button_ok,icon-stop-sign', description='no')
    # todo_command('Goals.mm', select='expired', filter='icon-button_ok')
    # todo_command('Goals.mm', select='assigned:@Sheremetov', filter='icon-button_ok')
    # todo_command('Goals.mm', select='assigned', filter='icon-button_ok', group='Assigned')
    # todo_command('D:\Denis\python\onixteam\Goals.mm', select='id:363b6bf92c5df3e2dc30043f1212d103')
    # PATH = 'D:\Denis\python\onixteam\Goals.mm'
    # stat_command(PATH)
    # nodes = query_nodes(PATH, 'icon-button_ok', '')
    # print(len(nodes))
    # exit()

    # nodes = freemind.freemind_load('Goals.mm')
    # todo_command('Goals.mm')

    from commandliner import commandliner
    commandliner(locals())