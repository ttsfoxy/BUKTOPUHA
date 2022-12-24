import sqlite3
import time
from multiprocessing.connection import wait
from random import randint

import telebot
import logging
import traceback
# 5104204084:AAEzwLaQuneEajh2Ez-yPPBXCEf-yqtCGKY викторина

import settings

glob_answer = ''
glob_rest_error = False
glob_num_q = 0            # текущий номер вопроса
glob_answer_z = ''        # текущий ответ в *
quest_len = 127580
temp_listed = [0]         # времянка для ответа
# glob_quest_num=[]       # список с вопросами
i = [0]
rest = False              # рестарт
glob_save_to_second = 0


def victopuha(message, sw):

    global glob_id_victop   # id чата викторины
    global glob_num_q       # номер вопроса
    global glob_answer_z    # ответ в *
    global rest             # остановка и рестарт
    global glob_answer_yes  # проверка на повторный правильный ответ
    global glob_save_to_second
    global glob_wait
    global glob_answer
    if glob_wait is True:
        return

    if sw == 's':                             # запуск викторины
        glob_answer_yes = False               # на всякий случай ставим что никто не ответил правильно еще
        if gqn_count(message.chat.id) >= quest_len:    # если все вопросы прошли, то чистим список вопросов и начинаем заново
            gqn_clear(message.chat.id, False)

        glob_num_q = randint(0, quest_len)
        while gqn(message.chat.id, glob_num_q) is False:     # если вопрос уже был повторяем рандом пока не выпадет тот что еще не был
            glob_num_q = randint(0, quest_len)

        question, answer = get_question(glob_num_q)
        bot.send_message(message.chat.id, question)                     # задаем вопрос

        tmp_str = answer                                                 # правильный ответ
        glob_answer = answer
        glob_answer_z = ''
        for x in range(0, len(tmp_str)):                                # форматируем его *ми
            glob_answer_z = glob_answer_z+'*'
        bot.send_message(message.chat.id, glob_answer_z+' ' +
                         str(len(tmp_str))+' букв и '+whats_words(tmp_str))  # шлем * и количество буков
        time.sleep(5)
##############
        while i[0] != (len(glob_answer_z)-1):                             # пока не кончатся буквы или не получим ответ()
            if rest is True:                                              # если рестарт то ждем и выходим
                # time.sleep(1)
                rest = False
                i[0] = 0
                                                                        # понемногу открываем буквы из за *
                # return 
                break        
            if len(glob_answer_z) < 1:                                    # проверка на баг с сброшенным ответом
                logging.error(' у меня ошибка c glob_answer_z 1')     
                stop_vi(message)
                start_vi(message)
            
            if i[0]==0:
                x=0                                                     # понемногу открываем буквы из за *
                lst = list(glob_answer_z)
                tmpx=glob_answer
                lst[x] = tmpx[x]
                glob_answer_z = ''.join(lst)
                bot.send_message(glob_id_victop,glob_answer_z)
                i[0]=i[0]+1

                if rest==True:           # при рест выходим тк гдето глобальый рестарт        
                    # time.sleep(1)
                    rest=False  
                    i[0]=0
                    break
                time.sleep(10)
                if rest==True:           # при рест выходим тк гдето глобальый рестарт        
                    # time.sleep(1)
                    rest=False  
                    i[0]=0    
                    break       

            elif i[0]!=0:        
                if rest==True:
                    rest=False  
                    i[0]=0
                    break
                if len(glob_answer_z)<1:
                    logging.error(' у меня ошибка c glob_answer_z 2')     
                    stop_vi(message)   
                    start_vi(message)       
                x=randint(0,len(glob_answer_z)-1)
                while x in temp_listed:
                    x=randint(0,len(glob_answer_z)-1)
                temp_listed.append(x)    
                i[0]=i[0]+1

                lst = list(glob_answer_z)
                tmpx=glob_answer
                lst[x] = tmpx[x]
                glob_answer_z = ''.join(lst)

                bot.send_message(glob_id_victop,glob_answer_z)
                time.sleep(10)
        else:
            if rest==True:
                time.sleep(1)
                rest=False   
                i[0]=0                                                               # понемногу открываем буквы из за *
                return
            bot.send_message(glob_id_victop,'это '+glob_answer+
                            ' Вы не угадали! Bот следующий вопрос')
            i[0]=0
            temp_listed.clear()
            temp_listed.append(0)
            victopuha(message,'s')
            
            #############


        # return
    if sw=='w':                                 # вариант при правильном ответе
        if message.text.lower()==(glob_answer).lower():
            rest=True                           #останавливаем цикл повтора
            if glob_answer_yes==True:           #если ктото ответил уже правильно
                time.sleep(2)
                rest=False                                                  ######################
                return
            glob_answer_yes=True     
            
            ret_name,ret_num=statgame(message)          #статистика и окончание к очкам
            d=ret_num%10
            h=ret_num%100      #################
            if d==1 and h!=11:
                s=""
            elif 1<d<5 and not 11<h<15:
                s="а"
            else:
                s="ов"
            if ret_num%1000==0:
                bot.send_message(glob_id_victop,'\u2B50')#############
                bot.send_message(glob_id_victop,'@'+ret_name+' Поздравляю с '
                                 +str(ret_num)+' очков')
            else:
                bot.send_message(glob_id_victop,'Правильно! '+glob_answer+
                                ' У '+ret_name+' '+str(ret_num)+' очк'+s)
            time.sleep(5)
            i[0]=0
            temp_listed.clear()
            temp_listed.append(0)
            glob_num_q=0
            glob_answer_z=''
            victopuha(message,'s')

