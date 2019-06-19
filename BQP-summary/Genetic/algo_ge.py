from random import randrange
from jensenshannon import CalcJS
import sys
from subprocess import Popen, PIPE
import subprocess

# -*- coding:Utf8 -*-

fichier_sortie = sys.argv[2]
fichier_source = sys.argv[1]

tt = fichier_source.split('/')
adress = '/'.join(tt[0:4])
which_tac = tt[-1][-6:-4]
file_stats = "stat_ws"+which_tac+".txt"

taille_max = 100 #3	#100
n_mut = 1
n_indivs = 240
n_mutes =  80
n_croises =  160
n_aleas =  80
n_gen =  150 #150

open(file_stats, "w").close()

def exe_ROUGE():
	open("tempo"+which_tac+".txt", "w").close()
	cmds = "python3.6 ../Preparation/rouge.py " + fichier_sortie + " " + adress + " >> tempo"+which_tac+".txt"
	process = subprocess.Popen(cmds, stdout=subprocess.PIPE,shell=True)
	proc_stdout = (process.communicate()[0]).decode("utf-8")

	with open("tempo"+which_tac+".txt", "r") as file:
		lastline = (list(file)[-2])
		rouge_ = float(lastline[-8:-1])
	#the first output is the F measure for ROUGE 2 and the second is the complete output of ROUGE measure.
	return (rouge_, proc_stdout)

def write_to_stat(output, is_tempo):
	if not is_tempo:
		cmds = "echo " + output + " >> " + "stat_ws"+which_tac+".txt"
	else:
		cmds = "cat " + "stat_ws"+which_tac+".txt" + " tempo"+which_tac+".txt > tempo2"+which_tac+".txt" + " ; ""cat tempo2"+which_tac+".txt > " + "stat_ws"+which_tac+".txt"

	process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=True)

	return

def fill_out(output_file_name, phrases, ind_max):
	fp = open (output_file_name, "w")
	for p in phrases:
		if ind_max.phrase_presente(p):
			fp.write("1 ")
		else:
			fp.write("0 ")
	fp.write("\n")
	fp.close()
	return


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
		self.wd = calcJS.calcule_wd(self)
		self.mono = calcJS.calcule_monotonicity(self)
		self.monow = calcJS.calcule_monotonicity_w(self)
		

	def get_score(self):
		#return self.score
		return self.wd
	def get_wd(self):
		#return self.wd
		return self.score
	def get_mono(self):
		return self.mono
	def get_monow(self):
		return self.monow

	def print_indiv(self):
		print("Affichage individu : ")
		for p in self.phrases:
			print(p)
		print("score : "+str(self.get_score()))
		print("Fin Affichage individu")

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
			#if self.indivs[i1].get_wd() < self.indivs[i2].get_wd():
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
		iter = 0
		ind_max = Individu(self.phrases, self.taille_max, self.calcJS, method="copie", i1=self.get_max())
		#print ("0eme generation. "+str(len(self.indivs))+" individus. Score max : "+str(ind_max.get_score())+" wd : "+str(ind_max.get_wd())+" mono : "+str(ind_max.get_mono())+" monow : "+str(ind_max.get_monow()))
		fill_out(fichier_sortie, self.phrases,ind_max)

		print(iter)
		tempo = exe_ROUGE()
		roug_result = tempo[1]

		out = "0eme generation. "+str(len(self.indivs))+" individus. Score max : "+str(ind_max.get_score())+ " Rouge_2 F : " + str(tempo[0]) +" wd : "+str(ind_max.get_wd())+" mono : "+str(ind_max.get_mono())+" monow : "+str(ind_max.get_monow())
		write_to_stat(out, is_tempo= False)
		#write_to_stat(roug_result, is_tempo= True)


		for i in range(n_gen):
			iter += 1
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
			fill_out(fichier_sortie, phrases, ind_max)

			print(iter)
			tempo = exe_ROUGE()
			roug_result = tempo[1]

			outi = str(i+1)+"eme generation. "+str(len(self.indivs))+" individus. Score max : "+str(ind_max.get_score())\
				   + " Rouge_2 F : " + str(tempo[0]) + " wd : "+str(ind_max.get_wd())+" mono : "+str(ind_max.get_mono())+" monow : "+str(ind_max.get_monow())

			write_to_stat(outi, is_tempo=False)
			#write_to_stat(roug_result, is_tempo=True)

			#ind_max.print_indiv()
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
			#print(t)
			#if int(t) > 0 and cpt-3 < len(phrases):
			if cpt-3 < len(phrases):
				#print cpt-3
				#print(t)
				phrases[cpt-3]["tokens"][i] = int(t)
			i+=1
	elif cpt-3 >= len(phrases):
		print("Phrase surnumeraire")
	cpt += 1
fp.close()

#Creation de la population
population = Population(n_indivs, n_mutes, n_croises, n_aleas, n_mut, phrases, taille_max, fichier_source)
ind_max = population.optimise(n_gen)
fill_out(fichier_sortie, phrases, ind_max)





