import os
from datetime import datetime
import glob
import OpenSSL
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

cert_dir = os.getenv('CERT_DIR')
certificate_list = os.getenv('CERT_LIST').split(",")


def run_fast_scandir(dir, ext):  # dir: str, ext: list
    files = []

    for filename in glob.iglob(dir + '**/**', recursive=True):
        if os.path.isfile(filename):
            files.append(filename)

    return files


def get_expire_date():
    fullString = ""

    files = run_fast_scandir(cert_dir, [".crt", ".key"])
    for i in files:
        if os.path.basename(i) in certificate_list:
            f = open(i, "r")
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())
            bytesAfter = x509.get_notAfter()
            timestampAfter = bytesAfter.decode('utf-8')
            bytesBefore = x509.get_notBefore()
            timestampBefore = bytesBefore.decode('utf-8')
            fullString += os.path.basename(i) + ":" + "\n"
            fullString += "\t\tNot Before : " + datetime.strptime(timestampBefore, '%Y%m%d%H%M%SZ').strftime(
                "%b %d %H:%M:%S %Y") + "\n"
            fullString += "\t\tNot After  : " + datetime.strptime(timestampAfter, '%Y%m%d%H%M%SZ').strftime(
                "%b %d %H:%M:%S %Y") + "\n"

    return fullString


def get_expire_date_like_prometheus():
    fullString = ""

    files = run_fast_scandir(cert_dir, [".crt", ".key"])
    for i in files:
        if os.path.basename(i) in certificate_list:
            f = open(i, "r")
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())
            bytesAfter = x509.get_notAfter()
            timestampAfter = bytesAfter.decode('utf-8')
            bytesBefore = x509.get_notBefore()
            timestampBefore = bytesBefore.decode('utf-8')
            dateTimeBefore = datetime.strptime(timestampBefore, '%Y%m%d%H%M%SZ').strftime(
                "%b %d %H:%M:%S %Y")
            dateTimeAfter = datetime.strptime(timestampAfter, '%Y%m%d%H%M%SZ').strftime(
                "%b %d %H:%M:%S %Y")

            print(dateTimeAfter)
            print(dateTimeBefore)

            d1 = datetime.strptime(dateTimeBefore, '%b %d %H:%M:%S %Y')
            d2 = datetime.strptime(dateTimeAfter, '%b %d %H:%M:%S %Y')

            check = 0
            if (d2-d1).days < 30:
                check = 1
            else:
                check = 0

            fullString += "certificate_expire_check{cert_name=" + os.path.basename(
                i) + ",not_after=" + dateTimeBefore + ",not_before=" + dateTimeAfter+"} " + str(check)

    return fullString


@app.get("/", response_class=PlainTextResponse)
async def read_root():
    fullString = get_expire_date()
    return fullString


@app.get("/metrics", response_class=PlainTextResponse)
async def read_root():
    fullString = get_expire_date_like_prometheus()
    return fullString


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
