import re
import os
import natsort
import pandas
import sys
#file = '/Volumes/PD-SDD/PP-XAFS_AsakuraLab/2013June16_NW14A/2013June22_9A/W_FEFF/paths.dat'

def read_FEFF(path_to_feff):
    #print path_to_feff+'/paths.dat'
    f = open(os.path.dirname(path_to_feff)+'/paths.dat','r')
    sign = 'pass'
    dict = {}
    route = ''
    path_info =[]
    for line in f:
        match_line = re.match(r"\s+(\d+)\s+(\d)\s+\d+\.\d+\s+index\,\s+nleg\,\s+degeneracy\,\s+r=\s+(\d+\.\d+)",line)
        match_xyz = re.match(r"\s+x\s+y\s+z\s+.*",line)
        match_data = re.search("\s+'\w+\s+'",line)
        if (sign =='read' or 'pass') and match_line != None:
            if match_line.group(1) =='1':
                path_info.append(['path_'+match_line.group(1),'r = ' + match_line.group(3)])
                #print path_info
            else:
                dict[path_info[int(match_line.group(1))-2][0]] = [route, path_info[int(match_line.group(1))-2][1]]
                path_info.append(['path_'+match_line.group(1),'r = ' + match_line.group(3)])
            route = ''
            sign = 'pass'
        elif sign =='pass' and match_xyz != None:
            #print line.rstrip()
            sign = 'read'
        elif sign == 'read' and match_data != None:
            if re.match("\w+",route):
                route = '-' + route
            route = match_data.group().replace("'","").replace(" ","") + route
    dict[path_info[-1][0]] = [route, path_info[-1][1]]
    #print natsort.natsorted(dict.keys())
    txt_array = {}
    for key in natsort.natsorted(dict.keys()):
        #print key
        str_ = "{:16s}{:16s}{:16s}".format(key+':', dict[key][0]+': ', dict[key][1]+': ')
        txt_array[key] = str_
    #for txt in txt_array:
    #    print txt
    list_file = os.path.dirname(path_to_feff)+'/list.dat'
    feffrun = os.path.dirname(path_to_feff)+'/feff.run'
    if os.path.isfile(list_file):
        rNames = ['pathindex','sig2','amp ratio','deg','nlegs','r effective']
        df = pandas.DataFrame()
        if sys.platform == 'win32':
            df = pandas.read_csv(list_file,delimiter=r"\s+",skiprows=3,names=rNames)
        else:
            df = pandas.read_csv(list_file,delim_whitespace=True,skiprows=3,names=rNames)
        #print len(df['amp ratio'].as_matrix())
        for i in range(0,len(df['amp ratio'].as_matrix())):
            #print df['amp ratio'][i]
            txt_array['path_'+str(df['pathindex'][i])] += "{:16s}".format(str(df['amp ratio'][i])) + "{:16s}".format(str(df['deg'][i]))
        return txt_array
    elif os.path.isfile(feffrun):
        f = open(feffrun,'r')
        for line in f:
            if re.search("(\s+|\t+)(\d+)(\s+|\t+)(\d+\.\d+)(\s+|\t+)(\d+\.\d+)(\s+|\t+)(\d+)(\s+|\t+)(\d+\.\d+)",line.rstrip()):
                # t_array =re.split("\s+",line.rstrip())
                #print t_array
                #i = 0
                # while i < len(t_array):
                #     if t_array[i] == '':
                #         t_array.pop(i)
                #     i += 1
                path_num = re.search("(\s+|\t+)(\d+)(\s+|\t+)(\d+\.\d+)(\s+|\t+)(\d+\.\d+)(\s+|\t+)(\d+)(\s+|\t+)(\d+\.\d+)",line.rstrip()).group(2)
                amp = re.search("(\s+|\t+)(\d+)(\s+|\t+)(\d+\.\d+)(\s+|\t+)(\d+\.\d+)(\s+|\t+)(\d+)(\s+|\t+)(\d+\.\d+)",line.rstrip()).group(4)
                degen = re.search("(\s+|\t+)(\d+)(\s+|\t+)(\d+\.\d+)(\s+|\t+)(\d+\.\d+)(\s+|\t+)(\d+)(\s+|\t+)(\d+\.\d+)",line.rstrip()).group(6)
                # print path_num
                # print amp
                # print degen
                txt_array['path_'+path_num] += "{:16s}".format(amp) + "{:16s}".format(degen)
        # print txt_array
        return txt_array



if __name__=="__main__":
    file = raw_input('Specify the path to feff.inp: ')
    read_FEFF(file)