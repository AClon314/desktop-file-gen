#!/bin/env python
import os
import re
import logging
import asyncio as aio
from platformdirs import user_data_path
IS_DEBUG = os.getenv('DEBUG')
if IS_DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
Log = logging.getLogger(__name__)
__appname__ = __name__.split('.')[0]


PATTERN_VERSION = re.compile(r'\d+\.\d+(?:\.\d+)?')


async def echo(cmd: str, timeout: int = 2):
    from asyncio.subprocess import PIPE
    p = await aio.create_subprocess_shell(cmd=cmd, stdout=PIPE, stderr=PIPE)
    if p.stdout is None:
        raise RuntimeError(f'`{cmd}` failed to run, stdout is None')
    ret = await aio.wait_for(p.wait(), timeout=timeout)
    out = await p.stdout.read()
    out = out.decode().strip()
    return p, out


async def version(path: str):
    __ = '--'
    tasks = [
        echo(f'{path} {__[i:]}version') for i in range(3)
    ]
    tasks = await aio.gather(*tasks)
    for t in tasks:
        p, text = t
        Log.debug(text)
        ver = regex_version(text)
        if p.returncode == 0 and (ver := regex_version(text)):
            Log.info(f'{ver=}')
            return ver


def regex_version(text):
    ver = PATTERN_VERSION.finditer(text)
    ver = next(ver, None)
    ver = ver.group(0) if ver else None
    return ver


async def get_title_icon(url: str):
    """异步获取url: title, icon_path"""
    import aiohttp
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    domain = url.split('/')[2]
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=timeout) as response:
            response.raise_for_status()  # 检查请求是否成功
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # 获取标题
            title = soup.title.string if soup.title else None

            # 获取 favicon
            icon_link = soup.find("link", rel=lambda x: x and "icon" in x.lower())
            icon_url = urljoin(url, icon_link["href"]) if icon_link and icon_link.get("href") else None
            icon_path = None

            if icon_url:
                # 下载 favicon 文件
                icon_response = await session.get(icon_url, timeout=timeout)
                icon_response.raise_for_status()
                icon_data = await icon_response.read()

                # 保存到本地文件
                _path = user_data_path(__appname__)
                _path.mkdir(parents=True, exist_ok=True)
                icon_path = _path.joinpath(domain)
                with open(icon_path, "wb") as f:
                    f.write(icon_data)

            return title, icon_path

if __name__ == '__main__':
    ...
    # import asyncio as aio
    # p = aio.run(version('ffmpeg'))
