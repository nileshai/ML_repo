from typing import List
from summary.data.evaluate_model_request import ModelRequest
from summary.data.summary import Entity
import re
import sys
from summary.constants import logger
from summary.predefined_entities.entity_type import EntityType
from summary.predefined_entities.utils import remove_entity_from_line
from summary.predefined_entities import pattern_based_entity as pattern_based_entity_extractor


def get_pattern_entities(model_request: ModelRequest) -> List[Entity]:
    """"""
    transcripts = model_request.transcripts
    entities = []
    for index, turn in enumerate(transcripts):
        # channel = turn.split(':')[0].strip()
        channel = turn.turn_channel.strip()
        # detected entities will be removed from the text 'line' to avoid overlap entities
        # line = turn.split(':')[1].strip()
        line = turn.turn_text.strip()
        # unmodified text of each turn from the transcript
        # turn_text = turn.split(':')[1].strip()
        turn_text = turn.turn_text.strip()
        turn_id = turn.line_no
        raw_turn_id = turn.raw_turn_id
        # NTE outputs spelled characters in upper case so not lowering the case before alphanumeric entity detection.
        line, alphanumeric_entities = alphanumeric_entity(line, turn_id, channel, turn_text, raw_turn_id)
        line, turn_text = line.lower(), turn_text.lower()

        line, relationship_entities = relationship_entity(line, turn_id, channel, turn_text, raw_turn_id)
        line, affirmation_entities = affirmation_entity(line, turn_id, channel, turn_text, raw_turn_id)
        line, date_entities = date_entity(line, turn_id, channel, turn_text, raw_turn_id)
        line, percentage_entities = percentage_entity(line, turn_id, channel, turn_text, raw_turn_id)
        line, money_entities = money_entity(line, turn_id, channel, turn_text, raw_turn_id)
        line, float_entities = float_entity(line, turn_id, channel, turn_text, raw_turn_id)
        line, duration_entities = duration_entity(line, turn_id, channel, turn_text, raw_turn_id)
        line, cardinal_entities = cardinal_entity(line, turn_id, channel, turn_text, raw_turn_id)

        all_entities = alphanumeric_entities + relationship_entities + affirmation_entities + date_entities + \
                       percentage_entities + money_entities + float_entities + duration_entities + cardinal_entities
        entities.extend(all_entities)
    return entities


def alphanumeric_entity(line: str, turn_number: int, channel: str, turn_text: str, raw_turn_id: List[int]) -> (str, List[Entity]):
    """ALPHANUMERIC entity - since NTE outputs spelled characters in upper case, looking for alphanumeric before
        lowering the case"""
    char_float_num = r'(((\b[A-Z]+\s)+([0-9]+\s)+((points|point|dot|\.)+\s+[A-Z0-9]+(?!\/)\b\s*)+)+)'
    float_num_char = r'((^|\s)[0-9]+\s(points|point|dot|\.)\s[0-9]+(?!\/)\s([A-Z]+\b\s*)+)'
    char_float_num_expansion = r'((((\b[A-Z]+\s)|((\b[A-Z]+\s)+(as in|like in|like|for)\s\w+\s))+[0-9]+\s)+' \
                               r'((points|point|dot|\.)+\s+[A-Z0-9]+(?!\/)(\s|\b))+)'
    float_num_char_expansion = r'((^|\s)[0-9]+\s(points|point|dot|\.)\s[0-9]+\s((([A-Z]+\s)+(as in|like in|like|for)' \
                               r'\s\w+(\s|\b))|([A-Z]+(\s|\b)))+)'
    caps_alpha_float_numerics = char_float_num_expansion + "|" + float_num_char_expansion + "|" + char_float_num \
                                + "|" + float_num_char

    char_num = r'(((\b[A-Z]+\s)+([0-9]+(?!\/)\b\s*)+([A-Z0-9]+(?!\/)\b\s*)*)+)'
    num_char = r'(((^|\s)[0-9]+(?!\/)\s([A-Z]+\b\s*)+([A-Z0-9]+(?!\/)\b\s*)*)+)'
    char_num_expansion = r'((((\b[A-Z]+\s)|((\b[A-Z]+\s)+(as in|like in|like|for)\s\w+\s))+[0-9]+(?!\/)\b\s*' \
                         r'(((\b[A-Z]+\s)+(as in|like in|like|for)\s\w+(\s|\b))|([A-Z]+\s|[A-Z]+\b)+' \
                         r'|[0-9]+(?!\/)\b\s*)*)+)'
    num_char_expansion = r'(((^|\s)[0-9]+(?!\/)\s((([A-Z]+\s)+(as in|like in|like|for)\s\w+(\s|\b))|' \
                         r'([A-Z]+\s))+((([A-Z]+\s)+(as in|like in|like|for)\s\w+(\s|\b))|' \
                         r'([A-Z]+\s|[A-Z]+\b)+|[0-9]+(?!\/)\b\s*)*)+)'
    general_alphanum = r'(?=[^\s]*?[0-9])(?=[^\s]*?[a-zA-Z])[a-zA-Z0-9]*'
    caps_alpha_pattern = caps_alpha_float_numerics + "|" + char_num_expansion + "|" + num_char_expansion + "|" + \
                         char_num + "|" + num_char + "|" + general_alphanum
    check_expansion_pattern = r'([A-Z])\s(as in|like in|like|for)\s(\w+)'
    # remove_expansion_pattern = r'(como en|como de|de)\s\w+'
    # remove_float_pattern = r'(puntos|punto)'
    return pattern_based_entity_extractor.alphanumeric_entity(caps_alpha_pattern, check_expansion_pattern, line,
                                                              turn_number, channel, turn_text, raw_turn_id)


