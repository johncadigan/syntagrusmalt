
import subprocess
import malt_wrapperm as m
from malt_eval_wrapper import MaltEvalWrapper as me
import sys
import glob
from time import sleep
import os

if __name__=="__main__":
    dir = sys.argv[1].strip()
    print os.environ
    while True:
        files = glob.glob("{0}/*.xml".format(dir))
        if len(files) > 0:
            name = files[0].split("/")[-1].split(".")[0]
            dev = "{0}/dev.conll".format(dir)
            res = m.train_and_calculate_accuracy("{0}/train.conll".format(dir), dev, name, files[0])
            eval = me()
            new_dir = "{0}/{1}".format(dir, name)
            cmd = 'mkdir {0}'.format(new_dir)
            subprocess.Popen(cmd.split())
            sleep(1)
            eval.calculate_accuracy(dev, res, new_dir)
            cmd = 'mv {0} {1} {2} {3}'.format(res, "{0}.mco".format(name), files[0], new_dir)
            subprocess.Popen(cmd.split())
        sleep(10)
            
