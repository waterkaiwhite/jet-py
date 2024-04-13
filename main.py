#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/4/13  下午9:52
# @Author  : wzZ
# @File    : main.py
# @Software: PyCharm
import asyncio

from power import get_key_and_pem, get_equal
from products import active

if __name__ == '__main__':
    get_key_and_pem()
    get_equal()
    try:
        asyncio.run(active("Water", "IKUN"))
        # asyncio.run(active("Water", "IKUN", update=True))  # updates product codes which may take a while
        # asyncio.run(active("Water", "IKUN", False, "Rainbow Brackets"))
    except Exception as e:
        print(e)
