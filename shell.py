# -*- coding: utf-8 -*-

# import os
# os.chdir('D:/Denis/python/freemind-tools')


import sys
sys.path.append('D:/Denis/python/freemind-tools')

from datetime import date, datetime
import freemind
import os.path
import re

from pprint import pprint


BTN_OK = 'button_ok'
BTN_STOP = 'stop-sign'
BTN_CANCEL = 'button_cancel'


# def print_as_tree(node, level):
#     for key in node.keys():
#         if key == '@TEXT':
#             print(level * '  '  + node[key])

def display_nodes(nodes:list, level=0):
    if type(nodes) is freemind.FreeMindNode:                
        print(level * '  ' + nodes.get_title())
        if nodes.has_content():
            content = nodes.get_content()
            l = level + 1            
            print(l * '  ' + '---')
            delim = l * '  '
            print(delim + ('\n' + delim).join(content.split("\n")))
            print(l * '  ' + '---')
        if len(nodes) > 0:
            for node in nodes:                
                display_nodes(node, level + 1)


def display_command(path=None):
    result = query_nodes(path)

    if not result:
        print("%s not found" % select)
    else:
        # then process only first node cause we don't expect find more
        display_nodes(result)


def check_path(path=None):
    if path is None or not os.path.isfile(path):
        print("Please define valid path")
        exit()


def dict_set(props, name, value):
    if name in props:
        props[name].append(value)
    else:
        props.setdefault(name, [value])


def node_is_expired(node):
    return node.has_attr('Due') and node.get_attr('Due') < datetime.now()


def format_icon(icon):
    if icon == BTN_OK:
        return 'DONE'
    elif icon == BTN_STOP:
        return 'STOP'
    elif icon == BTN_CANCEL:
        return 'CANCEL'
    else:
        return icon


def format_icons(icons):
    if icons is None:
        return []
    return [format_icon(i) for i in icons]

def full_node_path(fullNodePath, node):
    return (full_node_path(fullNodePath, node.get_parent()) if
            node.get_parent() is not None and node.get_parent().get_title() != 'root' else fullNodePath) + '/' + node.get_title()

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
    grandparent = ''
    fullnodepath = full_node_path('', node)
    if node.get_parent() is not None:
        parent = node.get_parent().get_title()

        if node.get_parent().get_parent() is not None:
            grandparent = node.get_parent().get_parent().get_title()

    icon = ", ".join(format_icons(node.get_attr('@ICON')))

    if node.has_content():
        content = "--\n%s\n--\n" % node.get_content()
    else:
        content = ''

    # return "%s%s / %s {%s} %s" % (flag, parent, node.get_title(), ", ".join(attrs), node.get_attr('@ICON'))
    # print(format.replace('icon', node.get_attr('@ICON')))

    attr_pattrn = re.compile("{@([\w\-]+)}")
    return attr_pattrn.sub(lambda m: node.get_attr(m.group(1)), format) \
        .replace('{parent}', parent) \
        .replace('{grandparent}', grandparent) \
        .replace('{fullnodepath}', fullnodepath) \
        .replace('{flag}', flag) \
        .replace('{title}', node.get_title()) \
        .replace('{attrs}', ", ".join(attrs)) \
        .replace('{icon}', icon)\
        .replace('{content}', content)


def match_condition(node, filter_rules):
    # if len(filter_rules) == 1 and filter_rules[0] == '':
    #     return True

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
        elif i[:9] == 'has-attr:' and node.has_attr(i[9:]):
                conditions.append(True)
        elif i[:11] == 'hasnt-attr:' and not node.has_attr(i[11:]):
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
                conditions.append(True)  # assigned and has passed assignee
        else:
            conditions.append(False)
    # TODO : simplify it later
    # print(node)
    # print(filter_rules, conditions)
    return len([i for i in conditions if i]) > 0


def nodes_select(doc, rules: str):
    if rules == '':
        return doc
    conditions = rules.split(',')
    return [i for i in freemind.traverse(doc, lambda n: match_condition(n, conditions))]


def nodes_filter(nodes: list, rules: str):
    if rules == '':
        return nodes
    conditions = rules.split(',')
    return [i for i in nodes if not match_condition(i, conditions)]


def query_nodes(path=None, select='', filter=''):
    check_path(path)
    doc = freemind.freemind_load(path)
    result = nodes_select(doc, select)
    result = nodes_filter(result, filter)
    return result


