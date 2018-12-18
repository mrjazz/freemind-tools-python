import xmltodict
from collections import OrderedDict
from datetime import date, datetime
from pprint import pprint


def read_xml(file_path):
    with open(file_path) as fd:
        return xmltodict.parse(fd.read())


def traverse_xml(nodes, fn, level=0):
    if type(nodes) is OrderedDict:
        result = fn(nodes, level)
        if result:
            return result

        if type(nodes) is OrderedDict:
            for node in nodes.keys():
                children = nodes[node]
                result = traverse_xml(children, fn, level + 1)
                if result:
                    return result

    if type(nodes) is list:
        for i in nodes:
            result = traverse_xml(i, fn, level + 1)
            if result:
                return result

    return False


class FreeMindNode:

    def __init__(self, parent):
        self.__parent = parent
        self.__title = ''
        self.__content = ''
        self.__nodes = []
        self.__attrs = {}

    def set_content(self, content: str):
        self.__content = content

    def get_content(self) -> str:
        return dict_to_txt(self.__content).strip()

    def has_content(self):
        return self.__content != ''

    def get_parent(self) -> str:
        return self.__parent

    def get_attr(self, name):
        if self.has_attr(name):
            return self.__attrs[name]
        return None

    def has_attr(self, name):
        return name in self.__attrs

    def set_title(self, title):
        self.__title = title

    def get_title(self):
        return self.__title

    def set_attrs(self, attrs):
        self.__attrs = attrs

    def add_node(self, node):
        self.__nodes.append(node)

    def add_nodes(self, nodes):
        for node in nodes:
            self.__nodes.append(node)

    def add_attr(self, name, value):
        self.__attrs.setdefault(name, value)

    def display(self, level=0):
        print("%s %s [%s]" % ("  " * level, self.__title, ",".join([i + "=" + str(self.__attrs[i]) for i in self.__attrs])))
        # print("%s%s" % ("  " * level, self.__title))
        for i in self.__nodes:
            i.display(level+1)

    def __len__(self) -> int:
        return len(self.__nodes)

    def __getitem__(self, i):
        return self.__nodes[i]

    def __repr__(self):
        return "%s {%s} [%s]" % (self.__title, ",".join([i + "=" + str(self.__attrs[i]) for i in self.__attrs]),
                                                        ",".join([str(i) for i in self.__nodes]))


def debug(node, level):
    print(node)


def search(node, level):
    for key in node:
        if key == '@TEXT' and node[key] == 'Internship':
            return node
    return False


def print_as_tree(node, level=0):
    for key in node:
        if key == '@TEXT':
            print(level * '  ' + node[key])


def traverse(node, fn):
    result = []
    if fn(node):
        result.append(node)

    for i in node:
        res = traverse(i, fn)
        if len(res) > 0:
            for j in res:
                result.append(j)
    return result


