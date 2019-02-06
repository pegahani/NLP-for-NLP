"developer: Aurelien"

from random import randrange
from Genetic.jensenshannon import CalcJS

fichier_sortie = "out.txt"
fichier_source = "concat.txt"
taille_max = 100
n_mut = 1
n_indivs = 240
n_mutes = 80
n_croises = 160
n_aleas = 80
n_gen = 150

def phrases_egales (p1, p2):
	#if len(p1["mots"]) != len(p2["mots"]):
	#	return False
	#for i in range(len(p1["mots"])):
	#	if p1["mots"][i] != p2["mots"][i]:
	#		return False
	#return True
	return p1["id"] == p2["id"]

class Individu:
	def __init__(self, phrases, taille_max, calcJS , method="init", i1 = None):
		if method == "init":
			self.phrases = []
			p_cpy = []
			self.taille = 0
			self._complete(phrases, taille_max)
		elif method == "copie":
			self.phrases = [p for p in i1.phrases]
			#print "copie : "
			#print self.phrases
			self.taille = i1.taille
		self._calcule_score(phrases, calcJS)
		#print len(self.phrases)
		#print "score : "+str(self.score)
	
	def phrase_presente(self, p):
		for p1 in self.phrases:
			if phrases_egales(p, p1):
				return True
		return False

	def _complete(self, phrases, taille_max):
		p_cpy = []
		for p in phrases:
			if p["taille"] <= taille_max - self.taille and not self.phrase_presente(p) :
				p_cpy.append(p)
		
		while self.taille < taille_max and len(p_cpy) != 0:
			#print "avant : "+str(self.taille)
			random_index = randrange(len(p_cpy))
			self.phrases.append(p_cpy[random_index])
			self.taille += p_cpy[random_index]["taille"]
			p_cpy.pop(random_index)
			i = 0
			while i < len(p_cpy):
				p = p_cpy[i]
				if p["taille"] > (taille_max - self.taille):
					p_cpy.pop(i)
				else:
					i+=1
					#print "phrase possible : "+str(p["taille"])
			#print "apres : "+str(self.taille)
		
	#Renvoie une mutation de self
	def _mutation(self, phrases, taille_max, calcJS, n_mut):
		ind = Individu(phrases, taille_max, calcJS, method="copie", i1=self)
		#suppression d'une ou plusieurs phrases
		for i in range(n_mut):
			random_index = randrange(len(ind.phrases))
			ind.taille -= ind.phrases[random_index]["taille"]
			ind.phrases.pop(random_index)
		
		ind._complete(phrases, taille_max)
		#print ind.phrases
		ind._calcule_score(phrases, calcJS)
		#print "mut : "
		#print ind.score
		return ind
		
	#Renvoie un croisement entre self et i2
	def _croisement(self, phrases, taille_max, calcJS, i2):
		ind = Individu(phrases, taille_max, calcJS, method="copie", i1=self)
		for p in i2.phrases:
			if not ind.phrase_presente(p):
				ind.phrases.append(p)
				ind.taille += p["taille"]
		#print ind.phrases
		while ind.taille > taille_max:
			#print "Reajustement de taille "+str(ind.taille)+"a taille :"+str(taille_max)
			#print ind.phrases
			random_index = randrange(len(ind.phrases))
			ind.taille -= ind.phrases[random_index]["taille"]
			ind.phrases.pop(random_index)
			
		ind._complete(phrases, taille_max)
		#print ind.phrases
		ind._calcule_score(phrases, calcJS)
		#print "croise : "
		#print ind.score
		return ind
	
	def _calcule_score(self, phrases, calcJS):
		self.tokens = {}
		for p in self.phrases:
			#print p
			for i in p["tokens"]:
				if i in self.tokens:
					self.tokens[i] += p["tokens"][i]
 				else:
					self.tokens[i] = p["tokens"][i]
		
		self.score = calcJS.calcule_js(self)

	def get_score(self):
		return self.score

	def print_indiv(self):
		print ("Affichage individu : ")
		for p in self.phrases:
			print (p)
		print ("score : "+str(self.get_score()))
		print ("Fin Affichage individu")

