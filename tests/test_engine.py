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
    print(path)

    # path = os.path.dirname(os.path.abspath(__file__))
    # print(path)

    engine = IHEWAengine.Engine(path, 'test_engine.yml')
    # print(engine._Engines__conf)
