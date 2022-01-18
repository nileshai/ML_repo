from vietnam_number import w2n
from vietnam_number import w2n_single, w2n_couple
import pandas as pd
import re

one_digit = {"số_không": 0, "không": 0, "lẻ": 0, "một": 1, "mốt": 1, "hai": 2, "ba": 3, "bốn": 4, "tư": 4, "năm": 5, "lăm":5, "sáu": 6,
       "bảy": 7, "tám": 8, "chín": 9, "không_trăm":0}

two_digit = {"mười": 10, "hai_mươi": 20, "ba_mươi": 30, "bốn_mươi": 40, "năm_mươi": 50, "sáu_mươi": 60, "bảy_mươi": 70, "tám_mươi": 80, "chín_mươi": 90, "chín_chục": 90}

three_digit = {"lakh": 100000, "trăm": 100, "ngàn": 1000, "nghàn": 1000, "nghìn": 1000, "triệu": 1000000, "tỉ": 1000000000, "trăm_nghìn": 100000}

month = {"tháng_một":"1", "tháng_giêng":"1", "tháng_hai":"2", "tháng_ba":"3", "tháng_tư":"4", "tháng_năm":"5", "tháng_sáu": "6", "tháng_bảy":"7", "tháng_tám":"8", "tháng_chín":"9", "tháng_mười":"10", "tháng_mười_một":"11", "tháng_mười_hai":"12"}

date ={"ngày_một": "1", "ngày_hai": "2", "ngày_ba": "3", "ngày_bốn": "4", "ngày_năm": "5", "ngày_lăm": "5", "ngày_sáu": "6", "ngày_bảy": "7", "ngày_tám": "8", "ngày_chín": "9", "ngày_mười": "10", "mồng_một": "1", "mồng_hai": "2", "mồng_ba": "3", "mồng_bốn": "4", "mồng_năm": "5", "mồng_lăm": "5", "mồng_sáu": "6", "mồng_bảy": "7", "mồng_tám": "8", "mồng_chín": "9", "mồng_mười": "10", "một_tây": "1", "hai_tây": "2", "ba_tây": "3", "bốn_tây": "4", "năm_tây": "5", "lăm_tây": "5", "sáu_tây": "6", "bảy_tây": "7", "tám_tây": "8", "chín_tây": "9", "mười_tây": "10", "ngày_mười_một": "11", "ngày_mười_hai": "12", "ngày_mười_ba": "13", "ngày_mười_bốn": "14", "ngày_mười_năm": "15", "ngày_mười_lăm": "15", "ngày_mười_sáu": "16", "ngày_mười_bảy": "17", "ngày_mười_tám": "18", "ngày_mười_chín": "19", "mười_một_tây": "11", "mười_hai_tây": "12", "mười_ba_tây": "13", "mười_bốn_tây": "14", "mười_năm_tây": "15", "mười_lăm_tây": "15", "mười_sáu_tây": "16", "mười_bảy_tây": "17", "mười_tám_tây": "18", "mười_chín_tây": "19", "ngày_hai_mươi": "20", "hai_mươi_tây": "20", "ngày_hai_mốt": "21", "ngày_hai_hai": "22", "ngày_hai_ba": "23", "ngày_hai_bốn": "24", "ngày_hai_năm": "25", "ngày_hai_lăm": "25", "ngày_hai_sáu": "26", "ngày_hai_bảy": "27", "ngày_hai_tám": "28", "ngày_hai_chín": "29", "ngày_hai_mươi_mốt": "21", "ngày_hai_mươi_hai": "22", "ngày_hai_mươi_ba": "23", "ngày_hai_mươi_bốn": "24", "ngày_hai_mươi_năm": "25", "ngày_hai_mươi_lăm": "25", "ngày_hai_mươi_sáu": "26", "ngày_hai_mươi_bảy": "27", "ngày_hai_mươi_tám": "28", "ngày_hai_mươi_chín": "29", "hai_mốt_tây": "21", "hai_hai_tây": "22", "hai_ba_tây": "23", "hai_bốn_tây": "24", "hai_năm_tây": "25", "hai_lăm_tây": "25", "hai_sáu_tây": "26", "hai_bảy_tây": "27", "hai_tám_tây": "28", "hai_chín_tây": "29", "hai_mươi_mốt_tây": "21", "hai_mươi_hai_tây": "22", "hai_mươi_ba_tây": "23", "hai_mươi_bốn_tây": "24", "hai_mươi_năm_tây": "25", "hai_mươi_lăm_tây": "25", "hai_mươi_sáu_tây": "26", "hai_mươi_bảy_tây": "27", "hai_mươi_tám_tây": "28", "hai_mươi_chín_tây": "29", "ngày_ba_mươi": "30", "ba_mươi_tây": "30", "ngày_ba_mươi_mốt": "31", "ba_mươi_mốt_tây": "31", "ngày_ba_mốt": "31", "ba_mốt_tây": "31"}        

