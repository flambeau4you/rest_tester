# Technology

## Python Version

Use Python version 2.x not 3.x.
3.x is lastest.
Windows Subsystem for Linux can not support Python 2.x

## Make IDs to variables

If there are real IDs in the URLs, make the IDs to variables as below commands in VIM.

```
:%s/\/[^/ \t]\{32\}\//\/{id}\//g
:%s/\/[^/ \t]\{32\}"/\/{id}"/g
:%s/\/[^/ \t]\{36\}\//\/{id}\//g
:%s/\/[^/ \t]\{36\}"/\/{id}"/g
```