class Population:
	#taille_max : la taille maximum d'un individu, phrases : le set de phrases a partir duquel on cree les indivs
	def __init__(self, n_indivs, n_mutes, n_croises, n_aleas, n_mut, phrases, taille_max, fichier_source):
		self.indivs=[]
		self.phrases = phrases
		self.taille_max = taille_max
		self.n_indivs=n_indivs
		self.n_mutes = n_mutes
		self.n_croises = n_croises
		self.n_aleas = n_aleas
		self.n_mut = n_mut
		self.calcJS = CalcJS(fichier_source)
		for i in range(n_indivs):
			self.indivs.append(Individu(phrases, taille_max, self.calcJS))
	
	#On ne garde comme parents que les gagnants de n_indivs/2 tournois		
	def _sel_tournoi (self):
		indexes = [i for i in range(self.n_indivs)]
		tournois = []
		for i in range(int(self.n_indivs/2)):
			ri1 = randrange(len(indexes))
			i1 = indexes[ri1]
			indexes.pop(ri1)
			ri2 = randrange(len(indexes))
			i2 = indexes[ri2]
			indexes.pop(ri2)
			tournoi = i1,i2
			tournois.append(tournoi)
		parents = []
		for (i1, i2) in tournois:
			#print "sel"
			#print self.indivs
			#print " "+str(i1)+" "+str(i2)
			if self.indivs[i1].get_score() < self.indivs[i2].get_score():
				parents.append(self.indivs[i1])
			else:
				parents.append(self.indivs[i2])
		self.indivs = parents

	#Renvoie un tableau d'individus mutes d'apres les individus presents
	def _genere_mutations (self):
		indivs_mutes = []
		for i in range(self.n_mutes):
			#Selection d'un individu a muter
			ri = randrange(len(self.indivs))
			indivs_mutes.append(self.indivs[ri]._mutation(self.phrases, self.taille_max, self.calcJS, self.n_mut))
			self.indivs.pop(ri)
		return indivs_mutes

	def _genere_aleas (self):
		indivs_aleas = []
		for i in range(self.n_aleas):
			indivs_aleas.append(Individu(self.phrases, self.taille_max, self.calcJS))
		return indivs_aleas
	
	def _genere_croisements (self):
		indivs_mutes = []
		for i in range(self.n_croises):
			#Selection d'un individu a muter
			ri1 = randrange(len(self.indivs))
			ri2 = randrange(len(self.indivs))
			indivs_mutes.append(self.indivs[ri1]._croisement(self.phrases, self.taille_max, self.calcJS, self.indivs[ri2]))
		return indivs_mutes

	def optimise (self, n_gen):
		ind_max = Individu(self.phrases, self.taille_max, self.calcJS, method="copie", i1=self.get_max())
		print ("0eme generation. "+str(len(self.indivs))+" individus. Score max : "+str(ind_max.get_score()))
		for i in range(n_gen):
			self._sel_tournoi()
			mutations = self._genere_mutations()
			#print str(len(mutations)) + " indivs mutes"
			croisements = self._genere_croisements()
			#print str(len(croisements)) + " indivs croises"
			aleas = self._genere_aleas()
			#print str(len(aleas)) + " indivs aleas"
			self.indivs = self.indivs + mutations + croisements + aleas
			#print self.indivs
			#Recupere l'individu max
			max_i = self.get_max()
			#print "max_i : "
			#max_i.print_indiv()
			if ind_max is None or max_i.get_score() < ind_max.get_score():
				#print "ancien max : "+str(ind_max.get_score())+" nouveau max : "+str(max_i.get_score())
				ind_max = Individu(self.phrases, self.taille_max, self.calcJS, method="copie", i1=max_i)
			#self.print_gen()
			print (str(i+1)+"eme generation. "+str(len(self.indivs))+" individus. Score max : "+str(ind_max.get_score()))
		return ind_max

	def get_max (self):
		#On peut la changer, c'est un bete max
		#print "get_max"
		ind_max = None
		for i in self.indivs:
			#print "parcours indiv"
			if ind_max is None or i.get_score() < ind_max.get_score():
				ind_max = i
				#print "ind_max change : "
				#ind_max.print_indiv()
		return ind_max
	
	def print_gen (self):
		for i in self.indivs:
			i.print_indiv()

#Lecture des phrases
fp = open(fichier_source, "r")
phrases = []
cpt = 0
for ligne in fp:
	ligne = ligne.rstrip()
	if cpt == 2:
		tab = ligne.split("\t")
		i = 0
		for t in tab:
			#print i
			p = {}
			p["taille"] = int(t)
			p["id"] = i
			phrases.append(p)
			i += 1
	if cpt > 2 and cpt-3 < len(phrases):
		tab = ligne.split("\t")
		i = 0
		phrases[cpt-3]["tokens"] = {}
		for t in tab:
			if t > 0 and cpt-3 < len(phrases):
				#print cpt-3
				#print t
				phrases[cpt-3]["tokens"][i] = int(t)
			i+=1
	elif cpt-3 >= len(phrases):
		print ("Phrase surnumeraire")
	cpt += 1
fp.close()

#Creation de la population
population = Population(n_indivs, n_mutes, n_croises, n_aleas, n_mut, phrases, taille_max, fichier_source)

ind_max = population.optimise(n_gen)

fp = open (fichier_sortie, "w")
for p in phrases:
	if ind_max.phrase_presente(p):
		fp.write("1 ")
	else:
		fp.write("0 ")
fp.write("\n")
fp.close()