def relationship_entity(line: str, turn_number: int, channel: str, turn_text: str, raw_turn_id: List[int]):
    """ RELATIONSHIP entity detection (eg: friend, wife, spouse, son etc.,) """
    relationship_pattern = r'\bcolleague\b|\bfriend\b|\bmother in law\b|\bfather in law\b|\bdaughter\b|\bson\b|' \
                           r'\bsister\b|\bbrother\b|\bwife\b|\bmother-in-law\b|\bfather-in-law\b|\bhusband\b|' \
                           r'\bhubby\b|\bcousin\b|\bmother\b|\bfather\b|\bfamily\b|\bboss\b|\bpa\b|\bassistant\b|' \
                           r'\bpartner\b|\bclient\b|\bcustomer\b|\bmanager\b'
    return pattern_based_entity_extractor.relationship_entity(relationship_pattern, line, turn_number, channel, turn_text, raw_turn_id)


def affirmation_entity(line: str, turn_number: int, channel: str, turn_text: str, raw_turn_id: List[int]):
    """ Detects affirmation based on yes/no related keywords """
    affirmation_pattern = r'\byeah\b|yeah please|thank you|ok thank you|okay thank you|\bokay thanks\b|' \
                          r'\bok thank you\b|\bok thanks\b|\byes\b|yes please|\bplease\b|\bsure\b|sure yeah|' \
                          r'yeah ok|yeah okay|yeah that\'s fine|yeah thats fine|\bright\b|\ball right\b|' \
                          r'\balright\b|\bok\b|\bokay\b|\bokay fine\b|\bok fine\b'
    negation_pattern = r'\bno\b|\bnope\b|i don\'t think|i don\'t want to|i dont think|i dont want to'
    return pattern_based_entity_extractor.affirmation_entity(affirmation_pattern, negation_pattern, line, turn_number,
                                                             channel, turn_text, raw_turn_id)


def date_entity(line: str, turn_number: int, channel: str, turn_text: str, raw_turn_id: List[int]):
    """ Detects date and date range (formats: d/d/d, d/d/, d/d/d to d/d/d, d/d/d through d/d/d, etc..) """
    date_range_pattern = r'((\d{1,2}/\d{1,2}/(\d{1}|\d{2}|\d{4})(\b|\s)|\d{1,2}/\d{1,2}/(\b|\s))\s' \
                         r'(\bto\b|\bthrough\b|\buntil\b|\btill\b)\s' \
                         r'(\d{1,2}/\d{1,2}/(\d{1}|\d{2}|\d{4})\b|\d{1,2}/\d{1,2}/(\s|$)))'
    full_date_pattern = r'\d{1,2}/\d{1,2}/(\d{1}|\d{2}|\d{4})\b'
    partial_date_pattern = r'\d{1,2}/\d{1,2}/(\s|$)'
    relative_date_pattern = r'(today|tomorrow|yesterday)'
    relative_year_pattern = r'((\d+\/\d+\/0|\d+\/\d+\/|\d+\/0\/0)\s(of\s)?' \
                            r'(\bthis year\b|\blast year\b|\bnext year\b))'
    relative_months = r'\bthis month\b|\blast month\b|\bnext month\b'
    relative_month_pattern = r'((\d+\s(of\s)?({0})\s\d+)|(\d+\s(of\s)?({1}))|(({2})\s(of\s)?\d+|({3})))'.format(
        relative_months, relative_months, relative_months, relative_months)
    final_date_pattern = relative_year_pattern + "|" + relative_month_pattern + "|" + date_range_pattern + "|" + \
                         full_date_pattern + "|" + partial_date_pattern + "|" + relative_date_pattern
    return pattern_based_entity_extractor.date_entity(final_date_pattern, line, turn_number, channel, turn_text, raw_turn_id)