lists=["lẻ", "linh", "số_không", "không", "một", "mốt", "hai", "ba", "bốn", "tư", "năm", "lăm", "sáu", "bảy", "tám", "chín", "không_trăm", "mươi", "mười", "hai mươi", "ba mươi", "bốn_mươi", "năm_mươi", "sáu_mươi", "bảy_mươi", "tám_mươi", "chín_mươi", "chín_chục", "trăm_nghìn", "tỉ", "lakh", "trăm", "ngàn", "nghàn", "nghìn", "triệu"]

date_mon = ["tháng_đầu", "tháng_một", "tháng_giêng", "tháng_hai", "tháng_ba", "tháng_tư", "tháng_năm", "tháng_sáu", "tháng_bảy", "tháng_tám", "tháng_chín", "tháng_mười", "tháng_mười_một", "tháng_mười_hai", "ngày_một", "ngày_hai", "ngày_ba", "ngày_bốn", "ngày_năm", "ngày_lăm", "ngày_sáu", "ngày_bảy", "ngày_tám", "ngày_chín", "ngày_mười", "mồng_một", "mồng_hai", "mồng_ba", "mồng_bốn", "mồng_năm", "mồng_lăm", "mồng_sáu", "mồng_bảy", "mồng_tám", "mồng_chín", "mồng_mười", "một_tây", "hai_tây", "ba_tây", "bốn_tây", "năm_tây", "lăm_tây", "sáu_tây", "bảy_tây", "tám_tây", "chín_tây", "mười_tây", "ngày_mười_một", "ngày_mười_hai", "ngày_mười_ba", "ngày_mười_bốn", "ngày_mười_năm", "ngày_mười_lăm", "ngày_mười_sáu", "ngày_mười_bảy", "ngày_mười_tám", "ngày_mười_chín", "mười_một_tây", "mười_hai_tây", "mười_ba_tây", "mười_bốn_tây", "mười_năm_tây", "mười_lăm_tây", "mười_sáu_tây", "mười_bảy_tây", "mười_tám_tây", "mười_chín_tây", "ngày_hai_mươi", "hai_mươi_tây", "ngày_hai_mốt", "ngày_hai_hai", "ngày_hai_ba", "ngày_hai_bốn", "ngày_hai_năm", "ngày_hai_lăm", "ngày_hai_sáu", "ngày_hai_bảy", "ngày_hai_tám", "ngày_hai_chín", "ngày_hai_mươi_mốt", "ngày_hai_mươi_hai", "ngày_hai_mươi_ba", "ngày_hai_mươi_bốn", "ngày_hai_mươi_năm", "ngày_hai_mươi_lăm", "ngày_hai_mươi_sáu", "ngày_hai_mươi_bảy", "ngày_hai_mươi_tám", "ngày_hai_mươi_chín", "hai_mốt_tây", "hai_hai_tây", "hai_ba_tây", "hai_bốn_tây", "hai_năm_tây", "hai_lăm_tây", "hai_sáu_tây", "hai_bảy_tây", "hai_tám_tây", "hai_chín_tây", "hai_mươi_mốt_tây", "hai_mươi_hai_tây", "hai_mươi_ba_tây", "hai_mươi_bốn_tây", "hai_mươi_năm_tây", "hai_mươi_lăm_tây", "hai_mươi_sáu_tây", "hai_mươi_bảy_tây", "hai_mươi_tám_tây", "hai_mươi_chín_tây", "ngày_ba_mươi", "ba_mươi_tây", "ngày_ba_mươi_mốt", "ba_mươi_mốt_tây", "ngày_ba_mốt", "ba_mốt_tây"]


two_digits_file = pd.read_excel(r"./preprocess/lang/viet/VietITNtwodigits.xlsx", index_col=0)
two_digit_dict = two_digits_file.to_dict()["match"]
digits_file = pd.read_excel(r"./preprocess/lang/viet/MultiWordVietnameseITN.xlsx", index_col=0)
digit_dict = digits_file.to_dict()["match"]


