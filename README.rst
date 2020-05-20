.. -*- mode: rst -*-

|CoverAlls|_ |Travis|_ |ReadTheDocs|_ |DockerHub|_ |PyPI|_

.. |CoverAlls| image:: https://coveralls.io/repos/github/wateraccounting/IHEWAengine/badge.svg?branch=master
.. _CoverAlls: https://coveralls.io/github/wateraccounting/IHEWAengine?branch=master

.. |Travis| image:: https://travis-ci.org/wateraccounting/IHEWAengine.svg?branch=master
.. _Travis: https://travis-ci.org/wateraccounting/IHEWAengine

.. |ReadTheDocs| image:: https://readthedocs.org/projects/ihewaengine/badge/?version=latest
.. _ReadTheDocs: https://ihewaengine.readthedocs.io/en/latest/

.. |DockerHub| image:: https://img.shields.io/docker/cloud/build/wateraccounting/ihewaengine
.. _DockerHub: https://hub.docker.com/r/wateraccounting/ihewaengine

.. |PyPI| image:: https://img.shields.io/pypi/v/IHEWAengine
.. _PyPI: https://pypi.org/project/IHEWAengine/


IHEWAengine
===========

IHE WaterAccounting Engine Tool.

- Engine1
- Engine2


Requirments for Python 2.7 and Anaconda2
----------------------------------------

- `wa <https://github.com/wateraccounting/wa>`_
- `watools <https://github.com/wateraccounting/watools>`_
- `WA_Hyperloop <https://github.com/wateraccounting/WA_Hyperloop>`_

Host machine, CMD
~~~~~~~~~~~~~~~~~

>>> docker pull continuumio/anaconda2
>>> docker run -it continuumio/anaconda2 bash

Docker container, Linux
~~~~~~~~~~~~~~~~~~~~~~~

>>> apt-get update
>>>
>>> apt-get install vim

**Git clone**

- wa
    >>> git clone https://github.com/wateraccounting/wa.git
- watools
    >>> git clone https://github.com/wateraccounting/watools.git
- WA_Hyperloop
    >>> git clone https://github.com/wateraccounting/WA_Hyperloop.git

**R, rpy2**

`r-base, r-base-dev <https://rpy2.github.io/>`_

>>> apt-get install r-base
>>> apt-get install r-base-dev

**CairoSVG**

- `libcairo2-dev <https://pypi.org/project/CairoSVG>`_
- `libffi-dev <https://github.com/libffi/libffi>`_

>>> apt-get install libcairo2-dev

>>> apt-get install libffi-dev

**GDAL**

`gdal-bin, libgdal-dev <https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html>`_

>>> apt-get install gdal-bin
>>> apt-get install libgdal-dev

>>> ls /usr/include

>>> export CPLUS_INCLUDE_PATH=/usr/include/gdal
>>> export C_INCLUDE_PATH=/usr/include/gdal

Check GDAL version::

    ogrinfo --version
    gdalinfo --version
    GDAL 2.4.0, released 2018/12/14

    pip install GDAL==GDAL VERSION FROM OGRINFO

**PyPi**

>>> pip install GDAL==2.4.0
>>> pip install netCDF4==1.5.3
>>> pip install rpy2==2.8.0
>>> pip install CairoSVG==1.0.22
>>> pip install geopy==1.22.0

Run
---

>>> cp /WA_Hyperloop/hyperloop_example.py /
>>>
>>> cd /
>>> python hyperloop_example.py


Note
====

For details, see https://www.wateraccounting.org/.
