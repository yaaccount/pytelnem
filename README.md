# pytelnem
Telegram bot = python cgi with sqlite + javascript nem-sdk over zerorpc

### NOTES:
* telegram webhook requires https

### Ubuntu 16.04 prerequisities:
    $ sudo apt-get install lighttpd python nodejs-legacy

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

      $ sudo mkdir -p /var/www/html/cgi-bin/telegram

    -- create /var/www/html/cgi-bin/telegram/hello-world.py

      print("Content-Type: text/html\n")
      print("<html><head><title>Test</title></head><body>Hello world!</body></html>")

    -- set rights

      $ sudo chown -R www-data:www-data /var/www/html/cgi-bin/telegram
      $ sudo chmod a+x /var/www/html/cgi-bin/telegram/hello-world.py

#### Checkpoint 1: navigate to http://yourdomain/cgi-bin/telegram/hello-world.py, see if it works

* **enable + configure ssl**
    -- generate server certificate (self-signed)

      $ cd /etc/lighttpd/
      $ sudo mkdir certificates; cd certificates
      $ sudo openssl req -new -x509 -keyout domainname.pem -out domainname.pem -days 3650 -nodes

    -- enable ssl
    
      $ sudo lighty-enable-mod ssl
      
    -- modify /etc/lighttpd/conf-enabled/10-ssl.conf
    -> point ssl.pemfile to the domainname.pem
    
    -- reload lighttpd configuration
      $ sudo /etc/init.d/lighttpd force-reload

#### Checkpoint 2: navigate to https://yourdomain/cgi-bin/telegram/hello-world.py, see if it works