def vi_preprocess(text):
    """ preprocessing """
    text = text.lower()
    input_sen = re.sub(r"^\s+", r"", text)
    input_sen = re.sub(r"\.$",r" .",text)
    input_sen = re.sub("chục","mươi", input_sen)
    input_sen = re.sub("thứ nhất","thứ một", input_sen)
    # my_file = pd.read_excel(r".\MultiWordVietnameseITN.xlsx", encoding="ISO-8859-1", index_col=0)
    # dictword = my_file.to_dict()["match"]
    for line in sorted(digit_dict.keys(), key=len, reverse=True):
        input_sen = re.sub(line, digit_dict[line], input_sen, flags=re.IGNORECASE)
    line = re.sub("-", " - ", input_sen)
    line = re.sub('\s+', ' ', line).strip()
    line_list1 = line.split(' ')
    for i, l in enumerate(line_list1):
        if i == 0:
            prev = 'nil'
            prev_prev = 'nil'
        elif i == 1:
            prev = line_list1[i - 1]
            prev_prev = 'nil'
        else:
            prev = line_list1[i - 1]
            prev_prev = line_list1[i - 2]

        if i == (len(line_list1) - 2):
            next_word = line_list1[i + 1]
            next_next_word = 'nil'
        elif i == (len(line_list1) - 1):
            next_word = 'nil'
            next_next_word = 'nil'
        else:
            next_word = line_list1[i + 1]
            next_next_word = line_list1[i + 2]

        if l in month.keys():
            if next_word == "năm":
                line_list1[i + 1] = "year"

        if l == "thứ" and line_list1[i - 1] == "năm":
            line_list1[i - 1] = "year"

        if l == "thứ":
            line_list1.remove(line_list1[i])

        if l in two_digit.keys():
            if next_word in one_digit.keys():
                if next_next_word in two_digit.keys():
                    line_list1.insert(i + 2, "and")
            elif next_word in two_digit.keys():
                line_list1.insert(i + 1, "and")

        if l == "trăm":
            if next_word in one_digit.keys():
                if next_next_word not in lists:
                    line_list1.insert(i + 1, "lẻ")

        if l in month.keys():
            if next_word == "triệu":
                if "_" in l:
                    x = l.split("_")
                    line_list1[i] = x[0]
                    line_list1.insert(i + 1, x[1])
                    line_list1.insert(i + 1, "month")

    line = ''
    line = ' '.join(str(x) for x in line_list1)
    line = re.sub("đúng không", "đúng_không", line)
    # my_file = pd.read_excel(r".\VietITNtwodigits.xlsx", encoding="ISO-8859-1", index_col=0)
    # dictword = my_file.to_dict()["match"]
    for lines in sorted(two_digit_dict.keys(), key=len, reverse=True):
        line = re.sub(lines, two_digit_dict[lines], line, flags=re.IGNORECASE)
    return line


# word2Num
def vi_word2num(text):
    string = ''
    line = re.sub('\s+', ' ', text).strip()
    line_list1 = line.split(' ')
    list_word = []
    list_num = []

    for i, l in enumerate(line_list1):
        if i == 0:
            prev = 'nil'
            prev_prev = 'nil'
        elif i == 1:
            prev = line_list1[i - 1]
            prev_prev = 'nil'
        else:
            prev = line_list1[i - 1]
            prev_prev = line_list1[i - 2]

        if i == (len(line_list1) - 2):
            next_word = line_list1[i + 1]
            next_next_word = 'nil'
        elif i == (len(line_list1) - 1):
            next_word = 'nil'
            next_next_word = 'nil'
        else:
            next_word = line_list1[i + 1]
            next_next_word = line_list1[i + 2]

        if l not in lists:
            list_word.append(l)
        elif l in lists:
            list_num.append(l)
            if next_word not in lists:
                check = all(item in list(one_digit.keys()) for item in list_num)
                x = check
                text = " ".join(list_num)
                if x is True:
                    try:
                        list_word.append(w2n_single(text))
                    except:
                        list_word.append(text)
                    finally:
                        pass
                else:
                    try:
                        list_word.append((w2n(text)))
                    except:
                        list_word.append(text)
                    finally:
                        pass
                list_num.clear()
    string = ' '.join(str(x) for x in list_word)
    string = re.sub(r"(\d\d)\sand\s(\d\d)", r"\1\2", string)
    return string


