wxnatpy
=======


[![PyPi version](https://img.shields.io/pypi/v/wxnatpy.svg)](https://pypi.python.org/pypi/wxnatpy/)
[![Build Status](https://travis-ci.org/pauldmccarthy/wxnatpy.svg?branch=master)](https://travis-ci.org/pauldmccarthy/wxnatpy)


`wxnatpy` is a [wxPython](https://www.wxpython.org) widget which allows users
to browse the contents of a [XNAT](https://xnat.org) repository. It is built
on top of `wxPython` and
[xnatpy](https://bitbucket.org/bigr_erasmusmc/xnatpy).


## Installation


`wxnatpy` is on [PyPi](https://pypi.python.org/) - install it through `pip`:


```sh
pip install wxnatpy
```


`wxnatpy` is also on [conda-forge](https://conda-forge.org/) - install it
through `conda`:


```sh
conda install -c conda-forge wxnatpy
```


**Important note for Linux users** `wnatpy` depends on `wxpython 4` which, for
Linux platforms, is not available on PyPi.  Therefore, if you are using Linux,
you will need to install wxPython first - head to
https://extras.wxpython.org/wxPython4/extras/linux/ and find the directory
that matches your OS. Then run this command (change the URL accordingly):


```sh
pip install --only-binary wxpython -f https://extras.wxpython.org/wxPython4/extras/linux/gtk2/ubuntu-16.04/ wxpython
```


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
