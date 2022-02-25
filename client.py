from irc import *
import os
import sys
import time
import random
import datetime

## IRC Config
server = "127.0.0.1" # The IP/Hostname to connect to.
server_hostname = "irc.pesterchum.xyz" # The server's hostname.
#server = "havoc.ddns.net"
#server_hostname = "irc.havoc.ddns.net"
port = 3333
botnick = "calSprite"
logging_enabled = False
mood_on_join_enabled = False
insecure_mode = False # For if the hostname can't be verified for SSL/TLS.
                      # Havoc needs True
calsprite_rules_reminder_msg = "Welcome to Pesterchum! This is an automated reminder to please read the rules regarding canon handles: ( https://www.pesterchum.xyz/pesterchum-rules/ )" # Set to "" to disable

## Irrelevant variables
bot_hostname = "calSprite"
bot_servername = "calSprite"
bot_realname = "calSprite"
nickserv_username = "calSprite"

## Don't edit the variables past this point.
setup_finished = False
do_not_random_encounter_afk = []
canon_handles = ["apocalypseArisen", "arsenicCatnip", "arachnidsGrip", "adiosToreador", \
                 "caligulasAquarium", "cuttlefishCuller", "carcinoGeneticist", "centaursTesticle", \
                 "grimAuxiliatrix", "gallowsCalibrator", "gardenGnostic", "ectoBiologist", \
                 "twinArmageddons", "terminallyCapricious", "turntechGodhead", "tentacleTherapist", "meeps", \
                 "gutsyGumshoe", "timaeusTestified", "tipsyGnostalgic", "golgothasTerror", \
                 "ghostyTrickster", "undyingUmbrage", "uranianUmbra", "glutinousGymnast", "adamantGriftress", "thespiansGlamor"]
online_time_dictionary = {}
#for x in canon_handles:
#    online_time_dictionary.update({x: datetime.datetime.now()})
print("online_time_dictionary =" + str(online_time_dictionary))

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
irc = IRC(server_hostname, insecure_mode)
irc.connect(server, port, botnick, server_hostname, bot_hostname, bot_servername, bot_realname)

