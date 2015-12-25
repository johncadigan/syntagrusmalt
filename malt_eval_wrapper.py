'''
Created on Nov 1, 2015

@author: john
'''
import subprocess
import re
import glob


class MaltEvalWrapper(object):
    def __init__(self):
        self.malt_eval_lib = 'meval/lib/MaltEval.jar'
        self.malt_evals = glob.glob("meval/evalpl_comparison/*.xml")
        
    def calculate_accuracy(self, in_auto_result, in_gold_result, to_dir):
        for x in self.malt_evals:
            name = x.split("/")[-1].split(".")[0]
            wf = open("{0}/{1}.txt".format(to_dir, name), "wb")
            cmd = "java -jar {0} -e {1} -s {2} -g {3}".format(self.malt_eval_lib, x, in_auto_result, in_gold_result)
            out = subprocess.check_output(cmd, shell=True)
            wf.write(out)
