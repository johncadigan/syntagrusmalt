'''
Created on Nov 1, 2015

@author: john
'''
import subprocess
import malt_eval_wrapper
import sys
import os

class MaltWrapper(object):
    def __init__(self):
        self.malt_lib = 'malt/malt.jar'

    def train(self, in_train_file, out_model_file_name, f):
        subprocess_cmd = 'java -Xmx15G -jar {0} -c {1} -i {2} -if conllx -m learn {3} -l libsvm -lx ./libsvmc/svm-train -lo -t_1_-d_3'.format(self.malt_lib, out_model_file_name, in_train_file, f)
        malt = subprocess.Popen(subprocess_cmd.split())
        malt.communicate()

    def parse(self, in_test_file, in_model_file_name, out_result_file, f):
        subprocess_cmd = 'java -jar {0} -c {1} -i {2} -o {3} -m parse -a nivreeager %s'.format(self.malt_lib, in_model_file_name, in_test_file, out_result_file, f)    
        malt = subprocess.Popen(subprocess_cmd.split())
        return malt.communicate()[0]

def train_and_calculate_accuracy(in_train_filename, in_test_filename, out_model_name, feature):
    wrapper = MaltWrapper()
    f = ""
    if feature!=None:
        f= "-F {0}".format(feature)
    wrapper.train(in_train_filename, out_model_name, f)
    out_name = os.getcwd() + '/{0}_res.conll'.format(out_model_name)

    wrapper.parse(in_test_filename, out_model_name + '.mco', out_name, f)
    return out_name

if __name__=="__main__":
    if len(sys.argv) > 5:
        train_and_calculate_accuracy(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        train_and_calculate_accuracy(sys.argv[1], sys.argv[2], sys.argv[3], None)
     
    
