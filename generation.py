#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/4/12  下午10:03
# @Author  : wzZ
# @File    : generation.py
# @Software: IntelliJ IDEA
import base64
import json

from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


def sign_license(license_part: bytes) -> bytes:
    with open('./jetbra.key', 'rb') as f:
        private_key = RSA.import_key(f.read())

    h = SHA1.new(license_part)

    signature = PKCS1_v1_5.new(private_key).sign(h)
    return signature


def get_cert_64() -> str:
    with open('jetbra.pem', 'rb') as f:
        pem_data = f.read()
    return ''.join(pem_data.decode().split('\n')[1:-2])


def generate_license(c_license: dict, license_id: str) -> str:
    c_license["licenseId"] = license_id
    license_part = json.dumps(c_license, separators=(',', ':')).encode('utf-8')
    signature = sign_license(license_part)

    license_part_base64 = base64.b64encode(license_part).decode('utf-8')
    signature_base64 = base64.b64encode(signature).decode('utf-8')

    license_result = f"{c_license['licenseId']}-{license_part_base64}-{signature_base64}-{get_cert_64()}"
    return license_result
