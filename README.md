wxnatpy
=======


[![PyPi version](https://img.shields.io/pypi/v/wxnatpy.svg)](https://pypi.python.org/pypi/wxnatpy/)
[![Build Status](https://travis-ci.org/pauldmccarthy/wxnatpy.svg?branch=master)](https://travis-ci.org/pauldmccarthy/wxnatpy)


`wxnatpy` is a [wxPython](https://www.wxpython.org) widget which allows users
to browse the contents of a [XNAT](https://xnat.org) repository. It is built
on top of `wxPython` and
[xnatpy](https://bitbucket.org/bigr_erasmusmc/xnatpy).


## Installation


`wxnatpy` is on [PyPi](https://pypi.python.org/) - install it throuygh `pip`:


```sh
pip install --pre wxnatpy
```


**Important** `wnatpy` depends on `wxpython 4` which, as of October 2017 has
not yet been officially released. Therefore, you need to add the `--pre` flag
when installing via `pip`. Under Linux, you will also need to have the
`wxpython` compile-time dependencies available in order to install `wxpython`.


## Usage


The `wxnat.XNATBrowserPanel` is a `wx.Panel`, which is intended to be embedded
in a `wxpython` application. The `wxnat` package can also be called as a
standalone application, e.g.:

```sh
python -m wxnat
```

This will open a dialog containing the browser panel, and *Download* and
*Close* buttons.


## Acknowledgements


Development on `wxnatpy` began at the [2017 XNAT Developer
Workshop](https://wiki.xnat.org/workshop-2017/), in Rotterdam, 16th-18th
November 2017, with the support of the [Wellcome Centre for Integrative
Neuroimaging](https://www.ndcn.ox.ac.uk/divisions/fmrib/).