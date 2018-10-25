# multi-thread-telegram-bot
multi thread telegram bot for login in ut mail on shared cpanel host

Requirements
=================
1-cpanel host.

2-create bot with https://telegram.me/BotFather "bot token".


Introduction
============
this bot can login in the ut web mail service ,check new message and send them.

you can change the code and use it for another web

Getting started
============
go cpanel/software/setup python app.

Setup new application , after you created a new app u need install some modules , add flask , requests ,mysqlconnector and then click 
update now we need go and change passenger_wsgi.py
delete all code in the passenger_wsgi.py and then replace "from myapp import application" if your project name isnt myapp u need change the 
myapp with your project name 

now go to core.telegram.org and set yout webhook
my webhook url ("www.yourdomin.com/HOOK")

now u just need to go cpanel/advanced/cron jobs 
we need cronjobs timer for run our mailchecker every 5 min to get new users mail
and one more for update useres information every 24h(we need it when someone changed the password or deleted some mail)
like that
"	wget -q -O /dev/null "http://yourdomin.com/tele/mails/notif" > /dev/null 2>&1"

HF :)
