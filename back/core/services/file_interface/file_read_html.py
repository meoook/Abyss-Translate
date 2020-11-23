import re

from core.services.file_interface.file_copy import CopyContextControl
from core.services.file_interface.parser_utils import ParserUtils

# regular = r'<([\w]+)(\s.*)?>\s*([^<>]+[^\s])\s*<'
# regggaa = r'<([\w]+)([^>]*)?>(\s*.*)</\1>'
#
# ONE_CONTENT_LOOK_UP = r'<([\w]+)([^>]*)?>([^\0]+)</\1>'
# xx = '(?:</\w+>|^)([^><]+)<'


class LocalizeHtmlReader(ParserUtils):
    """ Generator class: Read csv file and yield FileMark object to insert in DB """

    def __init__(self, decoded_data, data_codec, _, copy_path=''):
        assert isinstance(decoded_data, str), "Data must be type - string"
        assert isinstance(data_codec, str), "Codec must be type - string"
        self.__html_parser = _HtmlDataSeeker(decoded_data)
        self.__codec = data_codec
        # File results
        self.__file_items = 0
        self.__file_words = 0
        # Counter
        self.__elem_index = 0
        # If copy path set - create CCC object to control it
        self.__copy = CopyContextControl(copy_path, data_codec, mode='append') if copy_path else None

    @property
    def stats(self):
        return self.__file_items, self.__file_words

    def __iter__(self):
        return self

    def __next__(self):
        try:
            next(self.__html_parser)  # StopIteration raised in this method
        except StopIteration:
            if self.__copy:  # handle copy control
                self.__copy.add_data('')  # To finish file
            raise StopIteration
        # Copy controlling inside html parser
        seeker_data = self.__html_parser.data

        text = seeker_data['text']
        clean_text = self._clean_text(text)
        item_words = self._count_words(clean_text)

        if not item_words:  # Pass if no words in text
            self.__next__()

        self.__elem_index += 1  # unused TODO: remove if no need
        self.__file_items += 1  # only one item for html
        self.__file_words += item_words

        return {
            'fid': seeker_data['tree'],
            'words': item_words,
            'items': [{
                'item_number': 1,
                'md5sum': self._get_md5(text.encode(self.__codec)),
                'md5sum_clear': self._get_md5(clean_text.encode(self.__codec)),
                'words': item_words,
                'text': text,
                'warning': seeker_data['warning'],
            }, ],
            'search_words': clean_text,
            'context': seeker_data['context'],
        }

    def change_item_content_and_save(self, values: list):
        """ Return context from start of file or previous tag with replaced context of current tag """
        # if not values[0]['text']:    # DEBUG - to check final tree
        #     [print(tree_item) for tree_item in self.__html_parser.tree]  # Print tag tree
        if self.__copy:  # handle copy control
            if not values:
                self.__copy.finish()
            else:
                to_add = self.__html_parser.change_item_content_and_save(values[0]['text'])
                self.__copy.replace_and_save(to_add)  # To finish file


class _HtmlDataSeeker:
    def __init__(self, html_data):
        self.__current_value = ''
        self.__left_data = html_data  # Not parsed data
        self.__tags = [1]  # DOM tree with child index(is always last item)
        self.__tag_params = ''  # Use tag params as context
        # Content before item (from file start or item before) to create changed copy
        self.__delta_content = {'unsaved_content': '', 'current_content': ''}
        # DOM tree of elements with context
        self.__dom_tree = []  # possible use - when merge (new element added in tree)
        self.__warning = ''

    @property
    def tree(self):
        return self.__dom_tree

    def change_item_content_and_save(self, value):
        """ This method can be used - when needed to make copy of file and replace some content """
        delta_content = self.__delta_content['unsaved_content'] + value
        # Null delta content
        self.__delta_content['current_content'] = ''
        self.__delta_content['unsaved_content'] = ''
        return delta_content

    @property
    def data(self):
        """ work around with bug - that __next__ don't return value """
        val = dict(self.__current_value)
        self.__warning = ''
        self.__tag_params = ''
        return val

    def __iter__(self):
        return self

    def __next__(self):
        """ Return not parsed html data and value if it was """
        if not self.__left_data:  # no more data to parse
            raise StopIteration
        # Try to parse data as 'in tag'
        tag_data = re.match(r'^\s*[^<>]+', self.__left_data, flags=re.A)
        if not tag_data:  # Data not found
            self.__open_or_close_next_tag()
        else:
            end = tag_data.end()
            self.__data_handler(end)  # add found content
            self.__current_value = {
                'tree': self.__get_item_tree(),
                'text': tag_data.group(),
                'context': self.__tag_params.strip(),
                'warning': self.__warning,
            }

    def __open_or_close_next_tag(self):
        """ Find what tag is next and continue lookup data """
        if self.__left_data.strip().startswith('<!'):
            # tag is <!doctype html>
            end = self.__left_data.index('>') + 1
        else:
            open_tag = re.match(r'^<([\w]+)([^>]*)?>', self.__left_data)  # <tag and=params>
            if open_tag:
                tag, params = open_tag.groups('')  # '' - for no group match
                self.__tag_params = params
                self.__tags += [tag, 1]  # Add tag and it's first index to tag tree
                # Close tag without content or other no-value-html-tags (<br/> <img .../> or <hr><br>)
                if tag in ['script', 'style', 'meta', 'link'] \
                        or tag[-1] == '/' \
                        or (params and params[-1] == '/')\
                        or (tag in ['br', 'hr', ] and not params):
                    self.__close_tag(tag)
                end = open_tag.end()
            else:
                closed_tag = re.match(r'^\s*</([\w]+)>', self.__left_data)
                if closed_tag:
                    self.__close_tag(closed_tag.group(1))
                    end = closed_tag.end()
                else:
                    # unknown data - add to the end of context
                    end = len(self.__left_data)
        self.__data_handler(end)
        self.__next__()

    def __data_handler(self, cut_index):
        """ Update unsaved content and left data """
        self.__delta_content['unsaved_content'] += self.__delta_content['current_content']
        self.__delta_content['current_content'] = self.__left_data[:cut_index]  # add found content
        self.__left_data = self.__left_data[cut_index:]  # refresh not parsed data

    def __close_tag(self, tag_name):
        """ Handle closing tag - update tag tree """
        if tag_name in self.__tags:
            if self.__tags[-2] == tag_name:
                self.__tags = self.__tags[:-2]
            else:
                # tag not the last in tree (tree cut error)
                self.__warning = 'previous tag was not closed'
                tag_index_from_right = len(self.__tags) - 1 - self.__tags[::-1].index(tag_name)
                self.__tags = self.__tags[:tag_index_from_right]
            self.__tags[-1] += 1  # increment index for next child
        else:
            # close tag not found in tree (tree error)
            self.__warning = 'incorrect close tag before previous'

    def __get_item_tree(self):
        """ Get item DOM tree """
        item_tree = ':'.join([str(tag) for tag in self.__tags])
        self.__dom_tree.append(item_tree)
        return item_tree