def get_achieves(message): # вывод ачивок
    bot.send_message(message.chat.id,'GodSkeptic \u2B50 \u2B50 \u2B50 - первым \
                    взял 1000 очков \nA P \u2B50 \u2B50 - вторым взял 1000 очков')
    
def read_updates(message):
    global glob_wait
    # glob_wait=True
  
    with open(updates_txt, 'r',encoding="utf-8") as filehandle:
        for line in filehandle:
            upd=filehandle.read()

    ress=bot.send_message(message.chat.id,upd)
    # glob_wait=False
    if message.from_user.id!=1675780013:
        time.sleep(60)
        bot.delete_message(message.chat.id,ress.message_id)

def whats_words(tmp_str):               # функция сколько слов в ответе
    tmm_lst=[]
    tmm_lst.extend(tmp_str.split(' '))    
    ret=len(tmm_lst)
    tmm_lst.clear
    if ret==1:
        return(str(ret)+ ' слово')
    elif ret < 5:
        return(str(ret)+ ' слова')
    elif ret >= 5: 
        return(str(ret)+ ' слов')
    

def stop_vi(message):                   #остановка викторины
    logging.info('Stopped')
    global rest 
    global glob_started
    global glob_num_q   
    global glob_answer_z     

    if glob_started==False:
        bot.send_message(message.chat.id,'BUkTOPUHA не запущена')    
        return  

    rest=True                              
    glob_started=False
    glob_num_q=0
    glob_answer_z=''
    temp_listed[0]=0
    i[0]=0
    
    bot.send_message(message.chat.id,'BUkTOPUHA ended, wait 9 sec')
    time.sleep(9)
    rest=False
    bot.send_message(message.chat.id,'BUkTOPUHA stopped')

def start_vi(message):
    
    global glob_id_victop
    global glob_started
    if glob_started==True:
        bot.send_message(message.chat.id,'BUkTOPUHA уже запущена')
        logging.info('BUkTOPUHA уже запущена')
        return
    else:
        logging.info('Started')
        bot.send_message(message.chat.id,'BUkTOPUHA started')   
        glob_started=True
        readuserstats()
        glob_id_victop=message.chat.id
        victopuha(message,'s')

def get_name(message):
    if message.from_user.username==None:
        if message.from_user.first_name==None:
            if message.from_user.last_name==None:
                username=message.from_user.id
            else:
                username=message.from_user.last_name
        else:
            username= message.from_user.first_name
    
    else:
        username=message.from_user.username
    return(username) 