def todo_command(path=None, select='', filter='', group='', format='flag title {attrs} icon'):
    result = query_nodes(path, select=select, filter=filter)

    # for i in result:
    #     print(i)
    # exit()

    if group == '':
        for i in result:
            print(format_node(i, format=format))
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
            print("\n".join(["\t%s" % format_node(i, format=format) for i in sorted(groups[i], key=lambda x: x.get_title())]))


def process_goals(nodes:list, filter:list, level=0, format='flag title {attrs} icon'):
    if type(nodes) is freemind.FreeMindNode:
        print(level * '  ' + format_node(nodes, format=format))
        # if nodes.has_content():
        #     content = nodes.get_content()
        #     l = level + 1
        #     if description == 'yes':
        #         print(l * '  ' + '---')
        #         delim = l * '  '
        #         print(delim + ('\n' + delim).join(content.split("\n")))
        #         print(l * '  ' + '---')
    if len(nodes) > 0:
        for node in nodes:
            if not match_condition(node, filter):
                process_goals(node, filter, level + 1, format=format)


def goals_command(path=None, select='', filter='', format='flag title {attrs} icon'):
    result = query_nodes(path, select, filter)

    if not result:
        print("%s not found" % select)
    else:
        # then process only first node cause we don't expect find more
        process_goals(result, filter.split(','), format=format)


def stat_command(path=None):
    check_path(path)
    print("Goals count: %s" % len(query_nodes(path, '*', '')))
    print("Goals done: %s" % len(query_nodes(path, 'icon-%s' % BTN_OK, '')))
    print("Goals canceled: %s" % len(query_nodes(path, 'icon-%s' % BTN_CANCEL, '')))
    print("Goals stoped: %s" % len(query_nodes(path, 'icon-%s' % BTN_STOP, '')))

    node = freemind.freemind_load(path)
    print("Goals in progress: %s" % len(freemind.select_bottom(node)))


def traverse_command(path=None, select='', filter='', format='title'):
    result = query_nodes(path, select, filter)

    if not result:
        print("%s not found" % select)
    else:
        # then process only first node cause we don't expect find more
        process_goals(result, filter=filter.split(','), format=format)


def questions_command(path=None):
    check_path(path)    

    def fn_list(n):
        if not hasattr(fn_list, 'counter'):
            fn_list.counter = 1
        if n.has_attr('@ICON') and 'help' in n.get_attr('@ICON'):            
            print("%s. %s\n   %s\n" % (fn_list.counter, n.get_title(), n.get_content()))
            fn_list.counter += 1

    result = freemind.freemind_load(path)
    freemind.traverse(result, fn_list)


def estimate_command(path=None, format=' - {grandparent}/{parent}/{title}, {@estimate}h'):
    check_path(path)  

    def fn_list(n):
        if not hasattr(fn_list, 'result'):
            fn_list.result = []
            fn_list.total = 0

        if n.has_attr('estimate'):
            if n.has_attr('@ICON') and BTN_STOP in n.get_attr('@ICON'):
                return

            fn_list.result.append(format_node(n, format))
            fn_list.total += float(n.get_attr('estimate'))

    result = freemind.freemind_load(path)
    freemind.traverse(result, fn_list)

    [print(i) for i in sorted(fn_list.result)]
    print("\nTotal: %sh" % fn_list.total)


def competences_command(path=None):
    check_path(path)

    result = query_nodes(path, select='title:Activities')
    if len(result) != 1:
        print('Activities node missed')
        return

    import json

    output = []
        
    for competence in result[0]:
        tech = False
        if competence.has_attr('tech') and competence.get_attr('tech').lower() == 'yes':
            tech = True

        project = False
        if competence.has_attr('project') and competence.get_attr('project').lower() == 'yes':
            project = True

        roles = '-'
        if competence.has_attr('roles'):
            roles = competence.get_attr('roles')

        confirm = ''
        if competence.has_attr('confirm'):
            confirm = competence.get_attr('confirm')
        
        # print("%s [tech: %s, project: %s, roles: %s]" % (competence.get_title(), tech, project, roles))

        competences = []

        for competence_level in competence:
            if competence_level.get_title() == 'attribute_layout':
                continue
            level = 0
            if competence_level.has_attr('@ICON'):
                if 'full-1' in competence_level.get_attr('@ICON'):
                    level = '1'
                elif 'full-2' in competence_level.get_attr('@ICON'):
                    level = '2'
                elif 'full-3' in competence_level.get_attr('@ICON'):
                    level = '3'
                elif 'full-4' in competence_level.get_attr('@ICON'):
                    level = '4'
            # print("  %s. %s" % (level, competence_level.get_title()))
            competences.append({'level': level, 'desc': competence_level.get_title()})    
        output.append({
            'title': competence.get_title(), 
            'tech': tech, 
            'project': project, 
            'roles': roles.split(','),
            'confirm': confirm.split(','),
            'competences': competences
        })    
    print(json.dumps(output))


