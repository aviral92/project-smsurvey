import unittest
import os
import inspect
import sys

c = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
p = os.path.dirname(c)
pp = os.path.dirname(p)
ppp = os.path.dirname(pp)
pppp = os.path.dirname(ppp)
ppppp = os.path.dirname(pppp)
sys.path.insert(0, ppppp)

