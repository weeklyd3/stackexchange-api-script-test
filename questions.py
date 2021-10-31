
#!/usr/bin/env python
import getpass
import logging
import logging.handlers
import os
import random
import requests
import sys
import json
import chatexchange.client
import chatexchange.events
from colorama import init, Fore, Back, Style
init()


logger = logging.getLogger(__name__)
if (not os.path.exists("num.txt")):
    open("num.txt", "w+").write("1")
    num = open("num.txt", "r+").read()
else:
    num = open("num.txt", "r+").read()
    open("num.txt", "w+").write(str(int(num) + 1))

def main():
    setup_logging()

    # Run `. setp.sh` to set the below testing environment variables
    global room

    host_id = 'stackexchange.com'
    room_id = '1'  # Sandbox

    if 'ChatExchangeU' in os.environ:
        email = os.environ['ChatExchangeU']
    else:
        email = input("Email: ")
    if 'ChatExchangeP' in os.environ:
        password = os.environ['ChatExchangeP']
    else:
        password = input("Password: ")

    client = chatexchange.client.Client(host_id)
    client.login(email, password)

    room = client.get_room(room_id)
    room.join()
    room.watch(on_message)

    print("(You are now in room #%s on %s.)" % (room_id, host_id))
    room.send_message("Hi! Question Monitor (try `!!/last30` or `!!/last30 preview`) (This is failed round "+ str(num) + " of testing.")
    mhelp = "Usage: !!/last30[ sitename][ preview]\nsitename: A site name (currently only `stackoverflow`, `superuser`, `serverfault`, or `askubuntu`)\npreview: If specified, preview is sent."
    helplines = mhelp.split("\n")
    i = 0
    while i < len(helplines):
        room.send_message(helplines[i])
        i += 1
    while True:
        pass
def on_message(message, client):
    if not isinstance(message, chatexchange.events.MessagePosted):
        # Ignore non-message_posted events.
        print(Fore.BLUE, end="")
        logger.debug("event: %r", message)
        print(Style.RESET_ALL, end="")
        return

    print("")
    a = message.content.split(" ")[1]

    if message.content.startswith('!!/last30'):
        if not a in ['stackoverflow', 'superuser', 'serverfault', 'askubuntu']:
            a = 'stackoverflow'
        
        site = a
        r = requests.get("https://api.stackexchange.com/2.3/posts?order=desc&sort=activity&site=" + site + "&key=1NjxX*Nb8cUwqN5S1BiKfg((")
        j = json.loads(r.text)
        j = j.items
        i = 0
        while i < 30:
            x = j()
            x = list(x)[0]
            print(Fore.GREEN + "obj: " + str(x[1][i]) + Style.RESET_ALL)
            x = x[1][i]
            string = "[" + x.get("post_type") + "] [Link to Post](" + x.get('link') + ") by [`" + x.get("owner").get("display_name") + "`](" + x.get("owner").get("link") + ") (Number " + str(i + 1) + ")"
            message.message.reply(str(string))
            if message.content.endswith(" preview"):
                message.message.reply(x.get('link'))
            i +=1


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.DEBUG)

    # In addition to the basic stderr logging configured globally
    # above, we'll use a log file for chatexchange.client.
    wrapper_logger = logging.getLogger('chatexchange.client')
    wrapper_handler = logging.handlers.TimedRotatingFileHandler(
        filename='client.log',
        when='midnight', delay=True, utc=True, backupCount=7,
    )
    wrapper_handler.setFormatter(logging.Formatter(
        "%(asctime)s: %(levelname)s: %(threadName)s: %(message)s"
    ))
    wrapper_logger.addHandler(wrapper_handler)


if __name__ == '__main__':
    main()
