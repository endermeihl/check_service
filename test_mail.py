import subprocess

EMAILS = ["377439457@qq.com","1021211431@qq.com"]
def send_email(subject, body):
    sendmail_location = "/usr/sbin/sendmail"  # 修改为 sendmail 的实际路径
    recipients = ", ".join(EMAILS)
    process = subprocess.Popen([sendmail_location, "-t", "-oi"], stdin=subprocess.PIPE)
    msg = f"Subject: {subject}\nTo: {recipients}\n\n{body}"
    process.communicate(msg.encode())

if __name__ == "__main__":
    try:
        send_email("test","test mail")
    except KeyboardInterrupt:
        pass