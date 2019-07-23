import pytest

from socioFetcher.config import *


def test_Global():
    glb = Global()
    assert len(glb.__dict__.keys()) == 2


def test_BLS():
    bls = BLS()
    assert len(bls.__dict__.keys()) == 9


def test_BEA():
    bea = BEA()
    assert len(bea.__dict__.keys()) == 9


def test_Census():
    census = Census()
    assert len(census.__dict__.keys()) == 6


def test_Config():
    config = Config()
    assert isinstance(config.Global, Global)
    assert isinstance(config.BLS, BLS)
    assert isinstance(config.BEA, BEA)
    assert isinstance(config.Census, Census)
