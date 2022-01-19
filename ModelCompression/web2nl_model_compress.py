#!/usr/bin/env python

import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-f", "--file", dest="mfile",
                  help="SVM input file", metavar="FILE")
parser.add_option("-o", "--outfile", dest="ofile",
                  help="Output file", metavar="FILE")
parser.add_option("-d", "--digits", dest="ndigits",
                  help="Number of significant digits for floating point numbers", metavar="FILE")
(options, args) = parser.parse_args()

mfile = options.mfile

ofp = sys.stdout
if options.ofile is not None:
    ofp = open(options.ofile, 'w')

ndigits = 8
if options.ndigits is not None:
    ndigits = int(options.ndigits)

in_features = False
with open(mfile, 'rb') as sfp:
     for line in sfp:
         if in_features:
             parts = line.split(',')
             #print line
             if len(parts) >= 2:
                 weights = []
                 for ent in parts[2:]:
                     (i, f) = ent.split(':')
                 #approximate before truncating
                     x = round(float(f), ndigits)
                     if(x != float(0)):
                         fstr = "%." + str(ndigits) + "f"
                         xs = fstr % x
                         weights.append("%s:%s" % (i, xs))
                 if len(weights):
                   ofp.write("%s,%s,%s\n" % (parts[0],parts[1],','.join(weights)))
             else:
                 ofp.write(line)
         else:
             ofp.write(line)
             if line.startswith("[Feats,"):
                 in_features = True
sfp.close()
