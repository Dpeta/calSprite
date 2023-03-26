#! /usr/bin/env python3
"""calSprite bot for Pesterchum using asyncio.
Keeps track of canon handles and gives miscellaneous info."""
import os
import time
import random
import asyncio
import datetime
import traceback
import configparser

SOURCE = "https://github.com/Dpeta/calSprite"
VERSION = "calSprite"
CLIENTINFO = "VERSION SOURCE PING CLIENTINFO"
PCHUM_REPO = "https://github.com/Dpeta/pesterchum-alt-servers"
RE_SOURCE = "https://github.com/Dpeta/randomEncounter"
REPUBLIC = "https://discord.gg/BbHvdwN"
SUPPORT = "https://discord.gg/eKbP6pvUmZ"
PREFIXES = ["~", "&", "@", "%", "+"]  # channel membership prefixes
ACCEPTABLE_EXCEPTIONS = (OSError, TimeoutError, EOFError, asyncio.LimitOverrunError)
CANON_HANDLES = ["apocalypseArisen",
                 "arsenicCatnip",
                 "arachnidsGrip",
                 "adiosToreador",
                 "caligulasAquarium",
                 "cuttlefishCuller",
                 "carcinoGeneticist",
                 "centaursTesticle",
                 "grimAuxiliatrix",
                 "gallowsCalibrator",
                 "gardenGnostic",
                 "ectoBiologist",
                 "twinArmageddons",
                 "terminallyCapricious",
                 "turntechGodhead",
                 "tentacleTherapist",
                 "meeps",  # famous beloved homestuck character meeps
                 "gutsyGumshoe",
                 "timaeusTestified",
                 "tipsyGnostalgic",
                 "golgothasTerror",
                 "ghostyTrickster",
                 "undyingUmbrage",
                 "uranianUmbra",
                 "glutinousGymnast",
                 "adamantGriftress",
                 "thespiansGlamor"]

if not os.path.isdir("errorlogs"):
    os.makedirs("errorlogs")

class Users:
    """Class to keep track of users and their states"""

    def __init__(self):
        self.userlist = []
        self.canon_times = {}

    async def add(self, *users):
        """Adds users if they joined or someone changed their nick to a new handle"""
        for user in users:
            if user[0] in PREFIXES:
                user = user[1:]
            if user not in self.userlist:
                self.userlist.append(user)
            # Add canon
            if user in CANON_HANDLES and user not in self.canon_times:
                self.canon_times.update({user: datetime.datetime.now()})
        #print(f"self.canon_times: {self.canon_times}")

    async def remove(self, *users):
        """Adds users if they quit/parted or someone changed their nick to a new handle"""
        for user in users:
            if user[0] in PREFIXES:
                user = user[1:]
            if user in self.userlist:
                self.userlist.remove(user)
            if user in CANON_HANDLES:
                try:
                    self.canon_times.pop(user)
                except (NameError, KeyError) as key_skill_issue:
                    print(f"Failed to remove canon key. {key_skill_issue}")
        #print(f"self.canon_times: {self.canon_times}")

    async def sanity_check(self):
        """Check if there's not any canons that aren't actually online being tracked"""
        for user in self.canon_times.copy():
            if user not in self.userlist:
                self.canon_times.pop(user)

