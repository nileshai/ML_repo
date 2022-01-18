import sys
from typing import List
from summary.data.evaluate_model_request import ModelRequest
from summary.data.summry import Entity                             ##call this file based on production version location
import re
from summary.constants import logger                                ##call this file based on production version location
from summary.predefined_entities.entity_type import EntityType      ##call this file based on production version location


def contact_entity(contact_pattern: str, line: str, turn_number: int, channel: str, turn_text: str, raw_turn_id: List[int]):
    contact_all = list(re.finditer(contact_pattern, line))
    contact_entities = []
    if len(contact_all) > 0:
        for contact in contact_all:
            try:
                start_index = re.compile(r'\b%s\b'%contact.group()).search(turn_text).span()[0]
                contact_word_list = list(re.finditer(r'\b%s\b' % contact.group(), turn_text))
                for contact_word in contact_word_list:
                    start_idx = [contact_word.start()]
                    for st_idx in start_idx:
                        word_start_index = len(turn_text[:st_idx].strip().split())
                        contact_entities.append(
                            Entity(EntityType.CARDINAL, contact.group(), start_index, len(contact.group()),
                                   word_start_index, turn_number, channel, turn_text, raw_turn_id))
            except Exception as err:
                logger.debug("Error in contact entity")
                logger.debug(repr(err))
                logger.debug("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    return line, contact_entities
    

def alphanumeric_entity(reg_pattern: str, line: str, turn_number: int, channel: str, turn_text: str, raw_turn_id: List[int]):
    reg_all = list(re.finditer(reg_pattern, line))
    reg_entities = []
    if len(reg_all) > 0:
        for reg in reg_all:
            try:
                start_index = re.compile(r'\b%s\b'%reg.group()).search(turn_text).span()[0]
                reg_word_list = list(re.finditer(r'\b%s\b' % reg.group(), turn_text))
                for reg_word in reg_word_list:
                    start_idx = [reg_word.start()]
                    for st_idx in start_idx:
                        word_start_index = len(turn_text[:st_idx].strip().split())
                        reg_entities.append(
                            Entity(EntityType.ALPHANUMERIC, reg.group(), start_index, len(reg.group()),
                                   word_start_index, turn_number, channel, turn_text, raw_turn_id))
            except Exception as err:
                logger.debug("Error in alphanumeric entity")
                logger.debug(repr(err))
                logger.debug("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    return line, reg_entities