def spec_command(path=None, parts=None, out=None):    
    check_path(path)

    doc = freemind.freemind_load(path)

    if out:
        output = open(out, "w", encoding="utf-8")

    def process_node(n, level):
        if n.has_attr('@ICON') and 'button_cancel' in n.get_attr('@ICON'):            
            return
        result = level * '#' + ' ' + n.get_title() + "\n\n"            
        
        if n.has_content():
            result += n.get_content() + "\n\n"

        if out:
            output.write(result)
        else:
            print(result)

    def fn_list(nodes, level):
        if not nodes:             
            return
        for n in nodes:            
            process_node(n, level)
                
            fn_list(n, level+1)

    if parts is None:
        pass
    else:
        for part in parts.split(';'):
            nodes = nodes_select(doc, "title:%s" % part)            

            fn_list(nodes, 1)                
            # print(nodes)

    if out:
        output.close()


def tex_command(path):
    check_path(path)
    doc = open(path).read()
    begin_marker = '\\begin{document}'
    end_marker = '\\end{document}'
    begin_pos = doc.find(begin_marker)
    end_pos = doc.find(end_marker)    
    
    if begin_pos < 0 or end_pos < 0:
        print('Markers not found')
        return
    
    print(doc[begin_pos+len(begin_marker):end_pos])    


if __name__ == '__main__':    
    # shell.py search --path=Goals.mm --icon=stop-sign // nodes on hold
    # shell.py search --path=Goals.mm --icon=yes // important nodes
    # shell.py search --path=Goals.mm // all nodes
    # shell.py group --path=Goals.mm --by=resource // actual tasks by resource
    # shell.py group --path=Goals.mm --by=expired // expired tasks
    # mm todo --path=Goals.mm --filter=not-assigned --group=Assigned
    # mm todo --path=Goals.mm --filter=expired
    # mm traverse --path=tests\Test.mm --select="title:New Mindmap" --format="title @Assigned"


    # node = freemind.FreeMindNode(None)
    # node.set_title('test')
    # node.add_attr('@ICON', 'stop-sign')
    # print(should_filter(node, ['icon-stop-sign']))

    # goals_command('Goals.mm', select='title:Ilya Levoshko (QA)', filter='icon-button_ok,icon-stop-sign', description='no')
    # todo_command('Goals.mm', select='expired', filter='icon-button_ok')
    # todo_command('Goals.mm', select='assigned:@Sheremetov', filter='icon-button_ok')
    # todo_command('D:\Denis\python\onixteam\Goals.mm', select='assigned', filter='icon-button_ok')
    # exit()
    # todo_command('D:\Denis\python\onixteam\Goals.mm', select='id:363b6bf92c5df3e2dc30043f1212d103')

    # stat_command(PATH)
    # nodes = query_nodes(PATH, 'icon-button_ok', '')
    # print(len(nodes))


    # nodes = freemind.freemind_load('Goals.mm')
    # todo_command('tests/Test.mm')    
    # result = freemind.freemind_load('D:/temp/presale/impesa/test.mm')    
    # freemind.traverse_with_level(result, lambda n, l: print((l-1) * '  ' + format_node(n, '{title}')))

    # traverse_command('tests/Test.mm', select='title:New Mindmap', filter='', format='title {@Assigned}')
    # traverse_command("D:/Dropbox/onix/clients/UpMost/UpMostLanding.mm", select='title:Screens', filter='icon-stop-sign', format='title,{@estimate},{@estimate-res}')

    # print([i.get_title() for i in query_nodes("D:/Dropbox/onix/clients/UpMost/UpMostLanding.mm")])
    
    # freemind.traverse(result, lambda n: print(format_node(n, 'title')))

    # estimate_command("D:/Dropbox/onix/clients/UpMost/UpMostLanding.mm")
    # estimate_command("tests/Test.mm")

    # spec_command('D:/temp/presale/impesa/Impesa.mm', 'Web application functionality')  

    # display_command('D:/temp/presale/impesa/impesa.mm')
    # tex_command('D:/temp/presale/impesa/impesa.tex')
    # exit()           

    # PATH = '/home/denis/Dropbox/Onix/skills-matrix-v2.mm'
    # competences_command(PATH)
    # exit()

    # python3 shell.py competences --path=/home/denis/Dropbox/Onix/skills-matrix-v2.mm > /var/www/hrm/web/code/webroot/competences.json

    from commandliner import commandliner
    commandliner(locals())    
