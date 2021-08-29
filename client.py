from irc import *
import os, sys, time
import random

## IRC Config
server = "192.168.0.17" # The IP/Hostname to connect to.
server_hostname = "pesterchum.xyz" # The server's hostname.
port = 6697
botnick = "calSprite"
logging_enabled = True
mood_on_join_enabled = False

## Irrelevant variables
bot_hostname = "calSprite"
bot_servername = "calSprite"
bot_realname = "calSprite"
nickserv_username = "calSprite"

## Don't edit the variables past this point.
setup_finished = False
do_not_random_encounter_afk = []

## Checks if files are missing and asks to generate them if they are.
if (os.path.exists("./password.txt") == False):
    print("password.txt not found.")
    f = open("password.txt", "w")
    f.write(input("Please input nickserv password.\n"))
    f.close()

## Load variables
try:
    f = open("password.txt", "r")
    nickserv_password = f.read()
    f.close()
except:
    print("Failed to load nickserv password.")
    nickserv_password = ""
    
## IRC
irc = IRC(server_hostname)
irc.connect(server, port, botnick, server_hostname, bot_hostname, bot_servername, bot_realname)

while True:
    try:
        text = irc.get_response()
            
        if (text!=None):
            print(text)
            if (("End of /MOTD" in text) & (setup_finished==False)):
                print("End of /MOTD found")
                if (irc.post_connect_setup(botnick, nickserv_username, nickserv_password)==0):
                    setup_finished = True
                print("setup_finished = " + str(setup_finished))

            # RE check
            textSplit = text.split(":")
            if (len(textSplit) > 1):
                if (len(textSplit) > 2):
                    if (mood_on_join_enabled==True):
                        # Give mood
                        # Because of the bot's modes, we can't actually check for GETMOOD,
                        # so, I decided to have it respond when people join.
                        # Of course, setting a mood isn't actually neccisarry for anything,
                        # so disabling it might actually be better for people with low bandwith :(
                        if (("JOIN" in textSplit[1])&("#pesterchum" in textSplit[2])):
                            irc.send("PRIVMSG #pesterchum MOOD >7" + "\n")
                    if (("PRIVMSG calSprite" in textSplit[1])&("REPORT" in textSplit[2])):
                            irc.send("PRIVMSG #reports "+ str(text) + "\n")
                            f = open("reports.txt", "a")
                            f.write(text + '\n')
                            f.close()
                        else:
                            if ( ("PRIVMSG calSprite" in textSplit[1])&("COLOR >" not in textSplit[2])&("PESTERCHUM" not in textSplit[2]) ):
                                nick = textSplit[1].split('!')
                                irc.send("PRIVMSG "+ nick[0] + " Howdy! I currently do not do anything except forward reports, so please refrain from messaging me, thank you!" + "\n")
                    
        else:
            time.sleep(1)
    except KeyboardInterrupt:
        if (irc.disconnect(do_not_random_encounter) == 0):
            print("Exiting gracefully.")
            sys.exit(0)
        else:
            print("Something went wrong :')")
            input()

