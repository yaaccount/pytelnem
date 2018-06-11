(work in progress; guide needs verification)

# pytelnem
Telegram bot = python cgi with sqlite + javascript nem-sdk over zerorpc

### Disclaimer:
* I am not planning to develop this further beyond bug fixing. It is quick and dirty code finished in a hurry and it seems to be serving its purpose well. For new features, I would recommend to write this from scratch using different technologies - https://github.com/aleixmorgadas/nem-library-ts and https://github.com/felipebergamin/api-telegram-bot are easy to integrate (+ lighttpd mod_proxy to forward https from 443 to 3000)

### NOTES:
* telegram webhook requires https

### Ubuntu 16.04 prerequisities:
    $ sudo apt-get install lighttpd python python-pip nodejs-legacy npm libzmq-dev
    $ sudo pip install requests zerorpc
    $ sudo npm install -g node-gyp

### lighttpd config
* **enable cgi for python**

      $ sudo lighty-enable-mod cgi

    -- uncomment in /etc/lighttpd/conf-enabled/10-cgi.conf

      cgi.assign      = (
        ".py" => "/usr/bin/python",
      )

    -- reload lighttpd configuration
    
      $ sudo /etc/init.d/lighttpd force-reload
      
    -- prepare cgi folder

      $ mkdir /home/myusername/telegram
      $ sudo mkdir -p /var/www/html/cgi-bin
      $ cd /var/www/html/cgi-bin
      $ sudo ln -s /home/mysuername/telegram telegram

    -- create /home/myusername/telegram/hello-world.py

      #!/usr/bin/python
      
      print("Content-Type: text/html\n")
      print("<html><head><title>Test</title></head><body>Hello world!</body></html>")

    -- set rights

      $ chmod a+x /home/myusername/telegram/hello-world.py

#### Checkpoint 1: navigate to http://yourdomain/cgi-bin/telegram/hello-world.py, see if it works

* **enable + configure ssl**
    -- generate server certificate (self-signed)

      $ cd /etc/lighttpd/
      $ sudo mkdir certs; cd certs
      $ sudo openssl req -new -x509 -keyout public.pem -out public.pem -days 3650 -nodes

    -- enable ssl
    
      $ sudo lighty-enable-mod ssl
      
    -- modify /etc/lighttpd/conf-enabled/10-ssl.conf
    -> point ssl.pemfile to the /etc/lighttpd/certs/public.pem
    
    -- reload lighttpd configuration

      $ sudo /etc/init.d/lighttpd force-reload

#### Checkpoint 2: navigate to https://yourdomain/cgi-bin/telegram/hello-world.py, see if it works

### checkout, configure, run bot

* **telegram**

    -- define your bot via telegram (talk to @BotFather), get the TOKEN

* **checkout**

      $ cd ~/telegram
      $ git clone https://github.com/yaaccount/pytelnem
      $ cd pytelnem
      $ sudo chown -R www-data:www-data logs db

* **install node/npm dependencies**

      $ cd /home/myusername/telegram/pytelnem
      $ npm install nem-sdk zerorpc readline-sync

* **configure nem101bot.py**

    -- open it, set your telegram bot TOKEN, public ip and admin mode password

* **run tx signing service**

    -- inside "screen" session:

      $ screen
      $ node nemsdk-over-zerorpc.js

    -- input your wallet - content of .wlt (base64 string)

    -- input your wallet password

    -- <ctrl+a><ctrl+d> (detaches from the screen session)

    -- Note: later, you can always reconnect to live screen session using "screen -rd" and terminate the tx service by "<ctrl+c>"