def vi_word2date(text):
    """ word2date """
    string = re.sub('\s+', ' ', text).strip()
    list_word = string.split(' ')
    list_ind = []
    for i, l in enumerate(list_word):
        if i == 0:
            prev = 'nil'
            prev_prev = 'nil'
        elif i == 1:
            prev = list_word[i - 1]
            prev_prev = 'nil'
        else:
            prev = list_word[i - 1]
            prev_prev = list_word[i - 2]

        if i == (len(list_word) - 2):
            next_word = list_word[i + 1]
            next_next_word = 'nil'
        elif i == (len(list_word) - 1):
            next_word = 'nil'
            next_next_word = 'nil'
        else:
            next_word = list_word[i + 1]
            next_next_word = list_word[i + 2]

        if l in month.keys():
            l = month[l]
            if prev in date.keys():
                list_word[i - 1] = date[prev]
            if next_word in date.keys():
                list_word[i+1] = date[next_word]
            if (re.match("^\d\d\d\d$|^\d\d$", str(next_word))):
                if prev in date.values():
                    if (re.match("^\d\d$", str(prev))):
                        list_word[i]= str(l) + '/' + str(list_word[i-1]) + '/' + str(list_word[i+1])
                        list_ind.append(i-1)
                        list_ind.append(i+1)
                    else:
                        list_word[i]= str(l) + '/' + "0" + str(list_word[i-1]) + '/' + str(list_word[i+1])
                        list_ind.append(i-1)
                        list_ind.append(i+1)
                else:
                    list_word[i]= str(l)+'/' + str(list_word[i+1])
                    list_ind.append(i+1)

            elif next_word == "year":
                if (re.match("^\d\d\d\d$|^\d\d$", str(next_next_word))):
                    if prev in date.values():
                        if (re.match("^\d\d$", str(prev))):
                            list_word[i]= str(l) + '/' + str(list_word[i-1]) + '/' + str(list_word[i+2])
                            list_ind.append(i+1)
                            list_ind.append(i-1)
                            list_ind.append(i+2)
                        else:
                            list_word[i]= str(l) + '/' + "0"+ str(list_word[i-1]) + '/' + str(list_word[i+2])
                            list_ind.append(i+1)
                            list_ind.append(i-1)
                            list_ind.append(i+2)
                    else:
                        list_word[i]= str(l)+'/'+ "00" + '/' + str(list_word[i+2])
                        list_ind.append(i+1)
                        list_ind.append(i+2)

            elif prev in date.values():
                if (re.match("^\d\d\d\d$|^\d\d$", str(prev_prev))): 
                    list_word[i]= str(l) + '/' + str(list_word[i-1]) + '/' + str(list_word[i-2])
                    list_ind.append(i-1)
                    list_ind.append(i-2)              
                else:
                    list_word[i]= str(l) + '/' + str(list_word[i-1]) + '/' + "0000"
                    list_ind.append(i-1)

            elif next_word.isnumeric()==False:
                if prev in date.values():
                    if (re.match("^\d\d$", str(prev))):
                        list_word[i]= str(l) + '/' + str(list_word[i-1]) +'/'+"0000"
                        list_ind.append(i-1)
                    else:
                        list_word[i]= str(l) + '/' +"0"+ str(list_word[i-1]) +'/'+"0000"
                        list_ind.append(i-1)                           
                elif (re.match("^\d+\/\d+$",str(prev))) and next_word in date.values():
                    list_word[i]= str(l) + '/' + str(list_word[i+1]) + '/' + "0000"
                    list_ind.append(i+1)                    
                elif (re.match("^\d\d\d\d",str(prev))):
                    list_word[i]= str(l) + '/'+ "00" + '/' + str(list_word[i-1])
                    list_ind.append(i-1)                    
                else:
                    list_word[i]= str(l) +'/'+ "00" +'/'+"0000"

            elif prev.isnumeric()==False:
                if (re.match("^\d\d\d\d$|^\d\d$", str(next_word))):
                    list_word[i]= str(l) + '/' + str(list_word[i+1]) + '/' + "0000"
                    list_ind.append(i+1)
                else:
                    list_word[i]= str(l) +'/'+ "00" +'/'+"0000"
            else:
                list_word[i]=month[l]

        elif l in date.keys():
            l=date[l]
            if (re.match("^\d\d$|^\d\d\d\d$", str(next_word))):
                list_word[i]= "00" + '/' + str(l) + '/' + str(list_word[i+1])
                list_ind.append(i+1)
            else:
                list_word[i]=l
                
        elif (re.match("^\d\d\d\d$", str(l))):
            if next_word in month.keys() and next_next_word in date.keys():
                list_word[i]= str(month[list_word[i+1]]) + '/' + str(date[list_word[i+2]]) + '/' + str(l)
                list_ind.append(i+1)
                list_ind.append(i+2)
            elif next_word in date.keys() and next_next_word in month.keys():
                list_word[i]= str(month[list_word[i+2]]) + '/' + str(date[list_word[i+1]]) + '/' + str(l)
                list_ind.append(i+1)
                list_ind.append(i+2)
            elif next_word in date.keys() and next_next_word not in month.keys():
                list_word[i]= "00" + '/' + str(date[list_word[i+1]]) + '/' + str(l)
                list_ind.append(i+1)
            elif next_word in month.keys() and next_next_word in date.values():
                list_word[i]= str(month[list_word[i+1]]) + '/' + str(list_word[i+2])  + '/' + str(l)
                list_ind.append(i+1)
                list_ind.append(i+2)
            elif next_word in date.keys() and next_next_word in month.values():
                list_word[i]= str(list_word[i+2]) + '/' +  str(date[list_word[i+1]]) + '/' + str(l)
                list_ind.append(i+1)
                list_ind.append(i+2)
            elif next_word in month.keys() and next_next_word not in date.keys():
                list_word[i]= str(month[list_word[i+1]]) + '/' + "00"  + '/' + str(l)
                list_ind.append(i+1)
            elif next_word not in month.keys() and next_next_word in date.keys():
                list_word[i]= "00" + '/' + str(date[list_word[i+2]])  + '/' + str(l)
                list_ind.append(i+2)
           
        else:
            list_word[i]=list_word[i]

    string = ' '.join([str(list_word[i]) for i in range(len(list_word)) if i not in list_ind])
    return string