def __process(nodes, title, parent):
    ignore_node = ['font', 'edge', 'attribute_registry']
    ignore_attr = ['@FOLDED', '@POSITION', '@X_COGGLE_POSY', '@X_COGGLE_POSX', '@STYLE', '@NAME_WIDTH', '@VALUE_WIDTH']
    attrs_date = ['START', 'DUE']
    content = ''

    if type(nodes) is OrderedDict:
        attrs = {}
        result = FreeMindNode(parent)
        for node in nodes:
            if type(node) is str and node[:1] == '@':
                if node not in ignore_attr:
                    attrs.setdefault(node, nodes[node])
            elif node not in ignore_node:
                if node == 'richcontent':
                    content = nodes[node]
                elif node == 'icon':
                    if type(nodes[node]) is list:
                        attrs.setdefault('@ICON', [i['@BUILTIN'] for i in nodes[node]])
                    else:
                        attrs.setdefault('@ICON', [nodes[node]['@BUILTIN']])
                elif node == 'attribute':
                    if type(nodes[node]) is list:
                        for i in nodes[node]:
                            if i['@NAME'].upper() in attrs_date:
                                attrs.setdefault(i['@NAME'], datetime.strptime(i['@VALUE'], "%d.%m.%Y"))
                            else:
                                attrs.setdefault(i['@NAME'], i['@VALUE'])
                    else:
                        attrs.setdefault(nodes[node]['@NAME'], nodes[node]['@VALUE'])

                    # attrs.setdefault('@ICON', [nodes[node]['@BUILTIN']])
                else:
                    processed_nodes = __process(nodes[node], node, result)
                    if type(processed_nodes) is list:
                        result.add_nodes(processed_nodes)
                    elif type(processed_nodes) is FreeMindNode:
                        result.add_node(processed_nodes)
                    else:
                        raise Exception('Unknown result of processing %s' % type(processed_nodes))

        result.set_attrs(attrs)
        result.set_content(content)

        if '@TEXT' in attrs:
            result.set_title(attrs['@TEXT'])
        else:
            result.set_title(title)
        return result

    elif type(nodes) is list:
        result = []
        for node in nodes:
            result.append(__process(node, 'none', parent))
            # if type(node) is str and node[:1] == '@':
            #     attrs.setdefault(node, nodes[node])
            # else:
            #     result.append(FreeMindNode(__process(node)))
        return result

    raise Exception("Unknown type %s" % type(nodes))


def freemind_load(path) -> FreeMindNode:
    doc = read_xml(path)
    return __process(doc['map'], 'root', None)


def node_has_stop_icon(node):
    return node.has_attr('@ICON') and 'stop-sign' in node.get_attr('@ICON')


def node_has_done_icon(node):
    return node.has_attr('@ICON') and 'button_ok' in node.get_attr('@ICON')


def node_is_actual(node):
    return not node.has_attr('Start') or node.get_attr('Start') < datetime.now()


def select_bottom(node: FreeMindNode):
    if node_has_stop_icon(node) or node_has_done_icon(node):
        return []

    result = []
    for i in node:
        if len(i) == 0:
            if not node_has_done_icon(i) and not node_has_stop_icon(i) and node_is_actual(i):
                result.append(i)
        else:
            result += select_bottom(i)
    return result


def dict_to_xml(nodes):
    if type(nodes) is OrderedDict:
        result = ''
        attrs = []
        for i in nodes:
            if i[:1] == '#':
                result += nodes[i]
            elif i[:1] == '@':
                attrs.append('%s="%s"' % (i[1:], nodes[i]))
            else:
                html, attr = dict_to_xml(nodes[i])
                if len(attr) > 0:
                    html_attr = ' ' + ' '.join(attr)
                else:
                    html_attr = ''

                if type(html) is list:
                    for tag in html:
                        result += "<%s%s>%s</%s>" % (i, html_attr, tag, i)
                else:
                    result += "<%s%s>%s</%s>" % (i, html_attr, html, i)
        return result, attrs
    elif type(nodes) is list:
        result = []
        for i in nodes:
            html, _ = dict_to_xml(i)
            result.append(html)
        return result, []
    elif nodes is not None:
        return nodes, []

    return '', []


def dict_to_txt(nodes):
    result = ''
    if type(nodes) is OrderedDict:
        for i in nodes:
            if i[:1] == '#':
                result += nodes[i]
            elif i[:1] == '@':
                pass
            else:
                result += "%s\n" % dict_to_txt(nodes[i])
    elif type(nodes) is list:
        for i in nodes:
            result += dict_to_txt(i) + "\n"
    elif nodes is not None:
        return nodes

    return result


if __name__ == '__main__':
    FILE = 'D:\Denis\python\onixteam\Goals.mm'
    result = freemind_load(FILE)
    # bottom = select_bottom(result)
    # for i in bottom:
    #     # print(i.get_title(), i.has_attr())
    #     i.display()

    # result[0].display()
    doc = read_xml(FILE)
    # pprint(doc)
    # print(traverse(doc, search))
    # traverse(doc, print_as_tree)
    traverse(doc, lambda n: False)
