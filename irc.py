import socket
import sys
import time
import random
import ssl

class IRC:
    def __init__(self, server_hostname):
        # Define the socket
        context = ssl.create_default_context()

        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        context.load_default_certs()
        
        irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc = context.wrap_socket(irc_socket, server_hostname=server_hostname)
 
    def send(self, message):
        # Send data
        self.irc.send(bytes(message, "UTF-8"))

    def connect(self, server, port, botnick, server_hostname, bot_hostname, bot_servername, bot_realname):
        # Connect to the server
        print("Connecting to: " + server)
        self.irc.connect((server, port))

        # For if the connecting is reaaaallly slow, give it a moment to not be dead :)

        resp = ""
        while(":" + server_hostname +" NOTICE" not in resp):
            resp = str(self.get_response())
            print(resp)
            time.sleep(1)
        resp = ""
        while(":" + server_hostname + " NOTICE" not in resp):
            resp = str(self.get_response())
            print(resp)
            time.sleep(1)
            
        cert = self.irc.getpeercert()
        print(cert)
        if (ssl.match_hostname(cert, server_hostname) == None):
            print("Cert (in decoded format as returned by SSLSocket.getpeercert()) matches the given hostname.")

        print(self.get_response())
        
        self.irc.send(bytes("USER " + botnick + " " + bot_hostname + " " + bot_servername + " :" + bot_realname + "\n", "UTF-8"))
        self.irc.send(bytes("NICK " + botnick + "\n", "UTF-8"))

        resp = ""
        fullresp = ""
        while((" :*** You are connected to " + server_hostname) not in fullresp):
            resp = str(self.get_response())
            print(resp)
            fullresp += resp.replace('\n','').replace('\r','')

            # Check if nick is taken.
            if ((":"+server_hostname+" 433 * "+botnick+" :Nickname is already in use.") in resp):

                botnick += str(random.randint(111,999))
                self.irc.send(bytes("USER " + botnick + " " + bot_hostname + " " + bot_servername + " :" + bot_realname + "\n", "UTF-8"))
                self.irc.send(bytes("NICK " + botnick + "\n", "UTF-8"))
            
            time.sleep(0.5)


    def post_connect_setup(self, botnick, nickserv_username, nickserv_password):
        print(self.get_response())
        self.irc.send(bytes("PRIVMSG nickserv identify " + nickserv_username + " " + nickserv_password + "\n", "UTF-8"))
        self.irc.send(bytes("MODE " + botnick + " +Bd " + "\n", "UTF-8"))
        print(self.get_response())
        
        self.irc.send(bytes("PRIVMSG nickserv recover " + nickserv_username + " " + nickserv_password + "\n", "UTF-8"))
        time.sleep(0.5)
        self.irc.send(bytes("NICK " + botnick + "\n", "UTF-8"))
        print(self.get_response())
        
        print(self.get_response())
        self.irc.send(bytes("JOIN " + "#reports" + "\n", "UTF-8"))
        self.irc.send(bytes("JOIN " + "#pesterchum" + "\n", "UTF-8"))
        self.irc.send(bytes("PRIVMSG #pesterchum MOOD >7" + "\n", "UTF-8"))
        print(self.get_response())

        return 0
        
    def disconnect(self, do_not_random_encounter):

        DN_RE_string = ""
        for x in range(len(do_not_random_encounter)):
            DN_RE_string += do_not_random_encounter[x]
            DN_RE_string += " "
        DN_RE_string = DN_RE_string.strip()
        
        f = open("do_not_random_encounter.txt", "w")
        f.write(DN_RE_string)
        f.close()
        
        self.irc.settimeout(1) # Time to wait for a response to QUIT from the server.
        self.irc.send(bytes("QUIT" + "\n", "UTF-8")) # Send quit command to server.
        try:
            print(self.get_response()) # Receive & print response.
        except:
            pass
        self.irc.shutdown(socket.SHUT_WR) # Disallow further sends.
        self.irc.close() # Close socket
        return 0
        
    def get_response(self):
        self.irc.settimeout(0)
        try:
            resp = self.irc.recv(2040).decode("UTF-8")
            if resp.find('PING') != -1:                      
                self.irc.send(bytes('PONG ' + resp.split() [1] + '\r\n', "UTF-8"))
        except:
            resp = None
 
        return resp