def writeuserstats(fle):   # функция записи базы с количеством сообщений
    global glob_wait
    glob_wait=True
    if not userstats:
        logging.error('список Userstats пуст')
        return
    f = open(fle, 'w')
    for item in userstats:
        s = str(item) # # 2.2.1. Сформировать строку вида key:valueвзять ключ как строку
        s += ':' # добавить символ ':'
        s += str(userstats.get(item)) # добавить значение value по его ключу
        s += '\n' # добавить символ новой строки
        f.write(s)
    f.close()
    glob_wait=False

def readuserstats():     # функция чтения забы с количеством сообщений
    global glob_wait
    glob_wait=True
    f = open(stat_txt, 'rt')

    for lines in f: # Использовать итератор файла
        strings = lines.split(':')
        # 3.3.2. Получить ключ и значение
        key = strings[0] # получить ключ
        value = int(strings[1].rstrip()) # получить значение без '\n'
        # 3.3.3. Добавить пару key:value к словарю D2
        userstats[key] = value
    f.close()
    glob_wait=False
    
def takestats(chat_id,test):     # сортировка топ 10 и вывод  топ 10
    send_str=''
    conn=connectsql()
    q="SELECT name,points,achives FROM '{name}' order BY points DESC"    # в
    info=conn.execute(q.format(name=str(chat_id)))
    ret=info.fetchall()
    for x in range (0,10):
        send_str=f'{send_str}{str(x+1)}: {ret[x][0]} - {ret[x][1]}  {ret[x][2]}\n'
    conn.close()
    if test==True:
        return(send_str)
    bot.send_message(chat_id,send_str)
    

userstats={}

def statgame(message):                              #возврат количества очков пользователю и добавление его в базу если его там нет
    if message.from_user.username==None:
        if message.from_user.first_name==None:
            if message.from_user.last_name==None:
                username=message.from_user.id
            else:
                username=message.from_user.last_name
        else:
            username= message.from_user.first_name
    
    else:
        username=message.from_user.username
    conn=connectsql()
    q="SELECT * FROM '{name}'where id={id}"    # проверяем есть ли этот пользователь
    info=conn.execute(q.format(name=str(message.chat.id),id=message.from_user.id))

    if info.fetchone() is None:
        temp_create(message,username)       # если его нет в базе то добавляем его и мигрируем его очки в базу
        conn.execute(q.format(name=str(message.chat.id),id=message.from_user.id))
        6
    else:                       # если есть то увеличиваем значение очков на 1
        q="UPDATE '{name}' SET points=points + 1 where id={id}"
        conn.execute(q.format(name=str(message.chat.id),id=message.from_user.id))
        conn.commit()
    q="SELECT * FROM '{name}'where id={id}"         #возвращаем количество очков
    info=conn.execute(q.format(name=str(message.chat.id),id=message.from_user.id))
    records = info.fetchone()  
    conn.close()
    return(records[1],records[2])

def temp_create(message,named):##########
    conn=connectsql()
    tmp=message.from_user.id
    if named in userstats:
        points=userstats[named]
    else:
        points=1
    entit=tmp,named,points,''
    namechatid=str(message.chat.id)
    # q='INSERT INTO "{name}"(id,name,points,achives) V'
    q='INSERT or REPLACE INTO "{name}"(id,name,points,achives) values(?,?,?,?);'
    conn.execute(q.format(name=namechatid),entit)
    conn.commit()
    conn.close()

def connectsql():                # коннект к базе 
    conn_to_base=sqlite3.connect(database_db)
    return(conn_to_base)

def get_question(glob_num_q):    #получение вопроса из базы по его номеру

    conn=connectsql()
    info=conn.execute("SELECT * FROM questions where number=?",(glob_num_q,))
      
    records = info.fetchone()  
    question=records[1]
    answer=records[2]
    conn.close()
    return(question,answer)
   

def gqn(chat_id,number_q):
    conn=connectsql()
    info=conn.execute("SELECT * FROM gqn where q_num=? AND id_chat=?",(number_q,chat_id,))
    if info.fetchone() is None:  # если нет в базе повторов этого вопроса
        conn.execute("INSERT INTO gqn(id_chat,q_num) values(?,?)",(chat_id,number_q))
        conn.commit()
        conn.close()
        return(True)
    else:
        conn.close()
        return(False)

