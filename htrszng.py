#!vim: fileencoding=utf-8
# Author: SaiChrla

import math as m
import argparse as arg
import pprint as pp


# input arguments
parser = arg.ArgumentParser()
parser.add_argument("w","watts", type=float, help="Required Wattage")
parser.add_argument("l","length", type=float, help="Required length in ft")
parser.add_argument("-t", "--tolerence", type=float, help="Length tolerence \
        default=0.5")
parser.add_argument("-f", "--factor", type=float, help="Factor of safety \
        default=1.5")
args = parser.parse_args()

# Assigning them as globals
w = args.w
l = args.l
if args.t:
    tol = args.t
else:
    tol = 0.5
if args.f:
    f = args.f
else:
    f = 1.5

Vmax = 60    # Maximum voltage

# Connection codes
cons = ['Series-Parallel', '4-lead-Series', '4-lead-Parallel',
        '2-lead-Parallel', '2-lead-Series']
conbr = [2, 1, 4, 2, 1]
condctbr = dict(zip(cons, conbr))
conr = [lambda x: x, lambda x: 4*x, lambda x: x/4.0, lambda x: x/2.0,
        lambda x: 2*x]
condctr = dict(zip(cons, conr))
conp = [4, 4, 4, 2, 2]
condctp = dict(zip(cons, conp))


class HtrType:
    """ This class creates the heater type objects with all necessary
    datails"""

    __init__(self, ohm, MaxWatt, code):
        """ Initiates a heater type"""
        self.ohmsPerFt = float(ohm)
        self.maxWatt = float(MaxWatt)
        self.leadCurrLim = m.sqrt(self.maxWatt/self.ohmPerFt)
        self.code = code


# Clayborn heater types
A = HtrType(1.9, 25, 'A')
B = HtrType(3.2, 25, 'B')
C = HtrType(4, 23, 'C')
D = HtrType(4.9, 20, 'D')
E = HtrType(7, 25, 'E')
F = HtrType(8.8, 23, 'F')
G = HtrType(10.8, 20, 'G')
H = HtrType(13.2, 20, 'H')
J = HtrType(21.3, 13, 'J')
K = HtrType(26.8, 10, 'K')


class HtrConn:
    """ This class creats opbjects for storing heater connection details"""

    __init__(self, htr, l, conn):
        """Instantiates the object with details"""
        self.htr = htr
        self.l = l
        self.conn = conn
        self.imax = get_imax(self.htr, self.l, self.conn)
        self.vmax = get_vmax(self.htr, self.l, self.conn)
        self.details = [self.htr.code, self.l, self.conn, self.imax, self.vmax]


def get_imax(htr, l, conn):
    """ Get the max. current for given heater length connection"""
    pmaxlead = htr.maxWatt/f
    rlead = htr.ohmPerFt*l
    nprls = condctbr[conn]
    imax = m.sqrt(pmaxlead/rlead) * nprls
    return imax


def get_vmax(htr, l, conn):
    """ Get max. voltage for the given connection"""
    pmax = (htr.maxWatt/f) * condctp[conn]
    r = condctr[conn](htr.ohmsPerft*l)
    vmax = m.sqrt(pmax*r)
    return vmax


