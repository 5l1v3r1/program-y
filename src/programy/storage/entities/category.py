"""
Copyright (c) 2016-2019 Keith Sterling http://www.keithsterling.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import re
from programy.utils.parsing.linenumxml import LineNumberingParser
import xml.etree.ElementTree as ET  # pylint: disable=wrong-import-order
from programy.utils.logging.ylogger import YLogger
from programy.storage.entities.store import Store
from programy.parser.aiml_parser import AIMLParser
from programy.parser.exceptions import ParserException
from programy.parser.exceptions import DuplicateGrammarException


class CategoryReadOnlyStore(Store):
    WHITESPACE = re.compile('[\n\t\r+]')

    def __init__(self):
        Store.__init__(self)

    def load_all(self, collector):
        raise NotImplementedError("load_all missing from Category Store")

    def load(self, collector, name=None):
        raise NotImplementedError("load missing from Category Store")

    @staticmethod
    def extract_content(name, element):
        content = ET.tostring(element, encoding='utf-8', method='xml').decode('utf-8')
        content = CategoryReadOnlyStore.WHITESPACE.sub('', content)
        content = content.replace('<br>', '<br />')
        content = re.sub(r'\s+', ' ', content)
        start = '<%s>' % name
        end = '</%s>' % name
        firstpos = content.find(start)
        lastpos = content.rfind(end)

        return content[firstpos + len(start):lastpos]

    def find_all(self, element, name, namespace):
        if namespace is not None:
            search = '%s%s' % (namespace, name)
            return element.findall(search)
        return element.findall(name)

    def find_element_str(self, name, xml, namespace):
        elements = self.find_all(xml, name, namespace)
        if len(elements) > 1:
            raise Exception("Multiple <%s> nodes found in category" % name)

        elif len(elements) == 1:
            return CategoryReadOnlyStore.extract_content(name, elements[0])

        return "*"

    def _load_category(self, groupid, pattern, topic, that, template, parser):

        text = \
            """<category>
                <pattern>%s</pattern>
                <topic>%s</topic>
                <that>%s</that>
                <template>%s</template>
            </category>""" % (pattern, topic, that, template)

        xml = None
        try:
            xml = ET.fromstring(text)
            parser.parse_category(xml, None)

        except DuplicateGrammarException as dupe_excep:
            parser.handle_aiml_duplicate(dupe_excep, groupid, xml)

        except ParserException as parser_excep:
            parser.handle_aiml_error(parser_excep, groupid, xml)

        except Exception as excep:
            YLogger.exception_nostack(self, "Error loading category from db", excep)


class CategoryReadWriteStore(CategoryReadOnlyStore):

    def __init__(self):
        CategoryReadOnlyStore.__init__(self)

    def upload_from_file(self, filename, fileformat=Store.XML_FORMAT, commit=True, verbose=False):
        count = 0
        success = 0

        try:
            groupname = Store.get_just_filename_from_filepath(filename)
            print(groupname)

            tree = ET.parse(filename, parser=LineNumberingParser())
            aiml = tree.getroot()

            for expression in aiml:
                tag_name, namespace = AIMLParser.tag_and_namespace_from_text(expression.tag)
                if tag_name == 'topic':
                    topic = expression.attrib['name']
                    for topic_expression in expression:
                        that = self.find_element_str("that", topic_expression, namespace)
                        pattern = self.find_element_str("pattern", topic_expression, namespace)
                        template = self.find_element_str("template", topic_expression, namespace)
                        if self.store_category(groupname, "*", topic, that, pattern, template) is True:
                            success += 1
                        count += 1

                elif tag_name == 'category':
                    topic = self.find_element_str("topic", expression, namespace)
                    that = self.find_element_str("that", expression, namespace)
                    pattern = self.find_element_str("pattern", expression, namespace)
                    template = self.find_element_str("template", expression, namespace)
                    if self.store_category(groupname, "*", topic, that, pattern, template) is True:
                        success += 1
                    count += 1

        except Exception as excep:
            YLogger.exception(self, "Failed to load contents of AIML file from [%s]", excep, filename)

        return count, success

    def store_category(self, groupid, userid, topic, that, pattern, template):
        raise NotImplementedError("store_category missing from Category Store")
