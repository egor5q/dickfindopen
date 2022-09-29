import os
import telebot
import time
import random
import threading
from emoji import emojize
from telebot import types
from pymongo import MongoClient
import traceback
import config


token = ""
bot = telebot.TeleBot(token, num_threads = 50)

mongo_client = MongoClient(os.environ['database'])
db = mongo_client.dickfind
users = db.users
chats = db.chats

polls={}
number=0

try:
    users.find_one({'id':441399484})['duelwin']
except:
    users.update_many({},{'$set':{'duelwin':0, 'duelloose':0, 'draw':0}})

symbols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'g', 'k', 'l', 'm', '1', '0', '9', '8', '6', '5', '4', '3', 'u', 'o', 'x', 'q', 'r', 's', 't', 'u', 'v', 'w', 'y', 'z']

dickcodes = []
emptycodes = []
golddickcodes = []

duels = {}

def randomgen():
    l = 10
    text = ''
    while len(text) < l:
        x = random.choice(symbols)
        if random.randint(1, 2) == 1:
            x = x.upper()
        text += x
    
    while text in dickcodes or text in emptycodes or text in golddickcodes:
        text = ''
        while len(text) < l:
            x = random.choice(symbols)
            if random.randint(1, 2) == 1:
                x = x.upper()
            text += x
    return text

while len(dickcodes) < 100:
    key = randomgen()
    dickcodes.append(key)
    
while len(emptycodes) < 100:
    key = randomgen()
    emptycodes.append(key)
    
while len(golddickcodes) < 100:
    key = randomgen()
    golddickcodes.append(key)


try:
    pass

except Exception as e:
    print('Ошибка:\n', traceback.format_exc())
    bot.send_message(441399484, traceback.format_exc())

def medit(message_text,chat_id, message_id,reply_markup=None,parse_mode=None):
    return bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=message_text,reply_markup=reply_markup,
                                 parse_mode=parse_mode)   

def createduelplayer(user):
    return {
        'id':user.id,
        'score':0,
        'name':user.first_name
    }

def createduel(m, limit=3):
    global number
    player = createduelplayer(m.from_user)
    a = {
        'players':{player['id']:player
        },
        'id':m.chat.id,
        'scorelimit':limit,
        'number':number,
        'started':False,
        'turnresults':{},
        'kb':None,
        'dicks':[],
        'golddicks':[],
        'msgid':None,
        'turn':1
    }
           
    number += 1
    return a

        
@bot.message_handler(func = lambda m: time.time() - m.date >= 120)
def skipp(m):
    return

@bot.message_handler(commands = ['testusers'])
def testusersss(m):
  try:
    if m.from_user.id != 441399484:
        return
    bot.send_message(m.chat.id, 'Проверяю')
    us = 0
    ch = 0
    for ids in users.find({}):
        try:
            bot.send_chat_action(ids['id'], 'typing')
            us += 1
        except:
            pass
    for ids in chats.find({}):
        try:
            bot.send_chat_action(ids['id'], 'typing')
            ch += 1
        except:
            pass
    bot.send_message(441399484, 'Пользователи: '+str(us)+'\nЧаты: '+str(ch))
  except:
    pass

@bot.message_handler(commands=['testreklama'])
def testrekkk(m):
    if m.from_user.id != 441399484:
        return
    try:
        bot.forward_message(chat_id = 441399484, from_chat_id = m.chat.id, message_id = m.reply_to_message.message_id)
    except:
        print(traceback.format_exc())
        
@bot.message_handler(commands=['reklama'])
def testrekkkrrr(m):
    if m.from_user.id != 441399484:
        return
    i = 0
    for ids in chats.find({}):
        try:
            bot.forward_message(chat_id = ids['id'], from_chat_id = m.chat.id, message_id = m.reply_to_message.message_id)
            i+=1
            if i%1000 == 0:
                try:
                    bot.send_message(441399484, 'Сообщение получило '+str(i)+' чатов!')
                except:
                    pass
        except:
            pass
    try:
        bot.send_message(441399484, 'Сообщение получило '+str(i)+' чатов!')
    except:
        pass

@bot.message_handler(commands=['sendm'])
def pinsendg(m):
    #config.about(m, bot)
    if m.from_user.id == 441399484:
        i = 0
        for ids in chats.find({}):
            try:
                time.sleep(0.1)
                bot.send_message(ids['id'], m.text.split('/sendm ')[1])
                i+=1
                if i%100 == 0:
                    try:
                        bot.send_message(441399484, str(i)+' чатов получили сообщение!')
                    except:
                        pass
            except:
                pass
        bot.send_message(441399484, str(i)+' чатов получили сообщение!')
    
