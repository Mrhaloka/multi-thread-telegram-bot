import threading
import re
import telegram
import mysql.connector
import requests
import time
from flask import Flask, request
app = Flask(__name__)
application = app
global bot
#bot token
bot = telegram.Bot(token='your bot token')
       
#route '/' 
@app.route('/',methods=['GET'])

def showmsg():
 
    return "Hello "
    
# route /hook for telegram webhook update
@app.route('/HOOK', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        #get user update msg and info
        update = telegram.Update.de_json(request.get_json(force=True))
        lastmsg=update.message.text
        chat_id = update.message.chat.id
        users_id=0
        #connect to the database
        mydb = mysql.connector.connect(
            host="",
            user="",
            passwd="",
            database=""
        )  
        mycursor = mydb.cursor()
        #status and user id
        sql = "SELECT * FROM users WHERE tele_id = %s"
        adr = (update.message.chat.id, )
        mycursor.execute(sql, adr)
        myres=mycursor.fetchall()
        if myres!=[]:
            status = myres[0][5]
            users_id = myres[0][0]
        else:
            status=0
        #mail username
        if users_id !=0:
            sql = "SELECT * FROM mails WHERE users_id = %s"
            adr = (users_id, )
            mycursor.execute(sql, adr)
            myres=mycursor.fetchall()
            if  myres!=[]:
               username =  myres[0][2]
        #when user say "/start"  
        if update.message.text=="/start" and status==0 :
            #check user was created or no
            
            sql = "SELECT * FROM users WHERE tele_id = %s"
            tele_id = (update.message.chat.id, )
            mycursor.execute(sql, tele_id)
            myresult = mycursor.fetchall()
            
            #if its a new users insert the users info in Db 
            if myresult==[] :
                sql = "INSERT INTO users (first_name, username ,tele_id,active) VALUES (%s, %s,%s,%s)"
                val = (update.message.chat.first_name, update.message.chat.username,update.message.chat.id,1)
                mycursor.execute(sql, val)
                mydb.commit()
                
    
            #keybord
            custom_keyboard =[['reset'],['']]
            reply_markup=telegram.ReplyKeyboardMarkup(custom_keyboard)
            #msg for start
            msgtext="wlc mssg"
            msgtext=msgtext.encode('utf-8')
            bot.sendMessage(chat_id=chat_id, text= msgtext,reply_markup=reply_markup)
            msgtext="enter you username"
            msgtext=msgtext.encode('utf-8')
            bot.sendMessage(chat_id=chat_id, text= msgtext,reply_markup=reply_markup)
            #end msg start
            #status 0------>1
            sql = "UPDATE users SET status = %s WHERE tele_id = %s"
            val = (1, update.message.chat.id)
            mycursor.execute(sql, val)
            mydb.commit()
            
            #end update DB
    #end "/start" if
    #status ------->1 user pass 
    if status==1 and lastmsg!="reset":
        
         #get mails of user info
        sql = "SELECT * FROM mails WHERE users_id = %s"
        tele_id = (users_id, )
        mycursor.execute(sql, tele_id)
        myresult = mycursor.fetchall()
          #if mail empty
        if myresult==[] :
            #save username
            sql = "INSERT INTO mails (users_id, username ) VALUES (%s,%s)"
            val = (users_id, update.message.text)
            mycursor.execute(sql, val)
            mydb.commit()
            #status=2 password
            sql = "UPDATE users SET status = %s WHERE id = %s"
            val = (2, users_id)
            mycursor.execute(sql, val)
            mydb.commit()
            
        else:
            sql = "UPDATE mails SET username = %s WHERE users_id = %s"
            val = (lastmsg, users_id)
            mycursor.execute(sql, val)
            mydb.commit()
            #status=2 password
            sql = "UPDATE users SET status = %s WHERE id = %s"
            val = (2, users_id)
            mycursor.execute(sql, val)
            mydb.commit()
        bot.sendMessage(chat_id=chat_id, text= "status 2 -> enter you pass ")        
            #status 2=======> password
    if status==2 and lastmsg!="reset":
        
          #get mails of user info
        sql = "SELECT * FROM mails WHERE users_id = %s"
        tele_id = (users_id, )
        mycursor.execute(sql, tele_id)
        myresult = mycursor.fetchall()
          #if mail empty
        if myresult==[] :
            #save password
            sql = "INSERT INTO mails (users_id, password ) VALUES (%s,%s)"
            val = (users_id, update.message.text)
            mycursor.execute(sql, val)
            mydb.commit()
            #status=3 password and user is here
            sql = "UPDATE users SET status = %s WHERE id = %s"
            val = (3, users_id)
            mycursor.execute(sql, val)
            mydb.commit()

          
        else:
            #update password
            sql = "UPDATE mails SET password = %s WHERE users_id = %s"
            val = (lastmsg, users_id)
            mycursor.execute(sql, val)
            mydb.commit()
            #status=3 password
            sql = "UPDATE users SET status = %s WHERE id = %s"
            val = (3, users_id)
            mycursor.execute(sql, val)
            mydb.commit()
        bot.sendMessage(chat_id=chat_id, text= "w8 for mail service response")    
        #check user and pass 
        password=lastmsg
        session=requests.Session()
        r=session.get('https://mail.ut.ac.ir/',timeout=5)
        #this site use csrf token we need it for login
        token_value_1=r.text.find('en" value="')+11
        token_value_2=r.text.find('">\n              <i')
        token=r.text[token_value_1:token_value_2]
        password=lastmsg
        login_data=dict(_user=username,_pass=password,_token=token,_url="",_action="login",_task= "login",_timezone="Asia/Tehran")
        r=session.post("https://mail.ut.ac.ir/?_task=login",data=login_data,timeout=5)
        r=session.get("https://mail.ut.ac.ir/?_task=mail&_action=list&_refresh=1&_mbox=INBOX&_remote=1&_unlock=",cookies=session.cookies.get_dict(),timeout=5)
        if r.text.count("Your session is invalid or expired") :
            #change status=1 and send msg your user or pass incorect
            sql = "UPDATE users SET status = %s WHERE id = %s"
            val = (1, users_id)
            mycursor.execute(sql, val)
            mydb.commit()
            bot.sendMessage(chat_id=chat_id, text="user or password incorrect ")
        else :
            #set the msgcount in Db and change status ->4 active->1
            msg_value_1=r.text.find('messagecount":')+14
            msg_value_2=r.text.find(',"pageco')
            msg_count=int(r.text[msg_value_1:msg_value_2])
            sql = "UPDATE users SET status = %s WHERE id = %s"
            val = (4, users_id)
            mycursor.execute(sql, val)
            mydb.commit()
            sql = "UPDATE mails SET active = %s , msg_count=%s WHERE users_id = %s"
            val = (1,msg_count, users_id)
            mycursor.execute(sql, val)
            mydb.commit()
                
            bot.sendMessage(chat_id=chat_id, text="تبریک میگم شما با موفقیت در بات ثبت نام کردید ایمیل های جدید شما توسط بات برای شما فرستاده خواهد شد ")

        
    #when users try for reset user and pass
    if lastmsg=="reset":
        sql = "UPDATE users SET status = %s WHERE id = %s"
        val = (1, users_id)
        mycursor.execute(sql, val)
        mydb.commit()
        status=1
        bot.sendMessage(chat_id=chat_id, text= "اطلاعات شما پاک شد لطفا دوباره یوزرنیم خود را وارد کنید ")
    mydb.close()  
    return 'ok'
#the mail processor
@app.route('/tele/mails/notif',methods=['GET'])
def mailnotif():
    class MyThread(threading.Thread):
        def __init__(self, username, password,msg,user_id):
            threading.Thread.__init__(self)
            self.username = username
            self.password = password
            self.msg = msg
            self.user_id=user_id
        def run(self):
            username=self.username
            password=self.password 
            msg=self.msg 
            user_id=self.user_id
            session=requests.Session()
            r=session.get('https://mail.ut.ac.ir/',timeout=5)
            token_value_1=r.text.find('en" value="')+11
            token_value_2=r.text.find('">\n              <i')
            token=r.text[token_value_1:token_value_2]
            login_data=dict(_user=username,_pass=password,_token=token,_url="",_action="login",_task= "login",_timezone="Asia/Tehran")
            r=session.post("https://mail.ut.ac.ir/?_task=login",data=login_data,timeout=5)
            r=session.get("https://mail.ut.ac.ir/?_task=mail&_action=list&_refresh=1&_mbox=INBOX&_remote=1&_unlock=",cookies=session.cookies.get_dict(),timeout=5)
            msg_value_1=r.text.find('add_message_row(')+16
            msg_value_2=r.text.find(',{\\"su')
            msg_count=r.text[msg_value_1:msg_value_2]
            msg_count=int(msg_count)
            if msg_count>msg:
                sql = "SELECT * FROM users WHERE id= %s"
                adr = (user_id, )
                mycursor2.execute(sql, adr)
                myres2=mycursor2.fetchall()
                text="you have"+str(msg_count-msg)+"  new msg "
                bot.sendMessage(chat_id=myres2[0][3],text=text)
                msg_loop=int(msg_count-msg)
                for i in range (0,msg_loop):
                    msg_count=int(msg_count)-i
                    msg_sub1=r.text.find("add_message_row("+str(msg_count)+',{\\"subject')+32+len(str(msg_count))
                    msg_sub2=r.text.find('fromto',msg_sub1-33)-5
                    
                    s=r.text[msg_sub1:msg_sub2]
                    #if u want make ut mail bot u need this 2 line for unicode
                    #s=eval("'%s'" % s)
                    #s=s.encode('utf-8').decode('unicode-escape')
                    bot.sendMessage(chat_id=myres2[0][3],text=s)
                    z=session.get("https://mail.ut.ac.ir/?_task=mail&_caps=pdf%3D1%2Cflash%3D0%2Ctiff%3D0%2Cwebp%3D1&_uid="+str(msg_count)+"&_mbox=INBOX&_framed=1&_action=preview",cookies=session.cookies.get_dict())
                    if z.text.find("ICSP")==-1:
                        msg_more1=z.text.find('class="message-htmlpart"')-5
                        msg_more2=z.text.find('<div id="attachmentmenu"')-1
                    else:
                        msg_more1=z.text.find('<td class="content">')+20
                        msg_more2=z.text.find('<div class="commands">')-1
                    msg_more=z.text[msg_more1:msg_more2]
                    cleanr = re.compile('<.*?>')
                    msg_more=cleantext = re.sub(cleanr, '', msg_more)
                    bot.sendMessage(chat_id=myres2[0][3],text="msg body :       "+msg_more)
                    msg_count=int(msg_count)+i
                sql = "UPDATE mails SET msg_count = %s WHERE username = %s"
                val = (msg+msg_loop, username)
                mycursor3.execute(sql, val)
                mydb.commit()
            
            
            
    #db connetor
    mydb = mysql.connector.connect(
            host="localhost",
            user="your user",
            passwd="your pass",
            database="your database"
        )  
    mycursor = mydb.cursor()
    mycursor2 = mydb.cursor()
    mycursor3 = mydb.cursor()
    sql = "SELECT * FROM mails WHERE active= %s"
    adr = (1, )
    mycursor.execute(sql, adr)
    #threads
    threadLock = threading.Lock()
    threads = []
    myres=mycursor.fetchall()
    for mail in myres:
        username=mail[2]
        password=mail[3]
        msg=mail[4]
        user_id=mail[1]   
        thread = MyThread(username,password,msg,user_id)
        thread.start()
        threads.append(thread)
    for t in threads:
        t.join()
        print ("Exiting Main Thread")
    mydb.close()     
        
    return  "ok "
#update DB when user changed password or deleted msg   
@app.route('/tele/user/check',methods=['GET'])
def updateusers():
    mydb = mysql.connector.connect(
            host="localhost",
            user="your user",
            passwd="your pass",
            database="your DB name"
        )  
    mycursor = mydb.cursor()
    mycursor2 = mydb.cursor()
    mycursor3 = mydb.cursor()
    sql = "SELECT * FROM mails WHERE active= %s"
    adr = (1, )
    mycursor.execute(sql, adr)
    myres=mycursor.fetchall()
    for mail in myres:
        username=mail[2]
        password=mail[3]
        user_id=mail[1]
        session=requests.Session()
        r=session.get('https://mail.ut.ac.ir/',timeout=5)
        token_value_1=r.text.find('en" value="')+11
        token_value_2=r.text.find('">\n              <i')
        token=r.text[token_value_1:token_value_2]
        login_data=dict(_user=username,_pass=password,_token=token,_url="",_action="login",_task= "login",_timezone="Asia/Tehran")
        r=session.post("https://mail.ut.ac.ir/?_task=login",data=login_data,timeout=5)
        r=session.get("https://mail.ut.ac.ir/?_task=mail&_action=list&_refresh=1&_mbox=INBOX&_remote=1&_unlock=",cookies=session.cookies.get_dict(),timeout=5)
        sql = "SELECT * FROM users WHERE id= %s"
        adr = (user_id, )
        mycursor3.execute(sql, adr)
        myres2=mycursor3.fetchall()
        if r.text.count("Your session is invalid or expired") :
            sql = "UPDATE users SET status = %s WHERE id = %s"
            val = (1, user_id)
            mycursor2.execute(sql, val)
            mydb.commit()
            sql = "UPDATE mails SET active = %s  WHERE users_id = %s"
            val = (0, user_id)
            mycursor2.execute(sql, val)
            bot.sendMessage(chat_id=myres2[0][3], text="user changed the password")
        else :
            #when user delete msg its can update DB msgcount
            msg_value_1=r.text.find('add_message_row(')+16
            msg_value_2=r.text.find(',{\\"su')
            msg_count=r.text[msg_value_1:msg_value_2]
            sql = "UPDATE mails SET   msg_count=%s WHERE users_id = %s"
            val = (msg_count, user_id)
            mycursor2.execute(sql, val)
            mydb.commit() 
    mydb.close()  
    return "updated"
if __name__ == "__main__":
    app.run()