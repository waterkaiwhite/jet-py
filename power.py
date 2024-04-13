#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/4/12  下午10:03
# @Author  : wzZ
# @File    : power.py
# @Software: IntelliJ IDEA
import datetime

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def get_key_and_pem():
    one_day = datetime.timedelta(days=1)
    ten_day = datetime.timedelta(days=3650)
    today = datetime.datetime.today()
    yesterday = today - one_day
    tomorrow = today + ten_day

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    builder = x509.CertificateBuilder()

    builder = builder.subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, 'wzy-from-2024-04-10'),
    ]))
    builder = builder.issuer_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, 'JetProfile CA'),
    ]))
    builder = builder.not_valid_before(yesterday)
    builder = builder.not_valid_after(tomorrow)
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.public_key(public_key)

    certificate = builder.sign(
        private_key=private_key, algorithm=hashes.SHA256(),
        backend=default_backend()
    )
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption())
    public_bytes = certificate.public_bytes(
        encoding=serialization.Encoding.PEM)
    with open("jetbra.key", "wb") as f:
        f.write(private_bytes)
    with open("jetbra.pem", "wb") as f:
        f.write(public_bytes)


def get_cert():
    with open('jetbra.pem', 'rb') as f:
        pem_data = f.read()

    cert = x509.load_pem_x509_certificate(pem_data, default_backend())
    return cert


def get_equal():
    # get signature
    cert = get_cert()
    signature = cert.signature

    # convert to big int
    x = int.from_bytes(signature, byteorder='big')
    # default y z
    y = 65537
    z = 860106576952879101192782278876319243486072481962999610484027161162448933268423045647258145695082284265933019120714643752088997312766689988016808929265129401027490891810902278465065056686129972085119605237470899952751915070244375173428976413406363879128531449407795115913715863867259163957682164040613505040314747660800424242248055421184038777878268502955477482203711835548014501087778959157112423823275878824729132393281517778742463067583320091009916141454657614089600126948087954465055321987012989937065785013284988096504657892738536613208311013047138019418152103262155848541574327484510025594166239784429845180875774012229784878903603491426732347994359380330103328705981064044872334790365894924494923595382470094461546336020961505275530597716457288511366082299255537762891238136381924520749228412559219346777184174219999640906007205260040707839706131662149325151230558316068068139406816080119906833578907759960298749494098180107991752250725928647349597506532778539709852254478061194098069801549845163358315116260915270480057699929968468068015735162890213859113563672040630687357054902747438421559817252127187138838514773245413540030800888215961904267348727206110582505606182944023582459006406137831940959195566364811905585377246353

    zp_public_numbers = cert.public_key().public_numbers()

    # cal x^y mod zp_public_numbers.n
    r = pow(x, y, zp_public_numbers.n)

    with open('power.conf', 'w') as f:
        f.writelines('[Result]' + '\n' + f"EQUAL,{x},{y},{z}->{r}")