@bot.message_handler(commands=['duel'])
def duelll(m):
  try:
    try:
        limit = int(m.text.split()[1])
    except:
        limit = 3
    d = createduel(m, limit)

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(text = 'Принять вызов', callback_data = 'startduel?'+str(d['number'])))
    msg = bot.send_message(m.chat.id, m.from_user.first_name+' хочет сразиться в поиске писюна! Лимит по очкам: '+str(limit)+'. Кто готов принять вызов?', reply_markup = kb)
    d['msgid'] = msg.message_id
    duels.update({d['number']:d})
  except:
    pass
    
    
@bot.callback_query_handler(func = lambda call: call.data[:9] == 'startduel')
def duells(call):
    try:
        duel = duels[int(call.data.split('?')[1])]
    except:
        print(traceback.format_exc())
        print(duels)
        return
    if duel['started']:
        bot.answer_callback_query(call.id, 'Дуэль уже началась! Присоединиться уже нельзя!')
        return
    if call.from_user.id in duel['players']:
        bot.answer_callback_query(call.id, 'Вы уже в дуэли!')
        return
    player = createduelplayer(call.from_user)
    duel['players'].update({player['id']:player})
    duel['started'] = True
    text = dueledit(duel)
    
    kb, dicks, golddicks = getdickkb(duel)
    
    duel['kb'] = kb
    duel['dicks'] = dicks
    duel['golddicks'] = golddicks
    
    medit(text, call.message.chat.id, call.message.message_id, reply_markup = kb)
    
    
@bot.callback_query_handler(func = lambda call: call.data[:4] == 'duel')
def duellss(call):
    time.sleep(random.randint(1, 10)/100)
    try:
        duel = duels[int(call.data.split('?')[2])]
    except:
        return
    
    if call.from_user.id not in duel['players']:
        bot.answer_callback_query(call.id, 'Вы не участвуете в дуэли!')
        return
    player = duel['players'][call.from_user.id]
    if call.from_user.id in duel['turnresults']:
        bot.answer_callback_query(call.id, 'Вы уже походили!')
        return
    dick = call.data.split('?')[1]
    d = False
    gd = False
    emp = False
    if dick in dickcodes:
        d = True
    elif dick in golddickcodes:
        gd = True
    else:
        emp = True
    
    if d:
        text = '🍆|Ура! Вы выбрали ящик с членом!'
        text2 = player['name']+': 🍆нашёл(ла) член\n'
           
        x = 'penis'          
        result = 'found'
    elif gd:
        text = '🍌|Ура! Вы нашли золотой пенис!'
        text2 = player['name']+': 🍌нашёл(ла) ЗОЛОТОЙ член!\n'
        
        x = 'goldpenis'
        player['score'] += 9
        result = 'found'
    else:
        text = '💨|О нет! Вы выбрали ящик без члена!'
        text2 = player['name']+': 💨открыл(а) пустую коробку\n'
        
        x = 'null'
        result = 'notfound'
    bot.answer_callback_query(call.id, text, show_alert = True)
    users.update_one({'id':player['id']},{'$inc':{x:1}})
    
    duel['turnresults'].update({player['id']:{'text':text2, 'result':result}})
    #medit(dueledit(duel), call.message.chat.id, call.message.message_id, reply_markup = duel['kb'])
    if len(duel['turnresults']) >= len(duel['players']):
        time.sleep(2)
        nextduelturn(duel)
        
def nextduelturn(duel):
    notscore = True
    for ids in duel['turnresults']:
        if duel['turnresults'][ids]['result'] == 'notfound':
            notscore = False
            
    if not notscore:
        for ids in duel['turnresults']:
            if duel['turnresults'][ids]['result'] == 'found':
                duel['players'][ids]['score'] += 1
    
    end = False
    for ids in duel['players']:
        player = duel['players'][ids]
        if player['score'] >= duel['scorelimit']:
            end = True
    kb2=types.InlineKeyboardMarkup()
    buttons1=[]
    buttons2=[]
    buttons3=[]
    i=1
    while i<=9:
        if i in duel['dicks']:
            emoj='🍆'
            if i in duel['golddicks']:
                emoj='🍌'
        else:
            emoj='💨'
        if i<=3:
            buttons1.append(types.InlineKeyboardButton(text=emoj, callback_data='xyi'))
        elif i<=6:
            buttons2.append(types.InlineKeyboardButton(text=emoj, callback_data='xyi'))
        elif i<=9:
            buttons3.append(types.InlineKeyboardButton(text=emoj, callback_data='xyi'))
        i+=1
    kb2.add(*buttons1)
    kb2.add(*buttons2)
    kb2.add(*buttons3)

    medit(dueledit(duel), duel['id'], duel['msgid'], reply_markup = kb2)
    time.sleep(5)
    duel['turn'] += 1
    duel['turnresults'] = {}
    
    if end:
        endduel(duel)
    else:
        kb, dicks, golddicks = getdickkb(duel)
        duel['kb'] = kb
        duel['dicks'] = dicks
        duel['golddicks'] = golddicks
        
        text = dueledit(duel)
    
        medit(text, duel['id'], duel['msgid'], reply_markup = kb)


