#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/4/12  下午10:03
# @Author  : wzZ
# @File    : products.py
# @Software: IntelliJ IDEA
import asyncio
import json

import aiofiles
import httpx
from httpx import HTTPError

from generation import generate_license


async def get_plugin_id(plugin_name):
    if not plugin_name:
        return None
    async with httpx.AsyncClient() as client:
        res = await client.get(f"https://plugins.jetbrains.com/api/searchPlugins?max=10&offset=0&search={plugin_name}")
        if res.status_code != 200:
            raise "Network Error"
        return res.json()["plugins"][0]["id"]


async def get_plugin_code(plugin_id):
    if not plugin_id:
        return None
    async with httpx.AsyncClient() as client:
        res = await client.get(f"https://plugins.jetbrains.com/api/plugins/{plugin_id}")
        if res.status_code != 200:
            raise HTTPError("Network Error")
        purchase = res.json().get("purchaseInfo")
        return purchase["productCode"]


async def get_all_plugin_code():
    async with httpx.AsyncClient() as client:
        res = await client.get("https://plugins.jetbrains.com/api/searchPlugins?max=10000&offset=0")
        if res.status_code != 200:
            raise HTTPError("Network Error")
        plugins = res.json()["plugins"]
        tasks = [get_plugin_code(plugin["id"]) for plugin in plugins if plugin["pricingModel"] != "FREE"]
        get_plugin_codes = await asyncio.gather(*tasks)
        get_plugin_codes = [code for code in get_plugin_codes if code is not None]

    async with aiofiles.open("../plugins_bak.json", "w") as f:
        await f.write(json.dumps(get_plugin_codes))


async def plugins_code_list(update: bool = False):
    # update plugins_bak.json
    if update:
        await get_all_plugin_code()
    async with aiofiles.open("../plugins_bak.json", "r") as f1:
        content = await f1.read()
    return json.loads(content)


async def get_software():
    async with httpx.AsyncClient() as client:
        res = await client.get("https://data.services.jetbrains.com/products?fields=code,name,description")
        if res.status_code != 200:
            raise HTTPError("Network Error")
        return res.json()


async def software_code_list(update: bool = False):
    async with aiofiles.open("../software_bak.json", "r") as f1:
        content = await f1.read()
        software_code = json.loads(content)
    # update = True
    if update:
        software = await get_software()
        for s in software:
            if s["code"] not in software_code:
                software_code.append(s["code"])
        async with aiofiles.open("../software_bak.json", "w") as f2:
            await f2.write(json.dumps(software_code))
    return software_code


async def active(username: str,
                 license_id: str,
                 active_all: bool = True,
                 plugin_name: str = None,
                 update: bool = False):
    """
    Activate all software and plugins for a given user.
    :param username: The name of the user to activate the products for.
    :param license_id: Identifier for the license.
    :param plugin_name: Plugin name to activate; only used when active_all is False.
    :param active_all: If True, activates all products, otherwise activates only specified plugin.
    :param update: If True, updates product codes which may take a while.
    """
    c_license = {
        "licenseId": license_id,
        "licenseeName": username,
        "assigneeName": username,
        "licenseRestriction": "",
        "checkConcurrentUse": True,
        "products": [],
        "metadata": "0120230102PPAA013009",
        "hash": "41472961/0:1563609451",
        "gracePeriodDays": 7,
        "autoProlongated": True,
        "isAutoProlongated": True
    }

    if active_all:
        if plugin_name:
            raise ValueError("Input Error: If you choose to activate all, you cannot specify a plugin name.")
        all_codes = await software_code_list(update=update) + await plugins_code_list(update=update)
        products = [{"code": code, "fallbackDate": "2099-12-31", "paidUpTo": "2099-12-31", "extended": True} for code in
                    all_codes]
        c_license["products"].extend(products)
    elif plugin_name:
        plugin_id = await get_plugin_id(plugin_name)
        code = await get_plugin_code(plugin_id)
        if not code:
            raise ValueError("Plugin code not found for the given plugin name.")
        c_license["products"].append(
            {"code": code, "fallbackDate": "2099-12-31", "paidUpTo": "2099-12-31", "extended": True})
    else:
        raise ValueError(
            "Input Error: You must either activate all or specify a plugin name for individual activation.")

    # Generate and print license
    c_license["licenseeName"] = username
    c_license["assigneeName"] = username
    activation_code = generate_license(c_license, license_id)
    print("Your activation code:")
    print(activation_code)
