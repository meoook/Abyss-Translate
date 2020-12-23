import re


class HtmlContextParser:
    """ Control text data in HTML document """

    __INVALID_DATA_TAGS = ['script', 'style']
    __AUTO_CLOSE_TAGS = ['meta', 'link', 'br', 'hr', 'img', 'input']

    def __init__(self, html_data: str, *_args):
        # re.purge()
        self.__left_data: str = html_data  # Not parsed data
        # Class props to return
        self.__dom_data: list[dict[str, str]] = []  # List of DOM-tree items (item where is valid text)
        self.__dom_tree: list[str] = []   # DOM tree of elements with context
        # Element props while parsing
        self.__elem_dom: list[any] = [1, ]  # Element DOM tree *Unique* (index is always last item)
        self.__elem_prefix: str = ''      # Element technical text before valid text
        self.__elem_warning: str = ''     # Element warning (DOM tree errors like 'tag not closed')

        self.__parse()

    def __parse(self):
        """ Parse file while not EOF """
        while self.__next_parse():
            pass

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
            _prefix = self.__prefix_return(0)
            _data_tail = {'dom': 'EOF', 'text': _prefix, 'prefix': _prefix, 'warning': 'end of file'}
            self.__dom_data.append(_data_tail)  # Add left data to return data as 'EOF'
            return False
        # Check for newline at start
        _start_with_newline = re.match(r'[\r\n]+(.*)', self.__left_data)
        if _start_with_newline:
            _cut_idx = _start_with_newline.start(1)
            self.__prefix_add(_cut_idx)  # Add \r or \n to prefix
            return True
        # Try to parse data as 'in tag'
        _tag_data = re.match(r'[^<]+', self.__left_data, flags=re.A)
        # _tag_data = re.match(r'[^<]+', self.__left_data)
        if not _tag_data:  # Data not found
            self.__open_or_close_next_tag()
        else:
            _text: str = _tag_data.group()
            _cut_idx: int = _tag_data.end()
            try:
                float(_text)
            except ValueError:
                if self.__is_text_valid(_text):  # URL check
                    _prefix = self.__prefix_return(_cut_idx)  # Will null prefix
                    _warning = self.__warning_return()    # Will null warning
                    _dom_tree = self.__elem_dom_string()  # Save element dom position to dom tree
                    _text = self.__handle_newline(_text)  # If text end with \r \n cut them and add to next prefix
                    self.__dom_data.append({'dom': _dom_tree, 'text': _text, 'prefix': _prefix, 'warning': _warning})
                    return True
            # If 'next' not valid
            self.__prefix_add(_cut_idx)
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
        """ Find what tag is next """
        _next_tag = re.match(r'<(/?\w+)+([^>]*)?>', self.__left_data)  # <tag_name and=params>
        if _next_tag:
            _tag_name, _tag_params = _next_tag.groups('')  # '' - as default
            _tag_name = _tag_name.lower()
            # Handle left data
            _cut_idx = _next_tag.end()
            self.__prefix_add(_cut_idx)

            if _tag_name.startswith('/'):  # Close tag - remove from dom tree
                self.__tag_dom_close(_tag_name[1:])
            else:  # Open tag - add tag and it's first index to dom tree
                self.__elem_dom += [_tag_name, 1]
                self.__tag_check_auto_close(_tag_name, _tag_params)
        elif re.match(r'</?(\W)+([^>]*)?>', self.__left_data.strip()):
            # tag like <!doctype> or unknown tags <?> ignored in DOM tree
            _cut_idx: int = self.__left_data.index('>') + 1
            self.__prefix_add(_cut_idx)
        else:  # Data broken - left data have no '<...>' pattern
            _cut_idx = len(self.__left_data)
            self.__prefix_add(_cut_idx)
            _prefix = self.__prefix_return(_cut_idx)
            _data_tail = {'dom': 'EOF', 'text': _prefix, 'prefix': _prefix, 'warning': 'data broken'}
            self.__dom_data.append(_data_tail)  # Add left data to return data as 'EOF'

    def __tag_check_auto_close(self, tag_name: str, tag_params: str) -> None:
        """ Open tag and check for auto-closed - if so -> return True """
        if tag_name in self.__INVALID_DATA_TAGS:
            # Auto-close not-valid-html-tags (<script> and <style>) and cut data inside them
            _cut_idx: int = self.__left_data.index(f'</{tag_name}')
            self.__prefix_add(_cut_idx)
        elif tag_name in self.__AUTO_CLOSE_TAGS or tag_name[-1] == '/' or (tag_params and tag_params[-1] == '/'):
            # Auto-close tags without content(<hr>, <br>) or <img... /> <input... />
            self.__tag_dom_close(tag_name)

    def __tag_dom_close(self, tag_name: str) -> None:
        """ Handle closing tag - update tag tree """
        if tag_name in self.__elem_dom:
            if self.__elem_dom[-2] == tag_name:
                self.__elem_dom = self.__elem_dom[:-2]
            else:
                # tag not at the end of a tree (tree cut error)
                self.__elem_warning = 'dom tree error - previous tag was not closed'
                _fix_dom_tree_cut_deep = len(self.__elem_dom) - 1 - self.__elem_dom[::-1].index(tag_name)
                self.__elem_dom = self.__elem_dom[:_fix_dom_tree_cut_deep]
            self.__elem_dom[-1] += 1  # increment index for next child
        else:
            # close tag not found in tree (tree error)
            self.__elem_warning = 'dom tree error - close tag have no open tag'

    def __elem_dom_string(self) -> str:
        """ Get tag and DOM tree of last element  """
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

    @staticmethod
    def __is_text_valid(text: str) -> bool:
        """ Validate text """
        try:  # Float check
            float(text)
            return False
        except ValueError:
            pass
        _text = text.strip()
        if ' ' in _text:
            return True
        elif _text and re.match(r'[^.:/\s]+.$', _text):  # Not empty and not URL or like technical
            return True
        else:
            return False