def vi_post_process(string):
    """ """
    string=re.sub("đồng|VND|dong","₫",string)
    string=re.sub("_"," ",string)
    string = re.sub("rupees","INR",string)
    string = re.sub("rupee","INR",string)
    string = re.sub("dollars|US dollars}us dollars","$",string)
    string = re.sub("dollar|US dollar|usd|đô la","$",string)
    string=re.sub("\byear\b","năm",string)
    string=re.sub("month","",string)
    string=re.sub("\s+"," ",string).strip()
    string=re.sub("nhất","1",string)
    string=re.sub(r"(\d+)\s+chấm\s+(\d+)",r"\1.\2",string)
    string=re.sub(r"(\d+)\s+phết\s+(\d+)",r"\1.\2",string)
    string=re.sub(r"(\d+)\s+phẩy\s+(\d+)",r"\1.\2",string)
    string = re.sub(r"\schấm\s|\sphết\s|\sphẩy\s|\sdot\s", r".",string)
    string = re.sub(r"\sat the rate\s|\sa còng\s","@",string)
    string = re.sub(r"\sat\s","@",string)
    string=re.sub(r"đầu tiên",r"1",string)
    string=re.sub(r"(\d+)\s+xẹt\s+(\d+)",r"\1/\2",string)
    string=re.sub(r"(\d+)\s+xuyệt\s+(\d+)",r"\1/\2",string)
    string=re.sub(r"(\d+)\s+trên\s+(\d+)",r"\1/\2",string)
    string=re.sub(r"(\d+)\s+gạch\s+(\d+)",r"\1/\2",string)
    string = re.sub(r"(\d+)\s+(giờ|hours)\s+(\d+)\s+phút",r"\1:\3",string)
    string = re.sub(r"(\d+)\s+(giờ|hours)\s+(\d+)\s+sáng",r"\1:\3 A.M",string)
    string = re.sub(r"(\d+)\s+(giờ|hours)\s+(\d+)\s+chiều",r"\1:\3 P.M",string)
    string = re.sub(r"(\d+)\s+(giờ|hours)\s+rưỡi",r"\1:30",string)
    string = re.sub(r"(\d+)\s+tiếng\s+rưỡi",r"\1 tiếng 30 phút",string)
    string = re.sub(r"(\d+)\s+(giờ|hours)\s+(\d+)",r"\1:\3",string)
    string = re.sub(r"(\d+)\s+(giờ|hours)\s+sáng",r"\1:00 A.M", string)
    string = re.sub(r"(\d+)\s+(giờ|hours)\s+chiều",r"\1:00 P.M", string)
    string = re.sub(r"hợp ₫", r"hợp đồng", string)
    string = re.sub(r"\b(\d)\/(\d)\/(\d\d\d\d)\b",r"0\1/0\2/\3",string)
    string = re.sub(r"\b(\d\d)\/(\d)\/(\d\d\d\d)\b",r"\1/0\2/\3",string)
    string = re.sub(r"\b(\d)\/(\d\d)\/(\d\d\d\d)\b",r"0\1/\2/\3",string)
    string = re.sub(r"\b(\d)\/(\d)\/(\d\d)\b",r"0\1/0\2/\3",string)
    string = re.sub(r"\b(\d\d)\/(\d)\/(\d\d)\b",r"\1/0\2/\3",string)
    string = re.sub(r"\b(\d)\/(\d\d)\/(\d\d)\b",r"0\1/\2/\3",string)
    string = re.sub(r"\b(\d)\:(\d)\b",r"0\1:0\2",string)
    string = re.sub(r"\b(\d)\:(\d\d)\b",r"0\1:\2",string)
    string = re.sub(r"\b(\d\d)\:(\d)\b",r"\1:0\2",string)
    string = re.sub(r"\s*\.\s*",".",string)
    string = re.sub(r"\s*\-\s*","-",string)


    return string

