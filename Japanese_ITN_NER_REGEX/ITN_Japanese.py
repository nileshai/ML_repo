from datetime import date
import japanese_numbers
import pandas as pd
import re


# pipeline instantiate Jpn_number_model
# call functions preprocess -> word2date -> word2time -> jpn_number -> postprocess of Jpn_number_model
class Jpn_number_model: 
    def __init__(self):
        super().__init__()
        self.address = []
        self.gpe_ent = []
        self.money = []
        self.ent = []
    
    def preprocess(self, sen):
        self.address = []
        self.gpe_ent = []
        self.money = []
        self.ent = []
        pat = re.findall('(?=([〇一二三四五六七八九十百千万億兆]\s[〇一二三四五六七八九十百千万億兆]))', sen)
        for i in pat:
            sen = re.sub(i, ''.join(i.split(' ')), sen)
        pattern = re.findall('〇', sen)
        for i in pattern:
            sen = re.sub(i, 'zero', sen)
        pattern = re.findall('([^郡町村都道府県市\s]{1,3}市)?([^郡町村都道府県市\s]{1,3}郡)?([^郡町村都道府県市\s]{1,3}町)?([^郡町村都道府県市\s]{1,3}村)?([^郡町村都道府県市\s]{1,3}都)?([^郡町村都道府県市\s]{1,3}道)?([^郡町村都道府県市\s]{1,3}府)?([^郡町村都道府県市\s]{1,3}県)?', sen)
        for s1, s2, s3, s4, s5, s6, s7, s8 in pattern:
            if s1 != '':
                self.address.append(s1)
            if s2 != '':
                self.address.append(s2)
            if s3 != '':
                self.address.append(s3)
            if s4 != '':
                self.address.append(s4)
            if s5 != '':
                self.address.append(s5)
            if s6 != '':
                self.address.append(s6)
            if s7 != '':
                self.address.append(s7)
            if s8 != '':
                self.address.append(s8)
        money_pat = re.findall('[〇一二三四五六七八九十千百万億兆\s]+円|[〇一二三四五六七八九十千百万億兆\s]+ドル', sen)
        for i in money_pat:
            self.money.append(i)
        
        pat = re.findall('[〇一二三四五六七八九十\s]{1,2}丁目', sen)
        for i in pat:
            self.gpe_ent.append(i)
            
        pat = re.findall('八王子|九十九里町|本日|今日|一度|一致|二重|十分|一旦|一定|万全|一番', sen)
        for i in pat:
            self.ent.append(i)
        
        return sen
                

    def _normalize(self, arr, sen):
        for i in arr:
            sen = re.sub(self.jpn_number(i), i, sen)
        return sen
                
    def postprocess(self, txt):
        txt = self._normalize(self.address, txt)
        txt = self._normalize(self.gpe_ent, txt)
        txt = self._normalize(self.money, txt)
        txt = self._normalize(self.ent, txt)
        txt = re.sub('\s{0,1}ハイフン\s{0,1}', '-', txt)
        return txt
    
    def jpn_number(self, txt: str):
        result = japanese_numbers.to_arabic(txt)
        prev = 0
        sen = ''
        for j in range(len(result)):
            sen = sen + txt[prev:result[j].index] + str(result[j].number)
            prev = result[j].index + len(result[j].text)
        sen = sen + txt[prev:]
        
        pattern = re.findall('zero', sen)
        for i in pattern:
            sen = re.sub(i, '0', sen)
        
        pattern = re.findall(r'(?=([0-9]\s{0,1}の\s{0,1}[0-9]))', sen)
        for j in pattern:
            ans = '-'.join(j.split('の'))
            ans = re.sub(r'\s+', '', ans)
            sen = re.sub(j, ans, sen)
        return sen


    def word2time(self, txt: str):
        pattern = re.findall('([〇一二三四五六七八九十千\s]{1,3}時[\s]{0,1})(半)?([\s]{0,1}[〇一二三四五六七八九十千\s]{1,3}分)?', txt)
        for hrs, half, mins in pattern:
            
            if hrs != '' and half != '':
                txt = re.sub(hrs+half, self.jpn_number(hrs)+'半', txt)

            elif hrs != '' and mins != '':
                txt = re.sub(hrs+mins, self.jpn_number(hrs) + self.jpn_number(mins), txt)

            elif hrs != '':
                txt = re.sub(hrs, self.jpn_number(hrs), txt)

        return txt

    
    def word2date(self, txt: str):
        pattern = re.findall('([〇一二三四五六七八九十千百\s]{1,12}年)?([の〇一二三四五六七八九十\s]{1,7}月)?([の〇一二三四五六七八九十\s]{1,7}日)?', txt)
        for year, month, _date in pattern:
            if _date != '' and month != '' and year != '':
                _date1 = ''.join(_date.split(' '))
                month1 = ''.join(month.split(' '))
                year1 = ''.join(year.split(' ')) 
                _date1 = _date1[1:] if _date1[0] == 'の' else _date1
                month1 = month1[1:] if month1[0] == 'の' else month1
                txt = re.sub(str(year)+str(month)+str(_date), ' ' + self.jpn_number(year1) + self.jpn_number(month1) + self.jpn_number(_date1), txt)
            elif _date != '' and month != '':
                _date1 = ''.join(_date.split(' '))
                month1 = ''.join(month.split(' '))
                _date1 = _date[1:] if _date[0] == 'の' else _date
                month1 = month[1:] if month[0] == 'の' else month
                txt = re.sub(str(month)+str(_date), ' ' + self.jpn_number(month1) + self.jpn_number(_date1), txt)
            elif _date != '':
                _date1 = ''.join(_date.split(' '))
                _date1 = _date[1:] if _date[0] == 'の' else _date
                txt = re.sub(_date, ' ' + self.jpn_number(_date1), txt)
            elif month != '':
                month1 = ''.join(month.split(' '))
                month1 = month[1:] if month[0] == 'の' else month
                txt = re.sub(month, ' ' + self.jpn_number(month1), txt)
                
        
        return txt