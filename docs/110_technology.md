# Technology

## Python Version

Use Python version 3.x.
3.x is latest.

## Make IDs to variables

If there are real IDs in the URLs, make the IDs to variables as below commands in VIM.

```txt
:%s/\/[^/ \t]\{32\}\//\/{id}\//g
:%s/\/[^/ \t]\{32\}"/\/{id}"/g
:%s/\/[^/ \t]\{36\}\//\/{id}\//g
:%s/\/[^/ \t]\{36\}"/\/{id}"/g
```