def vi_timetrans(string):
    for word, day in {"sáng mai":"tomorrow morning", "tháng á":"a month", "là ngày":"days", "tuần sau":"next week", "thứ hai tới":"next monday", "thứ ba tới":"next tuesday", "thứ tư tới":"next wednesday","thứ năm tới":"next thursday","thứ Sáu tới":"next friday", "thứ bảy tới":"next saturday", "chủ nhật tới": "next sunday", "thứ hai trước":"previous monday", "thứ ba trước đó":"previous tuesday", "thứ tư trước đó": "previous wednesday", "thứ năm trước": "previous thursday", "thứ sáu trước đó": "previous friday", "thứ bảy trước" : "previous saturday", "chủ nhật trước":"previous sunday", "thứ hai cuối cùng": "last monday", "thứ ba cuối cùng":"last tuesday", "last month":"tháng trước", "last week":"tuần trước","thứ tư vừa rồi": "last wednesday", "hai tuần": "fortnight", "ngày mai": "tomorrow", "Thứ Năm tuần trước":"last thursday", "thứ sáu tuần rồi": "last friday", "thứ bảy tuần trước":"last saturday", "chủ Nhật trước":"last sunday", "thứ hai này":"this monday", "thứ ba tuần này": "this tuesday", "thứ tư này":"this wednesday", "thứ năm này":"this thursday", "thứ Sáu này": "this friday", "thứ bảy này": "this saturday", "chủ nhật này": "this sunday", "hôm nay": "today", "bữa nay":"today", "ngày hôm qua":"yesterday", "hôm qua": "yesterday", "ngày hôm kia": "day before yesterday", "tháng tiếp theo": "next month", "tháng sau": "next month", "tháng tới":"next month", "năm sau nữa":"next year", "năm sau": "next year", "năm nay": "this year", "ngày tiếp theo": "next year", "ngày này": "this day", "năm tới":"next year", "năm trước": "last year", "ngày": "days", "tháng": "months", "tuần tới":"next week", "tuần sau":"next week", "tuần trước":"previous week", "tuần này": "this week", "tuần":"weeks", "tháng này": "this month", "tháng trước":"previous month", "giờ":"hours"}.items():
        string = re.sub(word.lower(), day,string)
    string = re.sub(r"\b1\s+months\b", r"1 month",string)
    string = re.sub(r"months month", r"months", string)
    string = re.sub(r"year\s+1", r"1 year",string)
    string = re.sub(r"\byears\s+(\d+)\b", r"\1 years",string)
    string = re.sub(r"\byear\s+(\d+)\b", r"\1 years",string)
    string = re.sub(r"\b1\s+weeks\b", r"1 week",string) 
    
    return string

# print(preprocess("chín trăm mười bảy ngàn hai trăm bảy chục ngàn á"))