def endduel(duel):
    kb2=types.InlineKeyboardMarkup()
    buttons1=[]
    buttons2=[]
    buttons3=[]
    i=1
    while i<=9:
        if i in duel['dicks']:
            emoj='🍆'
            if i in duel['golddicks']:
                emoj='🍌'
        else:
            emoj='💨'
        if i<=3:
            buttons1.append(types.InlineKeyboardButton(text=emoj, callback_data='xyi'))
        elif i<=6:
            buttons2.append(types.InlineKeyboardButton(text=emoj, callback_data='xyi'))
        elif i<=9:
            buttons3.append(types.InlineKeyboardButton(text=emoj, callback_data='xyi'))
        i+=1
    kb2.add(*buttons1)
    kb2.add(*buttons2)
    kb2.add(*buttons3)

    medit(dueledit(duel, endgame=True), duel['id'], duel['msgid'], reply_markup = kb2)
    try:
        del duels[duel['number']]
    except:
        pass
        
          
def dueledit(duel, endgame = False):
    text = 'Раунд '+str(duel['turn'])+':\n\n'
    for ids in duel['players']:
        player = duel['players'][ids]
        score = player['score']
        if str(score)[-1] in ['1']:
            t = 'очко'
        elif str(score)[-1] in ['2', '3', '4']:
            t = 'очка'
        elif str(score)[-1] in ['0', '5', '6', '7', '8', '9']:
            t = 'очков'
        text += player['name']+': '+str(player['score'])+'/'+str(duel['scorelimit'])+' '+t+'\n'
    text += '\n'
    if not endgame:
        for ids in duel['turnresults']:
            text += duel['turnresults'][ids]['text']
    else:
        winner = None
        players = []
        maxscore = -1000
        winner = None
        for ids in duel['players']:
            player = duel['players'][ids]
            if player['score'] > maxscore:
                maxscore = player['score']
                winner = player
            elif player['score'] == maxscore:
                winner = None
        if winner != None:     
            for ids in duel['players']:
                if duel['players'][ids]['id'] != winner['id']:
                    looser = duel['players'][ids]
            text += '🏆 И победитель этой дуэли - '+winner['name']+'! Поздравляем!'
            users.update_one({'id':winner['id']},{'$inc':{'duelwin':1}})
            users.update_one({'id':looser['id']},{'$inc':{'duelloose':1}})
        else:
            text += 'Ничья!'
            for ids in duel['players']:
                users.update_one({'id':duel['players'][ids]['id']},{'$inc':{'draw':1}})
        
    return text
    
    
def getdickkb(duel):
    kb=types.InlineKeyboardMarkup(row_width = 3)
    buttons1=[]
    buttons2=[]
    buttons3=[]
    amount=random.randint(1,8)
    i=0
    dicks=[]
    golddicks=[]
    while i<amount:
        x=random.randint(1,9)
        while x in dicks:
            x=random.randint(1,9)
        dicks.append(x)
        i+=1
    i=1
    while i<=9:
        if i in dicks:
            if random.randint(1,100)!=1:
                callb=random.choice(dickcodes)
            else:
                callb=random.choice(golddickcodes)
                golddicks.append(i)
        else:
            callb=random.choice(emptycodes)
        
        if i<=3:
            buttons1.append(types.InlineKeyboardButton(text='📦', callback_data='duel?'+callb+'?'+str(duel['number'])))
        elif i<=6:
            buttons2.append(types.InlineKeyboardButton(text='📦', callback_data='duel?'+callb+'?'+str(duel['number'])))
        elif i<=9:
            buttons3.append(types.InlineKeyboardButton(text='📦', callback_data='duel?'+callb+'?'+str(duel['number'])))
        i+=1
    kb.add(*buttons1)
    kb.add(*buttons2)
    kb.add(*buttons3)
    
    return kb, dicks, golddicks
    
