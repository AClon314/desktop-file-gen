# desktop-file-gen
Create .desktop for linux with fewest arguments.

## .desktop
| Key                   | type            | require |
| --------------------- | --------------- | ------- |
| Type                  | string          | YES     |
| Version               | string          | NO      |
| Name                  | localestring    | YES     |
| GenericName           | localestring    | NO      |
| NoDisplay             | boolean         | NO      |
| Comment               | localestring    | NO      |
| Icon                  | iconstring      | NO      |
| Hidden                | boolean         | NO      |
| OnlyShowIn, NotShowIn | string(s)       | NO      |
| DBusActivatable       | boolean         | NO      |
| TryExec               | string          | NO      |
| Exec                  | string          | NO      |
| Path                  | string          | NO      |
| Terminal              | boolean         | NO      |
| Actions               | string(s)       | NO      |
| MimeType              | string(s)       | NO      |
| Categories            | string(s)       | NO      |
| Implements            | string(s)       | NO      |
| Keywords              | localestring(s) | NO      |
| StartupNotify         | boolean         | NO      |
| StartupWMClass        | string          | NO      |
| URL                   | string          | YES     |
| PrefersNonDefaultGPU  | boolean         | NO      |
| SingleMainWindow      | boolean         | NO      |
