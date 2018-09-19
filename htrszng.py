#!vim: fileencoding=utf-8
# Author: SaiChrla

import math as m
import argparse as arg
import pprint as pp


# input arguments
parser = arg.ArgumentParser()
parser.add_argument("watts", type=float, help="Required Wattage")
parser.add_argument("length", type=float, help="Required length in ft")
parser.add_argument("-t", "--tolerence", type=float, help="Length tolerence \
        default=0.5")
parser.add_argument("-f", "--factor", type=float, help="Factor of safety \
        default=1.5")
args = parser.parse_args()

# Assigning them as globals
w = args.watts
l = args.length
if args.tolerence:
    tol = args.tolerence
else:
    tol = 0.5
if args.factor:
    f = args.factor
else:
    f = 1.5

Vmax = 60    # Maximum voltage

# Connection codes
cons = ['Series-Parallel', '4-lead-Series  ', '4-lead-Parallel',
        '2-lead-Parallel', '2-lead-Series  ']
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

    def __init__(self, ohm, MaxWatt, code):
        """ Initiates a heater type"""
        self.ohmsPerFt = float(ohm)
        self.maxWatt = float(MaxWatt)
        self.leadCurrLim = m.sqrt(self.maxWatt/self.ohmsPerFt)
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
hlist = [A, B, C, D, E, F, G, H, J, K]


class HtrConn:
    """ This class creats opbjects for storing heater connection details"""

    def __init__(self, htr, l, conn):
        """Instantiates the object with details"""
        self.htr = htr
        self.l = l
        self.conn = conn
        self.imax = get_imax(self.htr, self.l, self.conn)
        self.vmax = get_vmax(self.htr, self.l, self.conn)
        self.details = [self.htr.code, self.l, self.conn, self.imax, self.vmax]

    def __str__(self):
        # for printing
        s = "{} type,\t {} ft,\t {},\t {} amp,\t {} V"
        heater = self.htr.code
        length = str(round(self.l,2)).rjust(2, '0')
        connection = self.conn
        imax = str(round(self.imax, 2)).rjust(2, '0')
        vmax = str(round(self.vmax, 2)).rjust(2, '0')
        return s.format(heater, length, connection, imax, vmax)

    def __repr__(self):
        return self.__str__()




def get_imax(htr, l, conn):
    """ Get the max. current for given heater length connection"""
    pmaxlead = htr.maxWatt/f
    rlead = htr.ohmsPerFt*l
    nprls = condctbr[conn]
    imax = m.sqrt(pmaxlead/rlead) * nprls
    return imax


def get_vmax(htr, l, conn):
    """ Get max. voltage for the given connection"""
    pmax = (htr.maxWatt/f) * condctp[conn]
    r = condctr[conn](htr.ohmsPerFt*l)
    vmax = m.sqrt(pmax*r)
    return vmax

def check_vmax(htr, l, conn):
    """ CHecks if vmax is less than 60V"""
    vmax = get_vmax(htr, l, conn)
    if vmax <= 60:
        return True
    else:
        return False

def req_len(w, htr, cond):
    """ returns the required length of the heater for various conditions"""
    leaddissip = htr.maxWatt/f
    if cond==0:
        dissperlead = w/4.0
    elif cond==1:
        dissperlead = w/2.0
    return dissperlead/leaddissip


phtrs = []
for heater in hlist:
    for cond in [0,1]:
        reqlength = req_len(w, heater, cond)
        if l-tol <= reqlength <= l+tol:
            phtrs.append((heater, reqlength, cond))


phcons = []
for pht in phtrs:
    if pht[2]==0:
        for connection in cons[0:3]:
            if check_vmax(pht[0], pht[1], connection):
                phcons.append((pht[0], pht[1], connection))
        for connection in cons[3:5]:
            if check_vmax(pht[0], pht[1], connection):
                phcons.append((pht[0], pht[1], connection))


htrcons = []
for phcon in phcons:
    htr = phcon[0]
    l = phcon[1]
    conn = phcon[2]
    hcon = HtrConn(htr, l, conn)
    htrcons.append(hcon)

pp.pprint(htrcons)
