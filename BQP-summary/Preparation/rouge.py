"developer: pegah"

import os
import pathlib
import sys
import xml.etree.cElementTree as ET
from pathlib import Path
from subprocess import Popen, PIPE
import subprocess

#command line for executing rouge score
# python3.6 rouge.py 'output file ([0 1 0 1 1 0 0 0 ])' 'address to the TAC subject'
#python3.6 rouge.py out.txt ..	AC/u08_corr/D0827

path = os.getcwd() + 'TAC/u08/'
adress = "/home/pegah/Documents/research/DVRC/NLP-for-NLP/NLP-for-NLP/BQP-summary/Preparation/ROUGE-RELEASE-1.5.5"
adress_2 = "/home/pegah/Documents/research/DVRC/NLP-for-NLP/NLP-for-NLP/BQP-summary/TAC/u08_corr"

class rouge:

	def __init__(self, source_xml, decode_text):

		self.source_path = ''
		if source_xml[-1] == '/':
			self.source_path = source_xml
		else:
			self.source_path = source_xml + '/'

		topic = os.path.basename(source_xml)

		if topic == '':
			path_topic = pathlib.PurePath(source_xml)
			self.topic = path_topic.name
		else:
			self.topic = topic

		self.source_xml = self.source_path + self.topic + '-A/'

		self.name = "summary.txt"
		self.decode_text = decode_text
		self.result_text = None

	def BQNout_to_text(self):
		"""
		convert the input file to its summary by using the related concat.xml
		The generated summary is saved in the related folder of the subject.
		:return:
		"""

		F = open(self.decode_text, "r")
		output_file = open(self.source_path + "summary.txt" , 'w+')

		tempo = (F.read()).split(' ')
		vect = [int(i) for i in tempo if (i == '0' or i == '1')]

		tree = ET.parse(self.source_xml + "concat.xml")
		root = tree.getroot()

		counter = 0
		for child in root:
			if vect[counter] == 1:
				output_file.write(child.find('raw').text)
				output_file.write('\n')

			counter += 1

		output_file.close()

		self.result_text = self.source_path + self.name
		return

	def make_in_file(self, adress_ = None):

		"""
		this code generates a .in file (xml file) to be sent to the ROUGE method.
		:return:
		"""

		if adress_ is None:
			"gold standards summaries address"
			model_root = os.path.abspath(self.source_path) + '/summary'
			"proposed summary address"
			peer_root = os.path.abspath(self.source_path)

		else:
			model_root = adress_2 + '/summary'
			peer_root = adress_2

		file = peer_root + '/EvalResume.in'
		Path(file).touch()

		root = ET.Element("ROUGE_EVAL", version="1.5.5")
		eval = ET.SubElement(root, "EVAL", ID = self.topic)

		ET.SubElement(eval, "PEER-ROOT").text = peer_root
		ET.SubElement(eval, "MODEL-ROOT").text = model_root

		ET.SubElement(eval, "INPUT-FORMAT", TYPE = "SPL").text = " "

		peers = ET.SubElement(eval, "PEERS")

		summary = os.path.basename(self.result_text)
		ET.SubElement(peers, "P", ID = "72").text = summary

		models = ET.SubElement(eval, "MODELS")

		models_names = os.listdir(model_root)
		for m in models_names:
			ET.SubElement(models, "M", ID = m[-1]).text = m

		tree = ET.ElementTree(root)
		tree.write(file)

		return

	def compute_ROUGE(self, pathp = None):

		path_ = os.getcwd()
		print(self.source_path)
		in_file = os.path.abspath(self.source_path) + '/' + 'EvalResume.in'

		if pathp is None:
			#in_file = os.path.abspath(self.source_path) + '/' + 'EvalResume.in'
			cmds = 'cd ' + path_+"/ROUGE-RELEASE-1.5.5/" + " ; ""./runrouge_opt.sh " + in_file
		else:
			#in_file = pathp + '/' + 'EvalResume.in'
			cmds = 'cd ' + pathp + " ; ""./runrouge_opt.sh " + in_file

		process = subprocess.Popen(cmds, stdout=subprocess.PIPE, shell=True)
		proc_stdout = (process.communicate()[0]).decode("utf-8")

		print(proc_stdout)

		return


def main(arg1, arg2):

	# parse arguments using optparse or argparse or what have you
	r = rouge(source_xml= arg2, decode_text= arg1)
	r.BQNout_to_text()
	r.make_in_file()
	r.compute_ROUGE(adress)

if __name__ == '__main__':

	decode_text = sys.argv[1]
	source_xml = sys.argv[2]
	#topic = sys.argv[3]
	main(decode_text, source_xml)



