import math
from backend import *

deff = [10000, 10000, 10000]
atta = [8, 8, 8]

print "Att:"
print atta
print "Def:"
print deff

print "--- battle ---"
ret = battle(atta, deff)

print "Att:"
print ret[0]
print "Def:"
print ret[1]