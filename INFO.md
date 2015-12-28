
```
Developed using Python 2.7.3
Database is PostgreSQL 9.1
```

### Restore database and site backups; restore ssl certificates

### Install requirements and setup virtualenv:

```
$ su - global_tender	# change username
$ pip install virtualenvwrapper
...
$ export WORKON_HOME=~/Envs
$ mkdir -p $WORKON_HOME
$ source /usr/local/bin/virtualenvwrapper.sh
$ mkvirtualenv --system-site-packages global-tender.ru
$ workon global-tender.ru

# enter repository root directory and install python packages:
$ pip install -r requirements.txt
```

### Setup Production (using nginx + gunicorn)

####Running gunicorn (WSGI HTTP Server) this way (5 instances, max timeout 30 seconds):

```
gunicorn system.wsgi -w 5 -t 30 --log-file=/path/to/gunicorn.log -b 127.0.0.1:9090
```

####Nginx config for our virtual host (replace PATH where needed):

```
server {
       listen         80;
       server_name    global-tender.ru www.global-tender.ru;
       return         301 https://$server_name$request_uri;
}

server {                                                                                                                                                                                        
        listen 443 ssl;                                                                                                                                                                         

        server_name global-tender.ru www.global-tender.ru;

        ssl_certificate /etc/letsencrypt/live/global-tender.ru/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/global-tender.ru/privkey.pem;



        access_log /path/to/global-tender.ru.access.log;
        error_log /path/to/global-tender.ru.error.log;

        root /path/to/app/tender/;

        location ~* \.(?:ico|css|js|gif|jpe?g|png)$ {
                expires 10d;
                add_header Pragma public;
                add_header Cache-Control "public";
        }

        gzip on;
        gzip_disable "msie6";

        gzip_comp_level 6;
        gzip_min_length 1100;
        gzip_buffers 16 8k;
        gzip_proxied any;
        gzip_types
            text/plain
            text/css
            text/js
            text/xml
            text/javascript
            application/javascript
            application/x-javascript
            application/json
            application/xml
            application/xml+rss;


        location /static/ { # STATIC_URL
                alias /path/to/app/tender/static/; # STATIC_ROOT
                expires 30d;
        }

        location /uploads/ {
                alias /path/to/app/tender/uploads/;
                expires 30d;
        }

        location / {
                proxy_pass_header Server;
                proxy_set_header Host $http_host;
                proxy_redirect off;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Scheme $scheme;
                proxy_connect_timeout 30;
                proxy_read_timeout 1000;
                proxy_pass http://127.0.0.1:9090/;
        }
}
```

### Additional info

####Ways to modify images or pdf before publishing (feedbacks, etc...):
```

for img in *; do convert "$img" -resize "512" "sml_${img}"; done

convert -density 300 -trim test.pdf -quality 100 test.jpg

```