@bot.message_handler(commands=['dick'])
def dd(m):
  try:
    #config.about(m, bot)
    if m.chat.id < 0:
        if chats.find_one({'id':m.chat.id}) == None:
            t = 1594395747
            chats.insert_one({
                'id':m.chat.id,
                'title':m.chat.title
            }
            )
            if time.time() - t <= 250400:
                bot.send_message(m.chat.id, 'У бота теперь есть статистика найденных членов - найти её можно по команде /dickstat!')
    count = 0
    for ids in polls:
        pol = polls[ids]
        if pol['chatid'] == m.chat.id:
            count += 1
    if count >= 10:
        bot.send_message(m.chat.id, 'Нельзя иметь больше, чем 10 активных игр в чате! Завершите предыдущие игры!')
        return
    global number
    text='Угадайте, в какой коробке хуй.'
    kb=types.InlineKeyboardMarkup(row_width = 3)
    buttons1=[]
    buttons2=[]
    buttons3=[]
    amount=random.randint(1,8)
    i=0
    dicks=[]
    golddicks=[]
    while i<amount:
        x=random.randint(1,9)
        while x in dicks:
            x=random.randint(1,9)
        dicks.append(x)
        i+=1
    i=1
    while i<=9:
        randoms=random.randint(1,10000000)
        if i in dicks:
            if random.randint(1,100)!=1:
                callb=random.choice(dickcodes)
            else:
                callb=random.choice(golddickcodes)
                golddicks.append(i)
        else:
            callb=random.choice(emptycodes)
        
        if i<=3:
            buttons1.append(types.InlineKeyboardButton(text='📦', callback_data=callb+' '+str(number)+' '+str(randoms)))
        elif i<=6:
            buttons2.append(types.InlineKeyboardButton(text='📦', callback_data=callb+' '+str(number)+' '+str(randoms)))
        elif i<=9:
            buttons3.append(types.InlineKeyboardButton(text='📦', callback_data=callb+' '+str(number)+' '+str(randoms)))
        i+=1
    kb.add(*buttons1)
    kb.add(*buttons2)
    kb.add(*buttons3)
    kb.add(types.InlineKeyboardButton(text='Окончить игру', callback_data='endgame '+str(number)))
    polls.update({number:{
        'users':{},
        'dicks':dicks,
        'kb':kb,
        'golddicks':golddicks,
        'chatid':m.chat.id
        
    }}
                )
    try:
        bot.send_message(m.chat.id, text, reply_markup=kb)
        number+=1
    except:
        pass
  except:
    pass


@bot.message_handler(commands=['dickstat'])
def dickstats(m):
  try:
    user = createuser(m.from_user)
    alls = user['penis']+user['goldpenis']+user['null']
    if alls > 0:
        penis = round((user['penis']/alls)*100, 2)
        goldpenis = round((user['goldpenis']/alls)*100, 2)
        null = round((user['null']/alls)*100, 2)
    else:
        penis = 0
        goldpenis = 0
        null = 0
    text = 'Статистика пользователя '+user['name']+':\n\n'
    try:
        for ids in user['statuses']:
            text += ids+'; '
        text = text[:len(text)-2]
        text += '.\n'
    except:
        pass
    text += 'Найдено членов: '+str(user['penis'])+'🍆 ('+str(penis)+'%)\n'
    text += 'Найдено ЗОЛОТЫХ членов: '+str(user['goldpenis'])+'🍌 ('+str(goldpenis)+'%)\n'
    text += 'Открыто пустых коробок: '+str(user['null'])+'💨 ('+str(null)+'%)\n\n'
    
    duelall = user['duelwin']+user['duelloose']+user['draw']
    if duelall > 0:
        duelwin = round((user['duelwin']/duelall)*100, 2)
        duelloose = round((user['duelloose']/duelall)*100, 2)
        draw = round((user['draw']/duelall)*100, 2)
    else:
        duelwin = 0
        duelloose = 0
        draw = 0
        
    text += 'Дуэли:\n'
    text += 'Победы: '+str(user['duelwin'])+' ('+str(duelwin)+'%)\n'
    text += 'Поражения: '+str(user['duelloose'])+' ('+str(duelloose)+'%)\n'
    text += 'Ничьи: '+str(user['draw'])+' ('+str(draw)+'%)\n'
    try:
        bot.send_message(m.chat.id, text, reply_to_message_id = m.message_id)
    except:
        pass
  except:
    pass
    
