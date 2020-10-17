#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of addfips.
# http://github.com/fitnr/addfips

# Licensed under the GPL-v3.0 license:
# http://opensource.org/licenses/GPL-3.0
# Copyright (c) 2016, fitnr <fitnr@fakeisthenewreal>

"""
Add FIPS codes to lists and files that contain the names of US state and counties.
"""

from .addfips import AddFIPS

__version__ = '0.3.1'

__all__ = ['addfips']
