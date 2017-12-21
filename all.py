import urllib.request 
import re

from flask import Flask, request, render_template
import json
import os
import codecs
-------------------------------------------------------------------------------------------------------
def pogoda(): #функция, выгруж погоду с сайта https://yandex.ru/pogoda/skopje
    req = urllib.request.Request('https://yandex.ru/pogoda/skopje')
    with urllib.request.urlopen(req) as response:
           html = response.read().decode('utf-8')
    regTemp = re.compile('<div class="temp fact__temp"><span class="temp__value">.*?<dd class="term__value"></dd></dl></div></div>', re.DOTALL)
    temp = regTemp.search(html).group(0) 
    temp = temp.replace('<a class="link fact__basic" href="/pogoda/skopje/details#18">', '')    
    return temp

def create_dict(): #функция для создания словаря из файла dictionary.txt, 
                    #который содер все слова с http://www.dorev.ru/ru-index.html
    dict_ = {}
    f = open('dictionary.txt', 'r')
    lin = f.readlines()
    f.close()
    len(lin)
    for i in lin:
        i = i.lower()
        i= i.split()

        if len(i[0]) == 2 and (len(i) > 2):
            wrd = i[2].replace("'", '')
            wrd = wrd.replace('?','ѣ')
            wrd = wrd.replace(',','')
            if  len(wrd)< (len(i[1]) + 2)  and (len(wrd) >= len(i[1])) and len(i[1]) > 1: dict_[i[1]] = wrd
        else:
            wrd = i[1].replace("'", '')
            wrd = wrd.replace('?','ѣ')
            wrd = wrd.replace(',','')
            if len(wrd) < (len(i[0]) + 2)  and (len(wrd) >= len(i[0])) and len(i[1]) > 1: dict_[i[0]] = wrd
    return dict_

dictionary = create_dict()

del_keys = ['за', 'что', 'по']
for i in del_keys :
    dictionary.pop(i)
    
    def mystem_word(word): #функция создающая файл размеченные при помощи mysterm   и возвращающая обработанные слово
    f = codecs.open('word.txt', 'w', 'utf-8')#открываем файл для записи в кодировке utf-8 ()
    f.write(word)
    f.close()   
    
    os.system('E:\\mystem.exe  -nig ' + 'word.txt' + ' res.txt')
    
    f = codecs.open('res.txt' , 'r','utf-8' )
    mysterm_words = f.read()
    f.close()
    
    return mysterm_words

def nf_word(word): #вытаскивает начальную форму слова из строчки получ., с помощью mystem_word
    regTemp = re.compile('{.*?[?|=]', re.DOTALL)
    temp = regTemp.search(word).group(0)
    
    wrd = re.sub('[=|?|{]','', temp)
    
    
    regTemp1 = re.compile('.*?{', re.DOTALL)
    temp1 = regTemp1.search(word).group(0)
    
    wrd1 = re.sub('{','', temp1)
    return wrd, wrd1
    
    
    def translit_word(word, dictionary): #транслитерация слова word
    try:
        word1 = nf_word(mystem_word(word))[0] #приведения слова к нормальной форме
        word = dictionary[word1]           
        warning = word + ' (из словаря ' + 'н.ф.  ' + word1 +')' 
    except:
        warning = 'слово было  не найдено в словаре'
        
    return (word, warning)

def chek_answ(dict_):#функция подсчитывающая  кол-во правильных ответов в тесте
    true = 0
    for i in dict_:
        if dict_[i] == 'true': true += 1
    print(true)
    return true
def freq_words(words): #словарь частот слов
    f_wrd = {}
    for i in words:
        try:
            f_wrd[i] = f_wrd[i] + 1
        except:
            f_wrd[i] = 1
    return f_wrd

def freq_10(f_wrds):#10 самых часто встречающихся слов
    wrds = sorted(f_wrds, key=lambda x: int(f_wrds[x]), reverse=True)
    wrds = wrds[:10]
    return ' '.join(wrds)

def mystem_word_html(words): #функция создающая файл размеченный при помощи mysterm   и возвращающая обработанные слова
    f = codecs.open('word.txt', 'w', 'utf-8')#открываем файл для записи в кодировке utf-8 ()
    f.write(' '.join(words.keys()))
    f.close()   
    
    os.system('E:\\mystem.exe  -nig ' + 'word.txt' + ' res.txt')
    
    f = codecs.open('res.txt' , 'r','utf-8' )
    mysterm_words = f.readlines()
    f.close()
    
    return mysterm_words
    
    
    def translit_words(f_wrds):#трансит всех слов с html страницы
    t_wrd = {}
    mystem_lines = mystem_word_html(f_wrds)
    for line in mystem_lines:
        nf_wrd = nf_word(line)
        try:
            t_wrd[nf_wrd[1]] = dictionary[nf_wrd[0]] 
        except:
            t_wrd[nf_wrd[1]] = nf_wrd[1]
    return t_wrd
    
    
    ---------------------------------------------------------------------------------------------------------------------------
    app = Flask(__name__)

from flask import url_for

@app.route('/') #главная страница
def index(): 
    f = open('index_.html','r')
    html = f.read()
    html = html.replace('.погода.', pogoda() )
    f.close()
    return html

@app.route('/index_res') #ответ на запрос транслитерации слова
def index_res(): 
    word_ = request.args
    f = open('index_res.html','r')
    html = f.read()
    html = html.replace('.запрос.', word_['word'])
    html = html.replace('.ответ.', translit_word(word_['word'],dictionary)[1])
    html = html.replace('.погода.', pogoda())    
    f.close()
    return html


@app.route('/test')#тест
def test(): 
    return render_template('test.html')

@app.route('/test_res')#ответ на тест
def test_res(): 
    true_answ = chek_answ(request.args)
    return render_template('test_res.html', true_answ = true_answ,  progr = str(int(true_answ)/10 * 100))

@app.route('/lenta')#страчичка с сайта
def lenta(): 
    req = urllib.request.Request('https://lenta.ru/')
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
    html = html.lower()
    

    regWord = re.compile('[а-я]+', re.DOTALL)
    html_words = regWord.findall(html)

    f_words = freq_words(html_words) 
    t_words = translit_words(f_words)
    
    for i in sorted(t_words, key = len, reverse=True):
        html = re.sub(i, t_words[i], html);
    
    html = '<!DOCTYPE html><html><head><title> 10 самых частотных слов: ' + freq_10(f_words) + html[len('<!DOCTYPE html><html><head><title>lenta.ru'):]
    #самые частотные слова выводятся при наведении на закладку страницы (название страницы)
    return html

if __name__ == '__main__':
    app.run()