class CalSpriteBot:
    """Class for an instance of the 'calSprite' bot"""

    def __init__(self):
        self.end = False
        self.reader = None
        self.writer = None
        self.users = Users()
        self.start_time = datetime.datetime.now()

    async def send(self, text, *params):
        """Works with command as str or as multiple seperate params"""
        for param in params:
            text += " " + param
        print("Send: " + text)
        await self.writer.drain()
        self.writer.write((text + "\r\n").encode())

    async def get_config(self):
        """Gets bot configuration from 'config.ini'"""
        config = configparser.ConfigParser()
        if os.path.exists("config.ini"):
            config.read("config.ini")
        else:
            config["server"] = {
                "server": "127.0.0.1",
                "hostname": "irc.pesterchum.xyz",
                "port": "6667",
                "ssl": "False",
            }
            config["tokens"] = {
                "nickserv_username": "",
                "nickserv_password": "",
                "vhost_login": "",
                "vhost_password": "",
                "oper_password": "",
                "operserv_password": "",
            }
            with open("config.ini", "w", encoding="utf-8") as configfile:
                config.write(configfile)
            print("Wrote default config file.")
        return config

    async def connect(self):
        """Connect to the server."""
        config = await self.get_config()
        if config["server"].getboolean("ssl"):
            self.reader, self.writer = await asyncio.open_connection(
                config["server"]["server"],
                config["server"].getint("port"),
                ssl=config["server"].getboolean("ssl"),
                server_hostname=config["server"]["hostname"],
            )
        else:
            self.reader, self.writer = await asyncio.open_connection(
                config["server"]["server"],
                config["server"].getint("port"),
                ssl=config["server"].getboolean("ssl"),
            )
        await self.send("NICK calSprite")
        await self.send("USER RE 0 * :PCRC")

    async def welcome(self, _):
        """Actions to take when the server has send a welcome/001 reply,
        meaning the client is connected and nick/user registration is completed."""
        config = await self.get_config()
        await self.send("MODE calSprite +B")
        await self.send("JOIN #pesterchum")
        await self.send("JOIN #reports")
        await self.send(
            "VHOST", config["tokens"]["vhost_login"], config["tokens"]["vhost_password"]
        )
        await self.send(
            "PRIVMSG nickserv identify",
            config["tokens"]["nickserv_username"],
            config["tokens"]["nickserv_password"],
        )
        # Sign in to operserv
        if "oper_password" in config["tokens"]:
            await self.send(
                "OPER",
                "calSprite",
                config["tokens"]["oper_password"],
                )
        else:
            print("oper_password not in config tokens")
        if "operserv_password" in config["tokens"]:
            await self.send(
                "PRIVMSG",
                "operserv",
                "login",
                config["tokens"]["operserv_password"],
            )
        else:
            print("operserv_password not in config tokens")
        # Set mood/color
        await self.send("METADATA * set mood 18")  #  'PROTECTIVE' mood
        await self.send("METADATA * set color #ff0000")  # Red

    async def nam_reply(self, text):
        """RPL_NAMREPLY, add NAMES reply to userlist"""
        # List of names start
        names_str = text.split(":")[2]
        # after second delimiter
        names_list = names_str.split(" ")  # 0x20 is the seperator
        # Add to userlist
        for name in names_list:
            # Strip channel operator symbols
            if name[0] in PREFIXES:
                await self.users.add(name[1:])
            else:
                await self.users.add(name)

    async def privmsg(self, text):
        """Handles incoming PRIVMSG"""
        parameters = text.split(" ")[2:15]
        receiver = parameters[0]
        prefix = text[1:].split(" ")[0]
        nick = prefix[: prefix.find("!")]

        # All remaining parameters as str, the delimiter ':' is stripped.
        msg = text[text.find(parameters[1][1:]) :]

        # We can give mood :3
        if receiver == "#pesterchum":
            if "calSprite" in msg and msg.startswith("GETMOOD"):
                await self.send("PRIVMSG #pesterchum MOOD >18")

        # Return if not addressed to us or if it's just Pesterchum syntax weirdness.
        if (
            receiver != "calSprite"
            or msg.startswith("PESTERCHUM")
            or msg.startswith("COLOR")
        ):
            return

        if msg[0] != "\x01":
            cal_command = msg.split(' ')[0]
            print(cal_command)
            match cal_command.upper():
                case "REPORT":
                    await self.send(f"PRIVMSG #reports {nick}: {msg}")
                    await self.send(f"PRIVMSG {nick} Report send :3 (mods can only see reports"
                                    " if they're online, might be better to "
                                    "ping a mod on discord if it's urgent)")
                case "ONLINEALL":
                    runtime = int( (datetime.datetime.now()
                                    - self.start_time).total_seconds()/60 )
                    time_difference = {}
                    for canon_time_key in self.users.canon_times:
                        time_difference.update({canon_time_key:
                                                datetime.datetime.now()
                                                - self.users.canon_times[canon_time_key]})
                    if time_difference:
                        for canon in time_difference:
                            canon_time = int(time_difference[canon].total_seconds() / 60)
                            if canon_time == runtime:
                                await self.send(f"PRIVMSG {nick} {canon} has been "
                                                f"online for **AT LEAST** {canon_time} minutes.")
                            else:
                                await self.send(f"PRIVMSG {nick} {canon} has been"
                                                f" online for {canon_time} minutes.")
                    else:
                        await self.send(f"PRIVMSG {nick} No handles are currently being tracked.")
                    await self.send(f"PRIVMSG {nick} calSprite has been running for {runtime}"
                                    " minutes, results may be inaccurate "
                                    "if it only recently got online.")
                case "HELP":
                    await self.send(f"PRIVMSG {nick} calSprite is just a little weewa :3")
                    await self.send(f"PRIVMSG {nick} Commands are:")
                    await self.send(f"PRIVMSG {nick} - \"report [MESSAGE]\"")
                    await self.send(f"PRIVMSG {nick} - \"onlineall\"")
                    await self.send(f"PRIVMSG {nick} - \"help\"")
                    await self.send(f"PRIVMSG {nick} Resources:")
                    await self.send(f"PRIVMSG {nick} - Website link: https://www.pesterchum.xyz")
                    await self.send(f"PRIVMSG {nick} - Github repository: {PCHUM_REPO}")
                    await self.send(f"PRIVMSG {nick} - Releases & Downloads: {PCHUM_REPO}/releases")
                    await self.send(f"PRIVMSG {nick} - ")
                    await self.send(f"PRIVMSG {nick} - Pesterchum Support: {SUPPORT}")
                    await self.send(f"PRIVMSG {nick} - Pesterchum Republic: {REPUBLIC}")
                    await self.send(f"PRIVMSG {nick} - ")
                    await self.send(f"PRIVMSG {nick} - @calSprite repository: {SOURCE}")
                    await self.send(f"PRIVMSG {nick} - @randomEncounter repository: {RE_SOURCE}")
                case _:  # Wildcard, matches any value
                    # Help command
                    await self.send(f"PRIVMSG {nick} Commands are:")
                    await self.send(f"PRIVMSG {nick}    \"report [MESSAGE]\"")
                    await self.send(f"PRIVMSG {nick}    \"onlineall\"")
                    await self.send(f"PRIVMSG {nick}    \"help\"")
        else:
            # CTCP
            msg = msg.strip("\x01")
            match msg:
                case "VERSION":
                    await self.send(f"NOTICE {nick} \x01VERSION {VERSION}\x01")
                case "SOURCE":
                    await self.send(f"NOTICE {nick} \x01SOURCE {SOURCE}\x01")
                case "PING":
                    await self.send(f"NOTICE {nick} \x01{msg}\x01")
                case "CLIENTINFO":
                    await self.send(f"NOTICE {nick} \x01CLIENTINFO {CLIENTINFO}\x01")

    async def notice(self, text):
        """Handles incoming NOTICE"""
        parameters = text.split(" ")[2:15]
        receiver = parameters[0]
        prefix = text[1:].split(" ")[0]
        nick = prefix[: prefix.find("!")]

        if receiver != "calSprite":
            return

        # All remaining parameters as str, the delimiter ':' is stripped.
        msg = text[text.find(parameters[1][1:]) :]

        if msg.upper().startswith("REPORT"):
            await self.send(f"PRIVMSG #reports {nick}: {msg}")
            await self.send(f"PRIVMSG {nick} Report send :3 (mods can only see reports"
                            " if they're online, might be better to ping "
                            "a mod on discord if it's urgent)")

    async def ping(self, text):
        """Handle incoming pings"""
        await self.send("PONG" + text[4:])

    async def nick(self, text):
        """Handle users changing their nicks,
        nick got changed from old_nick to new_nick"""
        prefix = text[1:].split(" ")[0]
        old_nick = prefix[: prefix.find("!")]
        parameters = text.split(" ")[2:15]
        new_nick = parameters[0]
        if new_nick[0] == ":":
            new_nick = new_nick[1:]

        await self.users.remove(old_nick)
        await self.users.add(new_nick)

    async def quit(self, text):
        """Handle other user's QUITs"""
        prefix = text[1:].split(" ")[0]
        nick = prefix[: prefix.find("!")]
        await self.users.remove(nick)

    async def part(self, text):
        """Handle other user's PARTs"""
        prefix = text[1:].split(" ")[0]
        nick = prefix[: prefix.find("!")]
        await self.users.remove(nick)

    async def join(self, text):
        """Handle other user's JOINs"""
        prefix = text[1:].split(" ")[0]
        nick = prefix[: prefix.find("!")]
        if nick[0] == ":":
            nick = nick[1:]
        await self.users.add(nick)

    async def get_names(self):
        """Routinely retrieve the userlist from scratch."""
        while True:
            await asyncio.sleep(1200)  # 20min
            print("Routine NAMES reset.")
            self.users.userlist = []
            try:
                await self.send("NAMES #pesterchum")
            except AttributeError as fail_names:
                print(f"Failed to send NAMES, disconnected? {fail_names}")

            # Run sanity check with a delay
            await asyncio.sleep(600) # 10min
            self.users.sanity_check()

    async def decode_data(self, data):
        """Returns decoded string, returns one space if it fails."""
        try:
            return data.decode()
        except ValueError:
            return " "

    async def get_command(self, text):
        """Return IRC command from line of text, returns empty string if it fails."""
        text_split = text.split(" ")
        length = len(text_split)
        if text.startswith(":") and length >= 1:
            return text_split[1].upper()
        if length >= 0:
            return text_split[0].upper()
        return ""

    async def youreoper(self, *_msg):
        """Auth to operserv when we're oper."""
        config = await self.get_config()
        if "operserv_password" in config["tokens"]:
            await self.send(
                "PRIVMSG",
                "operserv",
                "login",
                config["tokens"]["operserv_password"],
            )
        else:
            print("operserv_password not in config tokens")
        await self.send("PRIVMSG operserv HELP")

    async def overtime_check_task(self):
        """Task to check for overtime every hour."""
        while True:
            time_difference = {}
            for canon_time_key in self.users.canon_times:
                time_difference.update({canon_time_key:
                                        datetime.datetime.now()
                                        - self.users.canon_times[canon_time_key]})
            if time_difference:
                for canon in time_difference:
                    canon_time = int(time_difference[canon].total_seconds() / 60)
                    if 600 > canon_time > 480:
                        # Warn for > 8 hours.
                        await self.overtime_warn(canon)
                    elif canon_time > 600:
                        # Change nick for > 10 hours.
                        await self.overtime(canon)
            await asyncio.sleep(3600)

    async def overtime_warn(self, handle):
        """Warn someone about being overtime."""
        await self.send(f"PRIVMSG {handle}",
                  ":You've been on a canon handle for >8 hours, maybe take a break :3")
        await self.send(f"PRIVMSG {handle}",
                  ":Limit is so other people get a turn, "
                        "check https://www.pesterchum.xyz/pesterchum-rules")

    async def overtime(self, handle):
        """Move someone off their handle if they've been on for too long."""
        new_handle = f"{handle}{random.getrandbits(10)}"
        await self.send(f"PRIVMSG {handle} :Changing your nick because of overtime.")
        await self.send(f"PRIVMSG operserv SVSNICK {handle} {new_handle}")

    async def main(self):
        """Main function/loop, creates a new task when the server sends data."""
        command_handlers = {
            "001": self.welcome,
            "353": self.nam_reply,
            "381": self.youreoper,
            #"366": self.end_of_names,
            "PING": self.ping,
            "PRIVMSG": self.privmsg,
            "NOTICE": self.notice,
            "NICK": self.nick,
            "QUIT": self.quit,
            "PART": self.part,
            "JOIN": self.join,
        }
        # Create task for routinely updating names from scratch
        asyncio.create_task(self.get_names())
        # Create task for moving overtime users.
        asyncio.create_task(self.overtime_check_task())

        # Repeats on disconnect
        while not self.end:
            # Try to connect
            try:
                await self.connect()
            except ACCEPTABLE_EXCEPTIONS as connection_exception:
                print("Failed to connect,", connection_exception)

            # Sub event loop while connected
            if self.writer and self.reader:  # Not none
                while not self.writer.is_closing() and not self.reader.at_eof():
                    try:
                        data = await self.reader.readline()
                        if data:
                            print(data)
                            text = await self.decode_data(data)
                            command = await self.get_command(text)
                            # Pass task to the command's associated function if it exists.
                            if command in command_handlers:
                                asyncio.create_task(command_handlers[command](text.strip()))
                    except ACCEPTABLE_EXCEPTIONS as core_exception:
                        print("Error,", core_exception)
                        # Write to logfile
                        local_time = time.localtime()
                        local_time_str = time.strftime("%Y-%m-%d %H-%M", local_time)
                        with open(
                            f"errorlogs/RE_errorlog {local_time_str}.log",
                            "a",
                            encoding="utf-8",
                        ) as file:
                            traceback.print_tb(core_exception.__traceback__, file=file)
                        self.writer.close()
                    except KeyboardInterrupt:
                        await self.send("QUIT goo by cwuel wowl,,")
                        self.end = True
            if not self.end:
                print("4.13 seconds until reconnect. . .")
                await asyncio.sleep(4.13)


if __name__ == "__main__":
    bot = CalSpriteBot()
    asyncio.run(bot.main())
    print("Exiting. . .")
