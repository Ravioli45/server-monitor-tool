from datetime import datetime, timezone, timedelta
import http.client
from urllib.parse import urlparse, quote_plus
import base64
import ssl
import os
import uuid
import io

import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db
from app.models import *
from flask_apscheduler import APScheduler
from pyzipper import AESZipFile, ZIP_DEFLATED, WZ_AES
from cryptography import x509

scheduler = APScheduler()

app = create_app()

scheduler.init_app(app)


AUTH_STR = base64.b64encode(f"api:{os.environ.get('API_KEY')}".encode("ascii")).decode("ascii")
MAILBOX_URL = os.environ.get("MAILBOX_URL")
def send_alert_email(monitor: Monitor, message: str):

    # constructing body and headers of post request for mailgun api
    data = None
    payload = None
    headers = None
    if monitor.user.zip_key is None:
        data = {
            'from':f'Mailgun Sandbox <postmaster@{MAILBOX_URL}>',
            'to':f'{monitor.user.username} <{monitor.user.email}>',
            'subject':f'Issue detected with {monitor.url}',
            'text':message,
        }
        payload = "".join([f"{k}={quote_plus(v)}&" for k, v in data.items()])[:-1]

        headers = {
            "Authorization": f"Basic {AUTH_STR}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": f"{len(payload)}"
        }
    else:
        boundary = uuid.uuid4().hex.encode()

        data = {
            'from':f'Mailgun Sandbox <postmaster@{MAILBOX_URL}>',
            'to':f'{monitor.user.username} <{monitor.user.email}>',
            'subject':f'Issue detected ',
            'text': "More information included in attached file"
        }
        
        zip_buffer = io.BytesIO()
        with AESZipFile(zip_buffer, 'w', compression=ZIP_DEFLATED, encryption=WZ_AES) as zf:
            zf.setpassword(monitor.user.zip_key.encode())
            zf.writestr("alert.txt", message)
        zip_buffer.seek(0)

        payload = bytes()
        for k, v in data.items():
            payload += (b"--" + boundary + b'\r\n')
            payload += (f"Content-Disposition: form-data; name=\"{k}\"\r\n\r\n").encode()
            payload += (v.encode() + b"\r\n")

        payload += (b"--" + boundary + b'\r\n')
        payload += b"Content-Disposition: form-data; name=\"attachment\"; filename=\"alert.zip\"\r\n\r\n"
        payload += zip_buffer.getvalue() + b'\r\n'
        payload += (b"--" + boundary + b'--\r\n')
        zip_buffer.close()

        headers = {
            "Authorization":f"Basic {AUTH_STR}",
            "Content-Type": f"multipart/form-data; boundary={boundary.decode()}",
            "Content-Length": f"{len(payload)}"
        }
    
    
    try:
        # send request to mailgun api
        conn = http.client.HTTPSConnection("api.mailgun.net")
        conn.request("POST", f"/v3/{MAILBOX_URL}/messages", body=payload, headers=headers)

        response = conn.getresponse()
        response.close()
        conn.close()
    except:
        pass

# runs this function every five minutes
@scheduler.task('cron', id="check-monitors", minute="*/5")
def check_monitors():
    
    # the current app context is needed to access the database
    with scheduler.app.app_context():
        monitors = db.session.scalars(sa.select(Monitor).order_by(sa.asc(Monitor.time_next_ping))).all()

        for i in range(len(monitors)):
            try:
                current = monitors[i]

                # this *will* fail if current is not in db...
                if current.time_next_ping.replace(tzinfo=None) <= datetime.now(timezone.utc).replace(tzinfo=None):

                    try:
                        parsed_url = urlparse(current.url)

                        host = parsed_url.netloc
                        path = parsed_url.path
                        port = parsed_url.port

                        # use an unverified context so we can still
                        # connect if ssl is expired
                        context = ssl._create_unverified_context()

                        conn = http.client.HTTPSConnection(host, port=port or 443, context=context, timeout=10)
                        conn.request("GET", f"/{path}")
                        response = conn.getresponse()

                        # I couldn't find any other way to get the certificate from an 
                        # unverified ssl context
                        cert = x509.load_der_x509_certificate(conn.sock.getpeercert(True))
                        http_status = f"{response.status} {response.reason}"

                        response.close()
                        conn.close()

                        expires_on = cert.not_valid_after_utc
                        ssl_expired = expires_on < datetime.now(timezone.utc)

                    except TimeoutError:
                        http_status = "TIMEOUT"
                        ssl_expired = None
                    except:
                        http_status = "STATUS CHECK FAILED"
                        ssl_expired = None
                    finally:
                        new_status = Status(response=http_status, ssl_expired=ssl_expired, monitor=current)
                        db.session.add(new_status)
                        current.time_next_ping = datetime.now(timezone.utc) + timedelta(seconds=current.seconds_to_next_ping-1)
                        db.session.commit()

            except:
                # ...this *should* hit when parent is removed from db mid job (ie user deletes account while this is happening)
                db.session.rollback()

# this function is called every fifteen minutess
@scheduler.task('cron', id="send-status", minute="1-59/15")
def send_status_emails():
    
    # app context needed to access database
    with scheduler.app.app_context():

        # get all statuses that haven't had alerts sent out
        statuses = db.session.scalars(
            sa.select(Status).where(Status.alerted == False).order_by(sa.asc(Status.timestamp))
        ).all()
        
        for i in range(len(statuses)):
            try:
                current = statuses[i]

                message = ""
                if current.response != "200 OK":
                    message += f"'{current.response}' detected at {current.monitor.url}\r\n"
                
                if current.ssl_expired:
                    message += f"Expired ssl certificate detected at {current.monitor.url}\r\n"

                if message != "":
                    message = f"The following issues were detected at {current.timestamp}\r\n" + message
                    message += f"Alert sent at {datetime.now(timezone.utc)}"
                    send_alert_email(current.monitor, message)

                current.alerted = True
                db.session.commit()

            except:
                db.session.rollback()

# start background tasks
scheduler.start()

# adds some variables to `flask shell`
@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db}
