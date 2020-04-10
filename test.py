#!/usr/bin/env python

import sys, types

import pytest

from mock import Mock

sys.path.append("/modules")

# sopel_module = types.PackageType("sopel")
# sopel_module.module = Mock(name="sopel.module")
# sys.modules["sopel"] = sopel_module

pytest.main(['/home/hellmuth/tests'])


