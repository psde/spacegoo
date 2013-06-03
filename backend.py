
def battle_round(attacker,defender):
	#nur eine asymmetrische runde. das hier muss mal also zweimal aufrufen.
	numships = len(attacker)
	defender = defender[::]
	for def_type in range(0,numships):
		for att_type in range(0,numships):
			multiplier = 0.1
			absolute = 1
			if (def_type-att_type)%numships == 1:
				multiplier = 0.25
				absolute = 2
			if (def_type-att_type)%numships == numships-1:
				multiplier = 0.01
			defender[def_type] -= (attacker[att_type]*multiplier) + (attacker[att_type] > 0) * absolute
		defender[def_type] = max(0,defender[def_type])
	return defender

def battle(s1,s2):
	ships1 = s1[::]
	ships2 = s2[::]
	while sum(ships1) > 0 and sum(ships2) >0:
		new1 = battle_round(ships2,ships1)
		ships2 = battle_round(ships1,ships2)
		ships1 = new1
		#print ships1,ships2

	ships1 = map(int,ships1)
	ships2 = map(int,ships2)
	#print ships1,ships2
	return ships1, ships2

def getMinimumAttackStrength(s1, s2, mod = 4.0):
	r = battle(s1, s2)
	opti = [s1[0] - int(r[0][0]/mod), s1[1] - int(r[0][1]/mod), s1[2] - int(r[0][2]/mod)]
	return opti
	opti = s1[::]
	while True:
		r = battle(s1, s2)
		if sum(r[0][::]) <= 3:
			break
		opti = s1[::]
		s1 = map(lambda x: int(x * 0.75), s1)
	return opti

def winsAgainst(att, deff):
	r = battle(att, deff)
	if sum(r[0]) >0:
		return True
	return False

def winsDeltaAgainst(att,deff):
	r = battle(att, deff)

	if sum(r[0]) > sum(r[1]):
		return True
	return False