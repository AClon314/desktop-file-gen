#!/bin/env python
import asyncio as aio
from pathlib import Path
from typing import Sequence, TypedDict, Literal, Unpack, Any
from desktop_file_gen.lib import get_title_icon, regex_version, version, Log
TYPE = Literal['Application', 'Link', 'Directory']
strs = Sequence[str]
OVERFLOW = 32


class _DesktopMustArgs(TypedDict):
    Name: str


class DesktopArgs(_DesktopMustArgs, total=False):
    Entry: None | str
    Type: TYPE
    Version: str
    GenericName: str
    NoDisplay: bool
    Comment: str
    Icon: Path
    Hidden: bool
    OnlyShowIn: strs
    NotShowIn: strs
    DBusActivatable: bool
    TryExec: str
    Exec: str
    Path: Path
    Terminal: bool
    Actions: Sequence['str | DesktopEntry']
    MimeType: strs
    Categories: strs
    Implements: strs
    # not be redundant with the values of Name or GenericName:
    Keywords: strs
    StartupNotify: bool
    StartupWMClass: str
    URL: str
    PrefersNonDefaultGPU: bool
    SingleMainWindow: bool


def toml_desktop(Dict: dict[str, Any], Entry: str | None, keep_None: bool = False) -> str:
    if Entry is None or Entry == 'Entry':
        Entry = 'Entry'
    S = f"[Desktop {Entry}]\n"
    for k, v in Dict.items():
        if k == 'Entry':
            continue
        elif isinstance(v, Path):
            v = str(v)
        elif isinstance(v, bool):
            v = 'true' if v else 'false'
        if keep_None or v:
            S += f"{k}={v}\n"
    return S


class DesktopEntry:
    def __repr__(self) -> str: return f"{self.__class__.__name__}({self.__dict__})"
    def __str__(self) -> str: return toml_desktop(self.__dict__, self.Entry)

    def __init__(self, path: str | None = None, **kw: Unpack[DesktopArgs]):
        self.Name = kw.get('Name')
        self.Entry = kw.get('Entry', None)
        self.Type = kw.get('Type', None)
        self.Version = kw.get('Version', None)
        self.GenericName = kw.get('GenericName', None)
        self.NoDisplay = kw.get('NoDisplay', False)
        self.Comment = kw.get('Comment', None)
        self.Hidden = kw.get('Hidden', False)
        self.OnlyShowIn = kw.get('OnlyShowIn', None)
        self.NotShowIn = kw.get('NotShowIn', None)
        self.DBusActivatable = kw.get('DBusActivatable', False)
        self.TryExec = kw.get('TryExec', None)
        self.Exec = kw.get('Exec', None)
        self.Path = kw.get('Path', None)
        self.Terminal = kw.get('Terminal', False)
        self.Actions = kw.get('Actions', None)
        self.MimeType = kw.get('MimeType', None)
        self.Categories = kw.get('Categories', None)
        self.Implements = kw.get('Implements', None)
        self.Keywords = kw.get('Keywords', None)
        self.StartupNotify = kw.get('StartupNotify', False)
        self.StartupWMClass = kw.get('StartupWMClass', None)
        self.URL = kw.get('URL', None)
        self.PrefersNonDefaultGPU = kw.get('PrefersNonDefaultGPU', False)
        self.SingleMainWindow = kw.get('SingleMainWindow', None)
        self = aio.run(self.init(path)) if path else None

    async def init(self, path: str):
        _path = Path(path)
        if '://' in path:
            self.Type = 'Link'
            self.URL = path
            title, icon = await get_title_icon(path)
            if title:
                self.Name = title[:OVERFLOW]
                self.Comment = title
            else:
                domain = path.split('/')[2]
                self.Name = domain[:OVERFLOW]
            if icon:
                self.Icon = icon
        elif _path.is_dir():
            Log.warning('use `ln -s` instead of `.desktop` file for directories')
            self.Type = 'Directory'
            self.Path = _path
            self.Name = _path.name
        else:
            self.Type = 'Application'
            self.Path = _path.parent if _path.parent != Path('.') else None
            self.Exec = path
            self.Name = _path.stem
            self.save()
            _version = await version(path)
            if _version is None:
                _version = regex_version(path)
            self.Version = _version
        return self

    def save(self, To: Path | None = None):
        if To is None:
            To = self.Path.joinpath(self.Name + '.desktop') if self.Path else Path(self.Name + '.desktop')
        with open(To, 'w') as f:
            f.write(str(self))
        return To


if __name__ == '__main__':
    ...
