import ConfigParser
import xlrd
from collections import *
import sys


def find_transcription_column(transcription_column_name):
    '''Finds transcription column by name and generates error message to check config file if not found'''
    all_column_headers = sh.row_slice(0)
    transcription_column_ind = None
    for column_index in range(len(all_column_headers)):
        column_header = sh.cell_value(0,column_index).strip().lower()
        if column_header == transcription_column_name:
            transcription_column_ind = column_index
    if transcription_column_ind is None:
        print "Transcription columns name '%s' not found in the excel workbook - please check your config file. Aborting." % \
              (transcription_column_name,)
        sys.exit(1)
    return transcription_column_ind


def count_word_freq(num_of_rows, transcription_column_index):
    '''Returns dictionary that records frequency of all words in transcription column'''
    word_freq = {}
    for row_ind in range(num_of_rows):
        transcription = sh.cell_value(row_ind, transcription_column_index).split()
        for word in transcription:
            if word in word_freq:
                word_freq[word] = word_freq[word] + 1
            else:
                word_freq[word] = 1
    return word_freq


if __name__ == "__main__":

    # Getting info from config file:
    sys.argv = ['transcriptionConsistencyExcel.py', 'transcriptionConsistencyExcel_config.cfg']

    config = ConfigParser.ConfigParser()
    config_file_path = sys.argv[1]
    config.read(config_file_path)

    inputfile = config.get('params', 'input_file')
    wb = xlrd.open_workbook(inputfile)

    inputtab = config.get('params', 'input_tab')
    sh = wb.sheet_by_name(inputtab)

    num_of_rows = sh.nrows

    name_of_transcription_column = config.get('params', 'transcription_column_name').strip().lower()
    transcription_column_index = find_transcription_column(name_of_transcription_column)

    word_freq = count_word_freq(num_of_rows, transcription_column_index)

    # Go through each pair or triplet of words in the normalized transcription to
    # search for cases such as "e mail" vs. "email", and "cell phone" vs. "cellphone".

    countpair = {}
    counttriplet = {}
    countquadlet = {}

    # Word pair

    for row_ind in range(1, num_of_rows):
        wordlist = []
        transcription = sh.cell_value(row_ind, transcription_column_index).split()
        for word in transcription:
            wordlist.append(word)
        if (len(wordlist) > 1):
            for i in range(1, len(wordlist)):
                wordpair = wordlist[i - 1] + wordlist[i]
                wordpairwithspace = wordlist[i - 1] + " " + wordlist[i]
                if wordpair in word_freq:
                    if wordpairwithspace in countpair:
                        countpair[wordpairwithspace] = countpair[wordpairwithspace] + 1
                    else:
                        countpair[wordpairwithspace] = 1

        # Word triplet
        if (len(wordlist) > 2):
            for i in range(2, len(wordlist)):
                wordtriplet = wordlist[i - 2] + wordlist[i - 1] + wordlist[i]
                wordtripletwithspace = wordlist[i - 2] + " " + wordlist[i - 1] + " " + wordlist[i]
                if wordtriplet in word_freq:
                    if wordtripletwithspace in counttriplet:
                        counttriplet[wordtripletwithspace] = counttriplet[wordtripletwithspace] + 1
                    else:
                        counttriplet[wordtripletwithspace] = 1

        # Word quadruplet
        if (len(wordlist) > 3):
            # print "longer than 4 words: " + line[1]
            for i in range(3, len(wordlist)):
                wordquadlet = wordlist[i - 3] + wordlist[i - 2] + wordlist[i - 1] + wordlist[i]
                wordquadletwithspace = wordlist[i - 3] + wordlist[i - 2] + " " + wordlist[i - 1] + " " + wordlist[i]
                if wordquadlet in word_freq:
                    if wordquadletwithspace in countquadlet:
                        countquadlet[wordquadletwithspace] = countquadlet[wordquadletwithspace] + 1
                    else:
                        countquadlet[wordquadletwithspace] = 1

    if countpair:
        print "\nINCONSISTENTLY TRANSCRIBED DOUBLES WITH RESPECTIVE COUNTS"
    for wordpairwithspace in countpair:
        wordpair = wordpairwithspace.replace(" ", "");
        print wordpair, ",", word_freq[wordpair], ":", wordpairwithspace, ",", countpair[wordpairwithspace]

    if counttriplet:
        print "\nINCONSISTENTLY TRANSCRIBED TRIPLETS WITH RESPECTIVE COUNTS"
    for wordtripletwithspace in counttriplet:
        wordtriplet = wordtripletwithspace.replace(" ", "");
        print wordtriplet, ",", word_freq[wordtriplet], ":", wordtripletwithspace, ",", counttriplet[
            wordtripletwithspace]

    if countquadlet:
        print "\nINCONSISTENTLY TRANSCRIBED QUADRUPLETS WITH RESPECTIVE COUNTS"
    for wordquadletwithspace in countquadlet:
        wordquadlet = wordquadletwithspace.replace(" ", "");
        print wordquadlet, ",", word_freq[wordquadlet], ":", wordquadletwithspace, ",", countquadlet[
            wordquadletwithspace]


