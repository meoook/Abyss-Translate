import re


class HtmlContextControl:
    """ Control text data in HTML document """

    def __init__(self, html_data: str, *_args):
        self.__left_data: str = html_data  # Not parsed data
        # Class props to return
        self.__dom_data: list[dict[str, str]] = []  # List of DOM-tree items (item where is valid text)
        self.__dom_tree: list[str] = []   # DOM tree of elements with context
        # Element props while parsing
        self.__elem_dom: list[any] = [1]  # Element DOM tree (index is always last item)
        self.__elem_prefix: str = ''      # Element technical text before valid text
        self.__elem_warning: str = ''     # Element warning (DOM tree errors like 'tag not closed')

        self.__parse()

    def __parse(self):
        """ Parse file while not EOF """
        while self.__next_parse():
            pass
        # Add left data to return data as 'EOF'
        _data_tail = {'dom': 'EOF', 'text': self.__elem_prefix, 'prefix': self.__elem_prefix, 'warning': 'end of file'}
        self.__dom_data.append(_data_tail)

    @property
    def tree(self) -> list[str]:
        return self.__dom_tree

    @property
    def data(self) -> list[dict[str, str]]:
        """ Dict of DOM-tree items. Item is a tag where valid text (context without close tag). """
        return self.__dom_data

    def __next_parse(self) -> bool:
        """ Parse next part of file to find valid text """
        if not self.__left_data:  # no more data to parse
            return False
        # Check for newline at start
        _start_with_newline = re.match(r'[\r\n]+(.*)', self.__left_data)
        if _start_with_newline:
            _cut_idx = _start_with_newline.start(1)
            self.__prefix_add(_cut_idx)  # Add \r or \n to prefix
            return True
        # Try to parse data as 'in tag'
        tag_data = re.match(r'[^<>]+', self.__left_data, flags=re.A)
        if not tag_data:  # Data not found
            self.__open_or_close_next_tag()
        else:
            _text: str = tag_data.group()
            _cut_idx: int = tag_data.end()
            try:
                float(_text)
            except ValueError:
                if _text.strip():  # If 'next' valid
                    _prefix = self.__prefix_return(_cut_idx)  # Will null prefix
                    _warning = self.__warning_return()    # Will null warning
                    _dom_tree = self.__elem_dom_string()
                    _text = self.__handle_newline(_text)  # If text end with \r \n cut them and add to next prefix
                    self.__dom_data.append({'dom': _dom_tree, 'text': _text, 'prefix': _prefix, 'warning': _warning})
                    return True
            self.__prefix_add(_cut_idx)  # If 'next' not valid
        return True

    def __warning_return(self) -> str:
        """ Return warning and null it """
        _warning = f'{self.__elem_warning}'
        self.__elem_warning = ''
        return _warning

    def __prefix_return(self, cut_index: int) -> str:
        """ Return prefix and refresh data """
        _prefix = f'{self.__elem_prefix}'
        self.__elem_prefix = ''
        self.__left_data = self.__left_data[cut_index:]  # refresh not parsed data
        return _prefix

    def __prefix_add(self, cut_index: int) -> None:
        """ Update prefix and left data """
        self.__elem_prefix += self.__left_data[:cut_index]
        self.__left_data = self.__left_data[cut_index:]  # refresh not parsed data

    def __open_or_close_next_tag(self) -> None:
        """ Find what tag is next and continue lookup data """
        if self.__left_data.strip().startswith('<!'):
            # tag is <!doctype>
            _cut_idx: int = self.__left_data.index('>') + 1  # index in row where tag ends
        else:
            open_tag = re.match(r'^<([\w]+)([^>]*)?>', self.__left_data)  # <tag and=params>
            if open_tag:
                tag, _tag_params = open_tag.groups('')  # '' - for no group match
                self.__elem_dom += [tag, 1]  # Add tag and it's first index to tag tree
                # Close tag without content or other no-value-html-tags (<br/> <img .../> or <hr><br>)
                if tag in ['script', 'style', 'meta', 'link'] \
                        or tag[-1] == '/' \
                        or (_tag_params and _tag_params[-1] == '/')\
                        or (tag in ['br', 'hr'] and not _tag_params):
                    self.__close_tag(tag)
                _cut_idx = open_tag.end()
            else:
                closed_tag = re.match(r'^\s*</([\w]+)>', self.__left_data)
                if closed_tag:
                    self.__close_tag(closed_tag.group(1))
                    _cut_idx = closed_tag.end()
                else:
                    # unknown data - add to the end of context
                    _cut_idx = len(self.__left_data)
        self.__prefix_add(_cut_idx)

    def __close_tag(self, tag_name: str) -> None:
        """ Handle closing tag - update tag tree """
        if tag_name in self.__elem_dom:
            if self.__elem_dom[-2] == tag_name:
                self.__elem_dom = self.__elem_dom[:-2]
            else:
                # tag not the last in tree (tree cut error)
                self.__elem_warning = 'previous tag was not closed'
                tag_index_from_right = len(self.__elem_dom) - 1 - self.__elem_dom[::-1].index(tag_name)
                self.__elem_dom = self.__elem_dom[:tag_index_from_right]
            self.__elem_dom[-1] += 1  # increment index for next child
        else:
            # close tag not found in tree (tree error)
            self.__elem_warning = 'incorrect close tag before previous'

    def __elem_dom_string(self) -> str:
        """ Get item DOM tree """
        item_tree = ':'.join([str(tag) for tag in self.__elem_dom])
        self.__dom_tree.append(item_tree)
        return item_tree

    def __handle_newline(self, text: str) -> str:
        """ If text ends with newline - add it to next prefix  """
        _validate = re.fullmatch(r'(.*?)[\r\n]+$', text)
        if _validate:
            _index = _validate.end(1)
            self.__elem_prefix += text[_index:]  # elem_prefix must be empty at this moment
            return text[:_index]
        return text