while True:
    try:
        text = irc.get_response()
            
        if (text!=None):
            print(text)
            #if ((("End of /MOTD" in text)|("MOTD File is missing" in text)) & (setup_finished==False)):
            if setup_finished==False:
                if (irc.post_connect_setup(botnick, nickserv_username, nickserv_password)==0):
                    setup_finished = True
                print("setup_finished = " + str(setup_finished))
            # RE check
            textSplit = text.split(":")
            if (len(textSplit) > 1):
                #print("len textSplit > 1")
                try:
                    nick = textSplit[1].split('!')
                    command = textSplit[1].split(' ')[1]
                except Exception as e:
                    print(e)
                    print("wtf sus????")
                    print("textSplit = " + str(textSplit))
                    nick = ['','']
                    command = ''
                
                if len(textSplit) > 2:
                    #print("len textSplit > 2")
                    
                    # command from canon handle
                    #print("nick[0] == " + nick[0])
                    if nick[0] in canon_handles:
                        print("canon")
                        print(textSplit[1].split(' ')[1] + textSplit[1].split(' ')[2])
                        # join
                        if command == "JOIN":
                            print("canon join")
                            if textSplit[2].startswith("#pesterchum"):
                                print("canon join #pesterchum")
                                print("update " + nick[0])
                                online_time_dictionary.update({nick[0]: datetime.datetime.now()})

                                #Send rules notification
                                try:
                                    if calsprite_rules_reminder_msg != "":
                                        irc.send("PRIVMSG " + nick[0]  + " " + calsprite_rules_reminder_msg + "\n")
                                except NameError as e:
                                    print("This shouldn't happen </3 " + str(e))
                                except KeyError as e:
                                    print("This shouldn't happen </3" + str(e))
                        # quit
                        elif command == "QUIT":
                            print("canon QUIT")
                            print("update " + nick[0])
                            try:
                                online_time_dictionary.pop(nick[0])
                            except NameError:
                                print("Can't pop, no such key.")
                            except KeyError:
                                print("Can't pop, no such key.")
                        # old part #pesterchum
                        #elif textSplit[1].split(' ')[1] + textSplit[1].split(' ')[2] == "PART#pesterchum":
                        #    print("canon PART")
                        #    print("canon part #pesterchum")
                        #    print("update " + nick[0])
                        #    try:
                        #        online_time_dictionary.pop(nick[0])
                        #    except NameError:
                        #        print("Can't pop, no such key.")
                        #    except KeyError:
                        #        print("Can't pop, no such key.")
                        # nick change from canon handle
                        elif command == "NICK":
                            print("pop da funni handle :o3")
                            try:
                                online_time_dictionary.pop(nick[0])
                            except NameError:
                                print("Can't pop, no such key.")
                            except KeyError:
                                print("Can't pop, no such key.")

                    # nick change to canon handle
                    if (command == "NICK") & (textSplit[2].strip() in canon_handles):
                        print("NICK change to canon handle, new key.")
                        online_time_dictionary.update({textSplit[2].strip(): datetime.datetime.now()})
                            
                        #Send rules notification
                        try:
                            if calsprite_rules_reminder_msg != "":
                                irc.send("PRIVMSG " + textSplit[2].strip()  + " " + calsprite_rules_reminder_msg + "\n")
                        except NameError:
                            print("This shouldn't happen </3")
                    
                    if (mood_on_join_enabled==True):
                        # Give mood
                        # Because of the bot's modes, we can't actually check for GETMOOD,
                        # so, I decided to have it respond when people join.
                        # Of course, setting a mood isn't actually neccisarry for anything,
                        # so disabling it might actually be better for people with low bandwith :(
                        if (("JOIN" in textSplit[1])&("#pesterchum" in textSplit[2])):
                            irc.send("PRIVMSG #pesterchum MOOD >7" + "\n")
                    if (("PRIVMSG calSprite" in textSplit[1])&("REPORT" in textSplit[2]) | ("PRIVMSG calSprite" in textSplit[1])&(textSplit[2].lower().startswith("report")) ):
                            irc.send("PRIVMSG #reports "+ str(text) + "\n")
                            f = open("reports.txt", "a")
                            f.write(text + '\n')
                            f.close()
                            irc.send("PRIVMSG "+ nick[0] + " Report send." + "\n")
                    elif (("PRIVMSG calSprite" in textSplit[1])&("onlineall" in textSplit[2].lower())):
                        #time_difference = online_time_dictionary
                        time_difference = {}
                        for x in online_time_dictionary:
                            time_difference.update({x: datetime.datetime.now()-online_time_dictionary[x]})

                        send_string = ""
                        for x in time_difference:
                            send_string += "PRIVMSG "+ nick[0] + " " + x + " has been online for " + str(round(time_difference[x].total_seconds() / 60)) + " minutes.\n"
                        #for x in send_string:
                        if send_string != '':
                            irc.send(send_string)
                        else:
                            irc.send("PRIVMSG "+ nick[0] + " No handles being tracked.\n")
                        #irc.send("PRIVMSG "+ nick[0] + str( round(difference.total_seconds() / 60, 0) ) + " minutes." + "\n")
                    elif (("PRIVMSG calSprite" in textSplit[1])&("help" in textSplit[2].lower())):
                        irc.send("PRIVMSG "+ nick[0] + " Replacement calSprite bot by @_turntechCatnip, msg for questions :3" + "\n")
                        irc.send("PRIVMSG "+ nick[0] + " Relevant resources:" + "\n")
                        irc.send("PRIVMSG "+ nick[0] + " - Website link: https://pesterchum.xyz" + "\n")
                        irc.send("PRIVMSG "+ nick[0] + " - Github repository: https://github.com/Dpeta/pesterchum-alt-servers" + "\n")
                        irc.send("PRIVMSG "+ nick[0] + " - Releases & Downloads: https://github.com/Dpeta/pesterchum-alt-servers/releases" + "\n")
                        irc.send("PRIVMSG "+ nick[0] + " - " + "\n")
                        irc.send("PRIVMSG "+ nick[0] + " - Pesterchum Discord: https://discord.gg/eKbP6pvUmZ" + "\n")
                        irc.send("PRIVMSG "+ nick[0] + " - Pesterchum Republic: https://discord.gg/BbHvdwN" + "\n")
                        irc.send("PRIVMSG "+ nick[0] + " - " + "\n")
                        irc.send("PRIVMSG "+ nick[0] + " - @calSprite repository: https://github.com/Dpeta/calSprite" + "\n")
                        irc.send("PRIVMSG "+ nick[0] + " - @randomEncounter repository: https://github.com/Dpeta/randomEncounter" + "\n")
                    else:
                        if ( ("PRIVMSG calSprite" in textSplit[1])&("COLOR >" not in textSplit[2])&("PESTERCHUM" not in textSplit[2]) ):
                            irc.send("PRIVMSG "+ nick[0] + " Commands are:" + "\n")
                            irc.send("PRIVMSG "+ nick[0] + " " + "    \"report [MESSAGE]\"" + "\n")
                            irc.send("PRIVMSG "+ nick[0] + " " + "    \"onlineall\"" + "\n")
                            irc.send("PRIVMSG "+ nick[0] + " " + "    \"help\"" + "\n")
                            
                # textsplit len 1 PART check
                # PART doesn't have a ':' ig??
                #print(textSplit[1].split(' ')[1] + textSplit[1].split(' ')[2])
                #print("len(textSplit[1].split(' ')) = " + str(len(textSplit[1].split(' '))))
                if len(textSplit[1].split(' ')) >= 2:
                    #print("len(textSplit[1].split(' ')) >= 2")
                    #print("textSplit[1].split(' ')[1] + textSplit[1].split(' ')[2] = \"%s\"" % str(textSplit[1].split(' ')[1] + textSplit[1].split(' ')[2]))
                    #print(textSplit[1].split(' ')[1] + textSplit[1].split(' ')[2] == "PART#pesterchum")
                    command_plus_target = textSplit[1].split(' ')[1] + textSplit[1].split(' ')[2]
                    command_plus_target = command_plus_target.replace('\n','').replace('\r','').strip()
                    if command_plus_target == "PART#pesterchum": 
                        print("canon PART")
                        print("canon part #pesterchum")
                        print("update " + nick[0])
                        try:
                            online_time_dictionary.pop(nick[0])
                        except NameError:
                            print("Can't pop, no such key.")
                        except KeyError:
                            print("Can't pop, no such key.")

            # Lingering handles fallback
            if datetime.datetime.now().second == 30:
                print('30')
                handle_list = irc.get_pesterchum_nick_list()
                for x in online_time_dictionary:
                    print("x=%s" % (x))
                    if x not in handle_list:
                        online_time_dictionary.pop(nick[0])
                        
                    
        else:
        #    # Check overtime
        #    time_difference = {}
        #    for x in online_time_dictionary:
        #        time_difference.update({x: datetime.datetime.now()-online_time_dictionary[x]})
        #        if ( int(time_difference[x].total_seconds()) % 3600 == 0) & \
        #           ( time_difference[x].total_seconds() > 1728000 ): #check if >8 hours every 60min
        #            irc.send("PRIVMSG #reports " + " " + x + " has been online for " + str(round(time_difference[x].total_seconds() / 60)) + " minutes.\n")
        #            irc.send("PRIVMSG "+ x + " This is an automated reminder not to hog canon handles :3 (According to calsprite you've been on " + x + " for " + str(round(time_difference[x].total_seconds() / 60)) + " minutes.)\n")
                    
            # Blanky mode
            time.sleep(1)
    except KeyboardInterrupt:
        if (irc.disconnect() == 0):
            print("Exiting gracefully.")
            sys.exit(0)
        else:
            print("Something went wrong :')")
            input()