def percentage_entity(line: str, turn_number: int, channel: str, turn_text: str, raw_turn_id: List[int]):
    """ Detects percentage related entities """
    percentage_pattern = r'(\b\d+ percent\b|\b\d+ percentage\b|\b\d+%|\b\d+\s%)'
    # words_to_symbol = r'(\bpor ciento\b|\bporcentaje\b)'
    return pattern_based_entity_extractor.percentage_entity(percentage_pattern, line, turn_number,
                                                            channel, turn_text, raw_turn_id)


def money_entity(line: str, turn_number: int, channel: str, turn_text: str, raw_turn_id: List[int]):
    """ Detects currency entities
        Supported currencies: dollars, US dollars, Euro, INR, Korean Von, australian dollar, british pound
    """
    dollars_pattern = r'((\d+)\s(\bus\b|\baustralian\b)?\s?(\bdollar\b|\bdollars\b)\s(\bpoint\b|\bdot\b|\band\b)?\s?' \
                      r'(\d+)\s(\bcent\b|\bcents\b))|((\d+)\s(\bus\b|\baustralian\b)?\s?(\bdollar\b|\bdollars\b))|' \
                      r'((\d+)\s(\bpoint\b|\bdot\b)\s(\d+)\s(\bus\b|\baustralian\b)?\s?(\bdollar\b|\bdollars\b))'
    euro_pattern = r'((\d+)\s(\beuros\b|\beuro\b|\bpounds\b|\bpound\b|\bquid\b))'
    rupee_pattern = r'((\d+)\s(\bindian\b|\bindia\b)?\s?(\brupees\b|\brupee\b|\binr\b))'
    won_pattern = r'((\d+)\s(\bkorean\b|\bcorian\b)\s(\bwon\b|\bvon\b))'
    yen_pattern = r'((\d+)\s(\bjapanese\b|\bjapan\b)?\s?(\byen\b))'
    money_pattern = dollars_pattern + '|' + euro_pattern + '|' + rupee_pattern + '|' + won_pattern + '|' + yen_pattern
    return pattern_based_entity_extractor.money_entity(money_pattern, line, turn_number, channel, turn_text, raw_turn_id)


def float_entity(line: str, turn_number: int, channel: str, turn_text: str, raw_turn_id: List[int]):
    """ Detects float entities (eg: 78.96, 45 point 69)"""
    float_pattern = r'(\d+\.\d+|\d+ points \d+|\d+ point \d+|\d+ dot \d+)'
    # words_to_symbol = r'(\bpuntos\b|\bpunto\b)'
    return pattern_based_entity_extractor.float_entity(float_pattern, line, turn_number, channel, turn_text, raw_turn_id)


def duration_entity(line: str, turn_number: int, channel: str, turn_text: str, raw_turn_id: List[int]):
    """ Detects duration entities (eg: 5 to 8 days/weeks/months/years/hours/minutes/working days/business days) """
    words = ["day", "minute", "hour", "week", "month", "year"]
    rewrite_words = ["days", "minutes", "hours", "weeks", "months", "years"]
    for index, word in enumerate(words):
        line = re.sub(r'\b%s\b' % word, rewrite_words[index], line)
    duration_pattern = r'\d+ to \d+ days|\d+ to \d+ business days|\d+ to \d+ minutes|\d+ minutes|\d+ days|' \
                       r'\d+ business days|\d+ to \d+ working days|\d+ working days|\d+ to \d+ hours|' \
                       r'\d+ hours|\d+ to \d+ weeks|\d+ weeks|\d+ to \d+ months|\d+ months|\d+ to \d+ years|' \
                       r'\d+ years'
    return pattern_based_entity_extractor.duration_entity(duration_pattern, line, turn_number, channel, turn_text, raw_turn_id)


def cardinal_entity(line: str, turn_number: int, channel: str, turn_text: str, raw_turn_id: List[int]):
    """ Detects Cardinal values """
    cardinal_all = r'(\d+)'
    return pattern_based_entity_extractor.cardinal_entity(cardinal_all, line, turn_number, channel, turn_text, raw_turn_id)
