############################################################
##  Website: https://www.ncbi.nlm.nih.gov/snp/
##  Author: BessyHuang 2022.07.05
##  Topic: Web crawler on NCBI in order to get GeneName
############################################################

from collections import defaultdict
from bs4 import BeautifulSoup
import requests



SampleID = input('Please Enter SampleID\n> ')

Input_FilePath = '/Users/bessyhuang/Downloads/GeneSymbol-Tool/WebCrawler_NCBI_python/'
Input_FileName = 'PGS000018.txt'

Output_FilePath = '/Users/bessyhuang/Downloads/GeneSymbol-Tool/WebCrawler_NCBI_python/'
Output_FileName = '{}_with_GeneName.txt'.format(SampleID)


def request_URL(user_input):
	if ":" in user_input:
        	chrN, pos = user_input.split(":")
        	url = 'https://www.ncbi.nlm.nih.gov/snp/?term=' + chrN + '%3A' + pos
	else:
        	rsID = user_input
        	url = 'https://www.ncbi.nlm.nih.gov/snp/?term=' + rsID
	return url

def get_GeneName(soup):
	table =  soup.find('dl', attrs={'class':'snpsum_dl_left_align'})
	#print(table.string)
	try:
        	Field_Gene = soup.find(text='Gene:')
        	Value_GeneName = Field_Gene.findNext("dd").text
        
        	Value_GeneName = Value_GeneName.replace(' (Varview)\n', '')
	except:
        	Value_GeneName = "No Gene Name"

	#print('==>', Field_Gene, ':', Value_GeneName)
	return Field_Gene, Value_GeneName

def get_SNP_chr_pos_dict(SampleID, content):
	# SampleID : { 'chr_pos': '1:2245570', {'rsID': 'rs2843152', 'effect_allele': 'G', 'other_allele': 'C', 'effect_weight': -2.76009e-02, 'GeneName': 'xxx'} }
	SNP_chr_pos_dict = defaultdict(lambda: defaultdict(lambda: defaultdict()))
	header = []

	for line in content:
		if '#' in line:
			pass
		elif ('chr_name' in line) and ('chr_position' in line):
			f1, f2, f3, f4, f5, f6 = line.split('\t')
			header = [f1, f2, f3, f4, f5, f6, 'GeneName']
		else:
			split_line = line.split('\t')
			chr_pos = '{}:{}'.format(split_line[1], split_line[2])
			SNP_chr_pos_dict[SampleID][chr_pos][f1] = split_line[0]
			SNP_chr_pos_dict[SampleID][chr_pos][f4] = split_line[3]
			SNP_chr_pos_dict[SampleID][chr_pos][f5] = split_line[4]
			SNP_chr_pos_dict[SampleID][chr_pos][f6] = split_line[5]

			#2 Query GeneName from NCBI website
			url = request_URL(chr_pos)
			response = requests.get(url)
			soup = BeautifulSoup(response.text, 'html.parser')
			Field_Gene, Value_GeneName = get_GeneName(soup)

			SNP_chr_pos_dict[SampleID][chr_pos]['GeneName'] = Value_GeneName
	return SNP_chr_pos_dict, header

def get_SNP_rsID_dict(SampleID, content):
	# SampleID : { 'rs646776' : {'effect_allele': 'T', 'effect_weight': 0.174, 'allelefrequency_effect': 0.77, 'locus_name': '1p13.3 (SORT1)', 'OR': 1.19, 'GeneName': 'xxx'} }
	SNP_rsID_dict = defaultdict(lambda: defaultdict(lambda: defaultdict()))
	header = []

	for line in content:
		if '#' in line:
			pass
		elif 'rsID' in line:
			f1, f2, f3, f4, f5, f6 = line.split('\t')
			header = [f1, f2, f3, f4, f5, f6, 'GeneName']
		else:
			split_line = line.split('\t')
			rsID = split_line[0]
			SNP_rsID_dict[SampleID][rsID][f2] = split_line[1]
			SNP_rsID_dict[SampleID][rsID][f3] = split_line[2]
			SNP_rsID_dict[SampleID][rsID][f4] = split_line[3]
			SNP_rsID_dict[SampleID][rsID][f5] = split_line[4]
			SNP_rsID_dict[SampleID][rsID][f6] = split_line[5]

			#2 Query GeneName from NCBI website
			url = request_URL(rsID)
			response = requests.get(url)
			soup = BeautifulSoup(response.text, 'html.parser')
			Field_Gene, Value_GeneName = get_GeneName(soup)

			SNP_rsID_dict[SampleID][rsID]['GeneName'] = Value_GeneName
	return SNP_rsID_dict, header


#1 Input TXT FILE and send to NCBI website
with open(Input_FilePath + Input_FileName, 'r') as f_in:
	content = [ line.strip() for line in f_in.readlines() ]
	for line in content:
		if ('chr_name' in line) and ('chr_position' in line):
			TXT_input_type = 'chr:pos'
			break
		elif 'rsID' in line:
			TXT_input_type = 'rsID'
			break
	if TXT_input_type == 'chr:pos':
		SNP_chr_pos_dict, chr_pos_header = get_SNP_chr_pos_dict(SampleID, content)
	elif TXT_input_type == 'rsID':
		SNP_rsID_dict, rsID_header = get_SNP_rsID_dict(SampleID, content)


with open(Output_FilePath + Output_FileName, 'w') as f_out:
	if TXT_input_type == 'chr:pos':
		f1, f2, f3, f4, f5, f6, f7 = chr_pos_header
		f_out.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(f1, f2, f3, f4, f5, f6, f7))
		for key in SNP_chr_pos_dict[SampleID]:
			v2, v3 = key.split(':')
			v1, v4, v5, v6, v7 = SNP_chr_pos_dict[SampleID][key].values()
			f_out.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(v1, v2, v3, v4, v5, v6, v7))
	elif TXT_input_type == 'rsID':
		f1, f2, f3, f4, f5, f6, f7 = rsID_header
		f_out.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(f1, f2, f3, f4, f5, f6, f7))
		for key in SNP_rsID_dict[SampleID]:
			v1, v2, v3, v4, v5, v6 = SNP_rsID_dict[SampleID][key].values()
			f_out.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(key, v1, v2, v3, v4, v5, v6))