import os
import sys
import numpy as np
from datetime import datetime
import math

data_folder = './data'
filelist = os.listdir(data_folder)
filelist = filter(lambda x: len(x) > 4 and x[-4:] == '.csv', filelist)

stock_filelist = filter(lambda x: x != x.lower() and x[:3] != 'GST' and x != 'OIL.csv', filelist)
oil_file = os.path.join(data_folder, 'OIL.csv')

stock_filelist = map(lambda x: os.path.join(data_folder, x), stock_filelist)

def read_csv(filename):
	''' Given a filename, read the file and return a matrix of 4 columns: 
	date (in integer), open, close, volumn
	Each unavailable data is represented using -1
	only used for stock price and oil price
	'''
	print('Reading '+filename)
	fin = open(filename, 'r')
	line = fin.readline().strip().lower()
	attributes = line.split(',')
	kept = []
	kept_attrs = ['date']
	for ind in xrange(len(attributes)):
		att = attributes[ind] 
		if att in ('open', 'close', 'volume', 'value'):
			kept.append(ind)
			kept_attrs.append(att)
	data = []
	line = fin.readline()
	while len(line) > 0: 
		str_split = line.strip().split(',')
		linedata = []
		linedata.append(datetime.strptime(str_split[0], '%Y-%m-%d').toordinal())
		for ind in kept: 
			value = -1
			try:
				value = float(str_split[ind])
			except ValueError:
				pass
				# print(str_split[ind])
			linedata.append(value)


		data.append(linedata)
		line = fin.readline()
	data = np.array(data)
	return data

def align_old(data1, data2, index1=1,index2=1,eps=0.001,threshold=0):
	# reverse if necessary
	data1 = data1[data1[:,0].argsort()]
	data2 = data2[data2[:,0].argsort()]

	res = np.zeros((min(data1.shape[0], data2.shape[0]),3))
	ind = 0
	ind1 = 0 
	ind2 = 0
	while ind1 < data1.shape[0] and ind2 < data2.shape[0]:
		if data1[ind1][0] - data2[ind2][0] > eps:
			ind2 += 1
		elif data1[ind1][0] - data2[ind2][0] < -eps:
			ind1 += 1
		else:
			res[ind][0] = data1[ind1][0]
			res[ind][1] = data1[ind1][index1]
			res[ind][2] = data2[ind2][index2]
			ind += 1
			ind1 += 1
			ind2 += 1
	res = res[:ind,:]
	# remove unavailable ones
	res = res[((res >= threshold).sum(1) == 3)]
	return res

def align(datas, index=1,eps=0.001,threshold=0):
	# reverse if necessary
	datas = [x[x[:,0].argsort()] for x in datas]

	ind = 0
	inds = np.zeros(len(datas)).astype('int')
	maxinds = np.array([x.shape[0] for x in datas])
	res = np.zeros((int(math.ceil(maxinds.min())),1+len(datas)))

	while (inds < maxinds).all():
		cur_time = map(lambda i: datas[i][inds[i]][0], range(len(datas)))
		if min(cur_time) == max(cur_time):
			res[ind][0] = datas[0][inds[0]][0]
			for i in xrange(len(datas)):
				res[ind][i+1] = datas[i][inds[i]][index]
			ind += 1
			inds = inds + 1
		else:
			max_time = max(cur_time)
			for i in xrange(len(datas)):
				if cur_time[i] < max_time: 
					inds[i] += 1

	res = res[:ind,:]
	# remove unavailable ones
	res = res[((res >= threshold).sum(1) == 1+len(datas))]
	return res

def get_data(filenames):
	datas = []
	for filename in filenames:
		datas.append(read_csv(filename))
	res = align(datas)
	return res

## test 
# print stock_filelist
# res = get_data(stock_filelist[0], oil_file)
# data, att = read_csv(stock_filelist[1])