@bot.message_handler(commands=['set_status'])
def setstatusss(m):
    if m.from_user.id != 441399484:
        return
    try:
        try:
            users.find_one({'id':m.reply_to_message.from_user.id})['statuses']
            users.update_one({'id':m.reply_to_message.from_user.id},{'$push':{'statuses':m.text.split('/set_status ')[1]}})
            bot.send_message(m.chat.id, 'Успешно!')
        except:
            users.update_one({'id':m.reply_to_message.from_user.id},{'$set':{'statuses':[m.text.split('/set_status ')[1]]}})
            bot.send_message(m.chat.id, 'Успешно!')
    except:
        bot.send_message(m.chat.id, 'Ошибка!')
    
    
@bot.callback_query_handler(func=lambda call:True)
def inline(call):
  try:
    user2 = createuser(call.from_user)
    user=call.from_user
    try:
        game=polls[int(call.data.split(' ')[1])]
    except:
        game=None
    if game!=None:
        if user.id not in game['users'] and call.data!='xyi':
            golddick=False
            if call.data.split()[0] in dickcodes:
                dick=True
                text='🍆|Ура! Вы выбрали ящик с членом!'
                x = 'penis'
                bot.answer_callback_query(call.id, text, show_alert=True)
            elif call.data.split()[0] in golddickcodes:
                dick = True
                golddick=True
                text='🍌|Ура! Вы нашли золотой пенис!'
                x = 'goldpenis'
            else:
                dick=False
                bot.answer_callback_query(call.id, '💨|О нет! Вы выбрали ящик без члена!', show_alert=True)
                x = 'null'
            
            game['users'].update({user.id:{'name':call.from_user.first_name,
                                          'dick':dick,
                                          'golddick':golddick}})
            kb=types.InlineKeyboardMarkup(row_width = 3)
     
            medit(editmsg(game), call.message.chat.id, call.message.message_id, reply_markup=game['kb'])
            users.update_one({'id':user.id},{'$inc':{x:1}})
        
        elif 'endgame' not in call.data:
            bot.answer_callback_query(call.id, 'Вы уже походили!')
        
    if 'endgame' in call.data:
        kb2=types.InlineKeyboardMarkup(row_width = 3)
        buttons1=[]
        buttons2=[]
        buttons3=[]
        i=1
        while i<=9:
            if i in game['dicks']:
                emoj='🍆'
                if i in game['golddicks']:
                    emoj='🍌'
            else:
                emoj='💨'
            if i<=3:
                buttons1.append(types.InlineKeyboardButton(text=emoj, callback_data='xyi'))
            elif i<=6:
                buttons2.append(types.InlineKeyboardButton(text=emoj, callback_data='xyi'))
            elif i<=9:
                buttons3.append(types.InlineKeyboardButton(text=emoj, callback_data='xyi'))
            i+=1
        kb2.add(*buttons1)
        kb2.add(*buttons2)
        kb2.add(*buttons3)
        result=editmsg(game, True)
        medit('Игра окончена юзером '+call.from_user.first_name+'! Результаты:\n'+result, call.message.chat.id, call.message.message_id, reply_markup=kb2)
        try:
            del polls[int(call.data.split(' ')[1])]
        except:
            print(traceback.format_exc())

  except Exception as e:
    bot.send_message(441399484, traceback.format_exc())
    
def editmsg(game, end=False):
    if end==False:
        text='Угадайте, в какой коробке хуй.\n\n'
    else:
        text=''
    for ids in game['users']:
        if game['users'][ids]['golddick']==True:
            text+=game['users'][ids]['name']+': 🍌нашёл(ла) ЗОЛОТОЙ член!\n'
        
        elif game['users'][ids]['dick']==True:
            text+=game['users'][ids]['name']+': 🍆нашёл(ла) член\n'
        else:
            text+=game['users'][ids]['name']+': 💨открыл(а) пустую коробку\n'
    return text

def createuser(user):
    user2 = users.find_one({'id':user.id})
    if user2 == None:
        users.insert_one({
            'id':user.id,
            'name':user.first_name,
            'penis':0,
            'goldpenis':0,
            'null':0,
            'duelwin':0,
            'duelloose':0,
            'draw':0
        })
        user2 = users.find_one({'id':user.id})
    return user2

chatstocheck = []
