
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

def getMinimumAttackStrength(s1, s2):
	r = battle(s1, s2)
	opti = [s1[0] - int(r[0][0]/1.9), s1[1] - int(r[0][1]/1.9), s1[2] - int(r[0][2]/1.9)]
	return opti