#!/bin/env python
import os
import re
import sys
import logging
import asyncio as aio
from platformdirs import user_data_path
from typing import Literal, Callable, Any, ParamSpec, TypeVar, cast
PS = ParamSpec('PS')
TV = TypeVar('TV')
IS_DEBUG = os.getenv('DEBUG')
if IS_DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
Log = logging.getLogger(__name__)
__appname__ = __name__.split('.')[0]


def copy_kwargs(
    kwargs_call: Callable[PS, Any]
) -> Callable[[Callable[..., TV]], Callable[PS, TV]]:
    """Decorator does nothing but returning the casted original function"""
    def return_func(func: Callable[..., TV]) -> Callable[PS, TV]:
        return cast(Callable[PS, TV], func)
    return return_func


async def popen(
    cmd: str,
    mode: Literal['realtime', 'wait', 'no-wait'] = 'wait',
    Raise=False,
    log: Callable = Log.warning,
    timeout=10,
    **kwargs
):
    """Used on long running commands

    Args:
        mode (str):
            - realtime: **foreground**, print in real-time
            - wait: await until finished
            - no-wait: **background**, immediately return, suitable for **forever-looping**, use:
            p = await popen('cmd', mode='bg')
            await p.expect(pexpect.EOF, async_=True)
            print(p.before.decode().strip())
        kwargs: `pexpect.spawn()` args

    Returns:
        process (pexpect.spawn):
    """
    import pexpect
    Log.info(f"{mode}: '{cmd}'")
    p = pexpect.spawn(cmd, timeout=timeout, **kwargs)
    FD = sys.stdout.fileno()
    def os_write(): return os.write(FD, p.read_nonblocking(4096))
    sig = 0
    if mode == 'realtime':
        while p.isalive():
            try:
                os_write()
            except pexpect.EOF:
                break
            except pexpect.TIMEOUT:
                log(f"Timeout: {cmd}")
                p.kill(sig)
                sig = 9
            except Exception:
                raise
            await aio.sleep(0.03)
        try:
            os_write()
        except pexpect.EOF:
            pass
    elif mode == 'wait':
        while p.isalive():
            try:
                await p.expect(pexpect.EOF, async_=True)
            except pexpect.TIMEOUT:
                log(f"Timeout: {cmd}")
                p.kill(sig)
                sig = 9
            except Exception:
                raise
    elif mode == 'no-wait':
        ...
    else:
        raise ValueError(f"Invalid mode: {mode}")
    if p.exitstatus != 0:
        if Raise:
            raise ChildProcessError(f"{cmd}")
        else:
            log(f'{p.exitstatus} from "{cmd}" → {p.before}')
    return p


@copy_kwargs(popen)
async def echo(*args, **kwargs):
    p = await popen(*args, mode='wait', **kwargs)
    if p.before and isinstance(p.before, bytes):
        text = p.before.decode()
        return p, text
    else:
        raise Exception(f"{args}, {kwargs}")

PATTERN_VERSION = re.compile(r'\d+\.\d+(?:\.\d+)?')


async def version(path: str):
    __ = '--'
    tasks = [
        echo(f'{path} {__[i:]}version', timeout=2, log=Log.debug) for i in range(3)
    ]
    tasks = await aio.gather(*tasks)
    for t in tasks:
        p, text = t
        Log.debug(text)
        if p.exitstatus == 0:
            return regex_version(text)


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
