import logging
import re
from abc import ABC, abstractmethod
from checkov.terraform.context_parsers.registry import parser_registry
from checkov.terraform.models.enums import ContextCategories
from itertools import islice

OPEN_CURLY = '{'
CLOSE_CURLY = '}'


class BaseContextParser(ABC):
    definition_type = ""
    tf_file = ""
    file_lines = []
    context = {}

    def __init__(self, definition_type):
        self.logger = logging.getLogger("{}".format(self.__module__))
        if definition_type not in ContextCategories.__members__:
            self.logger.error("Terraform context parser type not supported")
            raise Exception()

        self.definition_type = definition_type
        parser_registry.register(self)

    def parse_file_lines(self, tf_file):
        self.tf_file = tf_file
        with(open(tf_file, 'r')) as file:
            file.seek(0)
            file_lines = [(ind + 1, re.sub('\s+', ' ', line).strip()) for (ind, line) in
                          list(enumerate(file.readlines()))]
            file_lines = [(ind, line) for (ind, line) in file_lines if line]
            self.file_lines = file_lines

    def compute_definition_end_line(self, start_line_num):
        start_line_idx = [line_num for (line_num, _) in self.file_lines].index(start_line_num)
        i = 1
        end_line_num = 0
        for (line_num, line) in islice(self.file_lines, start_line_idx+1, None):
            if OPEN_CURLY in line:
                i = i+1
            if CLOSE_CURLY in line:
                i = i-1
                if i == 0:
                    end_line_num = line_num
                    break
        return end_line_num

    @abstractmethod
    def enrich_definition_block(self, definition):
        raise NotImplementedError()
