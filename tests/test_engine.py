# -*- coding: utf-8 -*-

import pytest

import inspect
import os

import yaml
import fnmatch
import pandas as pd

import IHEWAengine


if __name__ == "__main__":
    print('\nEngine\n=====')
    path = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe()))
    )

    engine = IHEWAengine.Engine(path, 'test_engine.yml')
    # print(engine._Engines__conf)

