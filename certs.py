import os

import yaml
from datetime import datetime
import OpenSSL
import ssl
import time

from sanic import Sanic
from sanic.response import text

app = Sanic("MyHelloWorldApp")

cert_dir = ".\\certs"
certificate_list = []


class Singleton(object):
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class MyTimeManager(Singleton):

    def updateParameter(self):
        global cert_dir
        global certificate_list
        with open("certs.yaml", 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            cert_dir = data_loaded["cert_dir"]
            certificate_list = data_loaded["certificate_list"]

    @property
    def cert_dir(self):
        return self.cert_dir

    @property
    def certificate_list(self):
        return self.certificate_list


def run_fast_scandir(dir, ext):  # dir: str, ext: list
    subfolders, files = [], []

    for f in os.scandir(dir):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)

    for dir in list(subfolders):
        sf, f = run_fast_scandir(dir, ext)
        subfolders.extend(sf)
        files.extend(f)

    return files


def get_expire_date():
    fullString = ""

    files = run_fast_scandir(cert_dir, [".crt", ".key"])
    for i in files:
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


@app.get("/")
async def hello_world(request):
    fullString = get_expire_date()
    return text(fullString)


if __name__ == '__main__':
    app.prepare(host='0.0.0.0', port=8000)
    MyTimeManager().updateParameter()
    Sanic.serve()