def gqn_count(id_chat):
    conn=connectsql()
    info=conn.execute("select Count() from gqn where id_chat=?",(id_chat,))
    cnt=info.fetchone()[0]
    conn.close()
    return(cnt)


def gqn_clear(id_chat,test):
    logging.info('запуск GQN_clear')
    conn=connectsql()
    conn.execute("DELETE  from gqn where id_chat=?",(id_chat,))
    conn.commit()
    conn.close()
    if test==True:
        return
    bot.send_message(id_chat,'Все вопросы прошли, рестартуем вопросы')

def createbase(message):
    # try:
    conn_to_base=connectsql()
    
    id_table_str=str(message.chat.id)

    print(id_table_str) 
    q="CREATE TABLE if not exists '{name}'(id integer PRIMARY KEY, name text, points integer, achives text)"   
    conn_to_base.execute(q.format(name=id_table_str))  #
    print('1')
    conn_to_base.commit()
    print('2')
    conn_to_base.close()



def connectsql():
    conn_to_base=sqlite3.connect(database_db)
    return(conn_to_base)



                                        # Start here
#################################################################################################################
#################################################################################################################
# уровни логирования
if __name__=='__main__':
    logging.basicConfig(level=logging.INFO,filename = victlog_log,format = 
                        "%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s")        

    glob_wait=False
    glob_id_victop=''
    glob_started=False
    glob_answer_yes=False
    bot = telebot.TeleBot(id_bot)
    @bot.message_handler(content_types=['text'])   # test
    def get_text_messages(message):

            # hellos(message)
            try:
                global glob_id_victop
                global glob_wait            # функция пропуска старых сообщений
                global rest
                global glob_started
                global glob_num_q
                global glob_answer_z
                global glob_answer_yes
                global glob_rest_error

                if glob_rest_error==True:
                    glob_rest_error=False
                    stop_vi(message)
                    start_vi(message)

                if glob_wait==True:
                    return

                if (message.text=='/migrate') and message.chat.id==-1001643971103 and message.from_user.username=='Titsfoxy':   
                    return;
                if (message.text=='/stop_vi' or message.text=='/stop_vi@tfbuktopuha_bot')  \
                    and message.chat.id==-1001643971103 and message.from_user.username=='Titsfoxy':   
                    stop_vi(message)
                    return
                if (message.text=='/start_vi' or message.text=='/start_vi@tfbuktopuha_bot' \
                    or message.text=='start_vi') and message.chat.id==-1001643971103 and message.from_user.username=='Titsfoxy':
                    start_vi(message)
                if (message.text=='/takest'or message.text=='/takest@tfbuktopuha_bot')and message.chat.id==-1001643971103:
                    takestats(message.chat.id,False)

                if message.text=='/get_updates' or message.text=='/get_updates@tfbuktopuha_bot':
                    read_updates(message)
                if message.text=='/achieves' or message.text=='/achieves@tfbuktopuha_bot':
                    get_achieves(message)
                if glob_answer_yes==True and message.text.lower()==glob_answer:           #если 2 правильных ответа
                    rtt=bot.send_message(message.chat.id,'@'+get_name(message)+' неуспель')
                    time.sleep(10)
                    bot.delete_message(message.chat.id,rtt.message_id)
                if message.chat.id==glob_id_victop:
                    victopuha(message,'w')

                
            except Exception as e:
                rest=True
                logging.error('у меня ошибка внутренняя'+ str(traceback.format_exc()))
                logging.info('stopped by error')
                stop_vi(message)
                start_vi(message)
                

    while True:
        try:
            
            bot.polling(none_stop=True, interval=1)
            # Предполагаю, что бот может мирно завершить работу, поэтому
            # даем выйти из цикла
            break
        except Exception as e:
            rest=True
            logging.error('у меня ошибка внешнняя'+ str(traceback.format_exc()))
            logging.info('stopped by error')
            bot.stop_polling()        
            glob_rest_error=True
            time.sleep(5)

        
# bot.polling(none_stop=True, interval=0)