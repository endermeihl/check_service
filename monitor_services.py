import subprocess
import requests
import time
import threading
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# 配置部分
SERVICES = [
    {
        "name": "Seller Service",
        "url": "https://b.sinepower.cn/qqcharger/pcseller/business/changepower/getchargerinfo",
        "data": {"data": 500070500},
        "headers": {
            "Content-Type": "application/json",
            "User-Agent":"PostmanRuntime/7.39.0",
            "Cookie": "SESSION=269a5065-e81b-41d6-9631-0da535c75e97; JSESSIONID=C6D6DDEA1443315DFFDECCE54BA1E246"
        }
    },
    {
        "name": "小程序API",
        "url": "https://mp.sinepower.cn/qqcharger/appcust/business/discount/getalldiscount",
        "data":{"sellerNum":3041,"category":2},
        "headers": {
            "Content-Type": "application/json",
            "User-Agent":"PostmanRuntime/7.39.0",
            "Cookie": "SESSION=269a5065-e81b-41d6-9631-0da535c75e97; JSESSIONID=C6D6DDEA1443315DFFDECCE54BA1E246"
        }
    },
]
EMAILS = ["377439457@qq.com","1021211431@qq.com"]
NOTIFY_URL = "http://baidu.com"
LOG_FILE = "/home/ender/service_monitor.log"
RETRY_INTERVAL = 30
MAX_RETRIES = 3
CHECK_INTERVAL = 300  # 5 minutes

# 设置日志记录
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')

def send_email(subject, body):
    sendmail_location = "/usr/sbin/sendmail"  # 修改为 sendmail 的实际路径
    recipients = ", ".join(EMAILS)
    process = subprocess.Popen([sendmail_location, "-t", "-oi"], stdin=subprocess.PIPE)
    msg = f"Subject: {subject}\nTo: {recipients}\n\n{body}"
    process.communicate(msg.encode())

def notify_service(service_name, url, reason):
    logging.error(f"Service {service_name} is down. Reason: {reason}")
    send_email(f"服务《 {service_name} 》出现问题", f"服务 {service_name} 对应地址 {url} 访问异常. 返回: {reason}")
    requests.get(NOTIFY_URL)

def check_service(service):
    retries = 0
    headers = {"Content-Type": "application/json"}
    while retries < MAX_RETRIES:
        try:
            response = requests.post(service["url"], json=service["data"], headers=service.get("headers", {}), timeout=10)
            if response.status_code == 200:
                logging.info(f"{service['name']} is up. Response: {response.text}")
                return
            else:
                reason = f"Unexpected status code: {response.status_code}.存在错误"
                logging.warning(reason)
        except requests.RequestException as e:
            reason = str(e)
            logging.warning(reason)
        
        retries += 1
        time.sleep(RETRY_INTERVAL)

    # 如果连续3次失败，发送通知
    notify_service(service["name"], service["url"], reason)

def monitor_services():
    while True:
        threads = []
        for service in SERVICES:
            t = threading.Thread(target=check_service, args=(service,))
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        monitor_services()
    except KeyboardInterrupt:
        logging.info("Service monitor stopped manually.")
