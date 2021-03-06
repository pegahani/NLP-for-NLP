import os
import re
import math
import sys
from scipy.stats import wasserstein_distance

class CalcJS:
	def __init__(self, fichier_source):
		self.delta = 0.0005
		fp = open (fichier_source, "r")
		self.dict_tokens_source = {}
		cpt = 0
		self.nb_tokens_source = 0
		for ligne in fp:
			if cpt > 2:
				ligne = ligne.rstrip()
				tab_tokens = ligne.split("\t")
				for i in range(len(tab_tokens)):
					if i in self.dict_tokens_source:
						self.dict_tokens_source[i] += int(tab_tokens[i])
					else:
						self.dict_tokens_source[i] = int(tab_tokens[i])
					self.nb_tokens_source += int(tab_tokens[i])
			cpt += 1	
		fp.close()

	def calcule_wd(self, indiv):
		dict_tokens_resume = indiv.tokens
		nb_tokens_resume = 0
		for t in dict_tokens_resume:
			nb_tokens_resume += dict_tokens_resume[t]


		taille_vocabulaire_source = len (self.dict_tokens_source)
		taille_vocabulaire_resume = len (dict_tokens_resume)
		#print(dict_tokens_resume)

		#Calcul des probabilites lissees
		self.probas_lissees_resume = self.probas_lissees (dict_tokens_resume, nb_tokens_resume, taille_vocabulaire_resume, self.delta)
		self.probas_lissees_source = self.probas_lissees (self.dict_tokens_source, self.nb_tokens_source, taille_vocabulaire_source, self.delta)
		#print self.probas_lissees_resume
		#print self.probas_lissees_source
		#return self.jensen_shannon (self.probas_lissees_resume, self.probas_lissees_source)
		return wasserstein_distance(list(self.probas_lissees_source.values()),list(self.probas_lissees_resume.values()))
		#return wasserstein_distance(list(self.dict_tokens_source.values()),list(dict_tokens_resume.values()))

	def calcule_js(self, indiv):
		dict_tokens_resume = indiv.tokens
		nb_tokens_resume = 0
		for t in dict_tokens_resume:
			nb_tokens_resume += dict_tokens_resume[t]


		taille_vocabulaire_source = len (self.dict_tokens_source)
		taille_vocabulaire_resume = len (dict_tokens_resume)
		#print(dict_tokens_resume)

		#Calcul des probabilites lissees
		self.probas_lissees_resume = self.probas_lissees (dict_tokens_resume, nb_tokens_resume, taille_vocabulaire_resume, self.delta)
		self.probas_lissees_source = self.probas_lissees (self.dict_tokens_source, self.nb_tokens_source, taille_vocabulaire_source, self.delta)
		#print self.probas_lissees_resume
		#print self.probas_lissees_source
		#self.wd=wasserstein_distance(self.probas_lissees_source.values(),self.probas_lissees_resume.values())
		#return self.jensen_shannon (self.probas_lissees_resume, self.probas_lissees_source)
		return self.jensen_shannon ()

	def calcule_monotonicity(self, indiv):
		dict_tokens_resume = indiv.tokens
		return self.pearson(self.dict_tokens_source,dict_tokens_resume)

	def calcule_monotonicity_w(self, indiv):
		dict_tokens_resume = indiv.tokens
		return self.pearson_weighted(self.dict_tokens_source,dict_tokens_resume)
		
	def kullback_leibler (self, probas1, probas2):
		kl = 0
		for token in probas1:
			kl += probas1[token] * math.log( probas1[token] / probas2[token] )
		return kl

	def jensen_shannon (self): 
		probas_moyenne = {}
		for token in self.probas_lissees_source: 
			#print("token"+str(token) + str(self.probas_lissees_source.keys()))
			probas_moyenne[token] = (self.probas_lissees_resume[token] + self.probas_lissees_source[token]) / 2
		#print("------"+str(self.probas_lissees_resume)+"----------")
		
		return self.kullback_leibler(self.probas_lissees_source, probas_moyenne) + self.kullback_leibler(self.probas_lissees_resume, probas_moyenne ) / 2

	def probas_lissees (self, dict_tokens, nb_tokens, taille_vocabulaire, delta ):
		probas = {}
		somme_probas = 0
		for token in dict_tokens:
			probas[token] = dict_tokens[token] + delta
			probas[token] = probas[token] / (nb_tokens + 1 *   delta * taille_vocabulaire)
			somme_probas += probas[token]
		#print "----------------Somme probas : "+str(somme_probas)+"----------------"
		return probas



	def pearson(self,dic1,dic2):
		ldec1 = sorted(dic1, key=dic1.get, reverse=True)
		#print(ldec1)
		ldec2 = sorted(dic2, key=dic2.get, reverse=True)
		#print(ldec2)
		#remplacer les valeurs de ldec2 par leur index dans ldec1
		indL1=[]
		for l2 in ldec2:
			indL1.append(ldec1.index(l2))
		#print(indL1)
		#compter le nombre d'inversions d'indexes
		count=0
		first = indL1.pop(0)
		index=0
		for l in indL1:
			#print("first:"+str(first)+",l:"+str(l))
			if first > l:
				count=count+1
			first = l
			index = index + 1
		return(count)

	def pearson_weighted(self,dic1,dic2):
		ldec1 = sorted(dic1, key=dic1.get, reverse=True)
		#print(ldec1)
		ldec2 = sorted(dic2, key=dic2.get, reverse=True)
		#print(ldec2)
		#remplacer les valeurs de ldec2 par leur index dans ldec1
		indL1=[]
		for l2 in ldec2:
			indL1.append(ldec1.index(l2))
		#print(indL1)
		#compter le nombre d'inversions d'indexes
		count=0
		first = indL1.pop(0)
		index=1
		for l in indL1:
			#print("first:"+str(first)+",l:"+str(l))
			if first > l:
				return l
				#count=count+index
			first = l
			index = index + 1
		return(count)



#out_ws.txt


#"python ../Genetic/algo_ge.py ../TAC/u08_corr/D0802/D0802-A/concat-D0802.txt out_ws.txt
#	python rouge.py out_ws.txt ../TAC/u08_corr/D0802 >> stat_ws.txt



