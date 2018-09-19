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
Imax = 10    # Maximum current

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
        self.imax = self.get_imax()
        self.vmax = self.get_vmax()

    def __str__(self):
        # for printing
        s = "{} type,\t {} ft,\t {},\t {} amp,\t {} V"
        heater = self.htr.code
        length = str(round(self.l, 2)).rjust(5, '0')
        connection = self.conn
        imax = str(round(self.imax, 2)).rjust(5, '0')
        vmax = str(round(self.vmax, 2)).rjust(5, '0')
        return s.format(heater, length, connection, imax, vmax)

    def __repr__(self):
        return self.__str__()

    def get_imax(self):
        """ Get the max. current for given heater length connection"""
        pmaxlead = self.htr.maxWatt/f
        rlead = self.htr.ohmsPerFt*l
        nprls = condctbr[self.conn]
        imax = m.sqrt(pmaxlead/rlead) * nprls
        return imax

    def get_vmax(self):
        """ Get max. voltage for the given connection"""
        pmax = (self.htr.maxWatt/f) * condctp[self.conn]
        r = condctr[self.conn](self.htr.ohmsPerFt*self.l)
        vmax = m.sqrt(pmax*r)
        return vmax

    def check_vmax(self):
        """ CHecks if vmax is less than 60V"""
        if self.vmax <= Vmax:
            return True
        else:
            return False

    def check_imax(self):
        """Checks the maximum current 10amp"""
        if self.imax <= Imax:
            return True
        else:
            return False

    def check_vmax_imax(self):
        """ checks both imax and vmax"""
        return self.check_vmax() and self.check_imax()


def req_len(htr, cond):
    """ returns the required length of the heater for various conditions"""
    leaddissip = htr.maxWatt/f
    if cond==0:
        dissperlead = w/4.0
    elif cond==1:
        dissperlead = w/2.0
    return dissperlead/leaddissip


def length_sizing():
    """ Returns a list of possible heaters and corresponding connections"""
    phtrs = []
    for heater in hlist:
        for cond in [0,1]:
            reqlength = req_len(heater, cond)
            if l-tol <= reqlength <= l+tol:
                phtrs.append((heater, reqlength, cond))
    return phtrs


def possible_heaters():
    """ Returns The list of possible heaters sorted in order of voltage"""
    hconlist = []
    for details in length_sizing():
        heater = details[0]
        length = details[1]
        cond = details[2]
        if cond==0:
            for connection in cons[0:3]:
                heatercon = HtrConn(heater, length, connection)
                if heatercon.check_vmax_imax():
                    hconlist.append(heatercon)
        if cond==1:
            for connection in cons[3:5]:
                heatercon = HtrConn(heater, length, connection)
                if heatercon.check_vmax_imax():
                    hconlist.append(heatercon)
    hconlist.sort(key=lambda x: x.vmax, reverse=True)
    return hconlist

pp.pprint(possible_heaters())
