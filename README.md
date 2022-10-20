Example environment variables


```
PRODIGY_KEY=XXXX-XXXX-XXXX-XXXX

export PIP_FIND_LINKS=https://${PRODIGY_KEY}@download.prodi.gy
```

# Troubleshooting

Errors in `make install` or `make reqs`:

```
ERROR: Could not install packages due to an OSError: [Errno 2] No such file or directory: '/home/user/bookfinder/.../build/
```

Try:

```
rm requirements-download.in
```

and running `make reqs` or `make install` again.
