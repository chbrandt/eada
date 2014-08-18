#!/usr/bin/env python

import sys
import logging

import math

# Near-UV, optical, IR
filters = {
    # name : [central wavelength, ]
    'U' : [3550, 1810],
    'B' : [4400, 4260],
    'V' : [5500, 3640],
    'R' : [6400, 3080],
    'I' : [7900, 2550],
    'Y' : [10000, 2125],
    'J' : [12600, 1600],
    'H' : [16500, 1020],
    'K' : [22200, 657]
}

# Cardelli et al. 1989 ApJ 345, 245

def absorption(nh,band):
    """
    """

    logging.debug("Filter being used: %s",band)
    lmb = filters[band][0]
    logging.debug("--> wavelength: %f [angstrons]",lmb)

    logging.debug("nh: %f",nh)
    
    Rv = 3.1
    av = Rv * (-0.055 + nh * 1.987e-22)
    logging.debug("Computed av: %f",av)
    av = av if av > 0 else 0
    logging.debug("Used av: %f",av)
    
    # lambda from Amstrongs to microns
    lmb = lmb/10000.0
    a = 0.574 / (lmb**1.61)
    logging.debug("a(lmb): %f",a)
    b = 0.527 / (lmb**1.61)
    logging.debug("b(lmb): %f",b)
    a_band=(a - b / Rv) * av
    logging.debug("Absorption value: %f",a_band)
    
    return a_band

# --

def extinction(nh,band,m_band,mErr_band):
    """
    """

    if band not in filters.keys():
        logging.error("Filter '%s' is not recognised.")
        return False

    a_band = absorption(nh,band)
    
    lmb = filters[band][0] # angstroms
    frequency = 3.e10 / (lmb / 1.e8) # [cm/s / cm]
    logging.debug("Frequency: %e",frequency)
    
    K = filters[band][1]
    logging.debug("--> K const: %e",K)

    cte = math.log(K,10) - 23
    logging.debug("Magnitude zero: %e",cte)

    flux = 10.**(-0.4 * (m_band - a_band) + cte) * frequency
    logging.debug("Flux: %e",flux)
    
    err = 10.**(-0.4 * (m_band - mErr_band - a_band) + cte) * frequency - flux
    logging.debug("Flux error: %e",err)
    
    a_=1.0
    print "Frequency   dummyErr   Flux   FluxErr"
    print "%.5e  %.1f     %.5e   %.5e" % (frequency,a_,flux,err)
    
    return flux,err
    
# --

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('nh', type=float,
                        help='Reference frequency')
    parser.add_argument('mag', type=float,
                        help='Magnitude at the given filter')
    parser.add_argument('magErr', type=float,
                        help='Magnitude error at the given filter')
    parser.add_argument('band',
                        help='Band/filter being used. Opions are: U, B, V, R, I, J, H, K.')
    
    args = parser.parse_args()
    
    logging.basicConfig(filename='dereddening.log', filemode='w',
                        format='%(levelname)s:%(message)s', level=logging.DEBUG)

    flux,err = extinction(args.nh,args.band,args.mag,args.magErr)
    
    sys.exit(0)
