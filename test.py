import math
from backend import *

deff = [20, 10, 5]
atta = [10, 25, 19]

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

print "----"
print getMinimumAttackStrength(atta, deff)
atta = [atta[0] - int(ret[0][0]/1.9), atta[1] - int(ret[0][1]/1.9), atta[2] - int(ret[0][2]/1.9)]
print "Opti:"
print atta
print "Def:"
print deff

print "--- battle opti ---"
ret = battle(atta, deff)
print "Att:"
print ret[0]
print "Def:"
print ret[1]
