import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from scipy.integrate import quad

def normal_trapezoidal(m, suitable_min, suitable_max, optimal_min, optimal_max):
    """
    m: value in t
    """
    if np.isnan(m):
        ret = 0.25
    elif m < suitable_min:
        ret = 0 
    elif m > suitable_max:
        ret = 0
    else:
        ret = min(((m-suitable_min)/(optimal_min-suitable_min), 1, (suitable_max-m)/(suitable_max-optimal_max)))
        
    return ret

def left_trapezoidal(m, suitable_min, suitable_max, optimal_max):
    """
    m: value in t
    """
    if np.isnan(m):
        ret = 0.25
    elif m < suitable_min:
        ret = 0
    elif m > suitable_max:
        ret = 0
    else:
        ret = min((1, (suitable_max-m)/(suitable_max-optimal_max)))

    return ret

def source_data(**kwargs):
    chem = pd.read_csv("data/data_chemical_v2.csv")
    bio = pd.read_csv("data/data_sample - biological.csv")

    doc = chem["Doc"].tolist()
    
    score_uia = []
    score_o2 = []
    score_temp = []


    for i in doc:
        score_uia.append(left_trapezoidal(chem[chem["Doc"] == i]["uia"].values[0],
                            kwargs["ua_suitable_min"], kwargs["ua_suitable_max"], kwargs["ua_optimal_max"]))
        
        score_o2.append(normal_trapezoidal(bio[bio["DOC"] == i]["DO_s"].values[0],
                            kwargs["do_suitable_min"], kwargs["do_suitable_max"],
                            kwargs["do_optimal_min"], kwargs["do_optimal_max"]))
        
        score_temp.append(normal_trapezoidal(bio[bio["DOC"] == i]["Suhu_s"].values[0],
                            kwargs["temp_suitable_min"], kwargs["temp_suitable_max"],
                            kwargs["temp_optimal_min"], kwargs["temp_optimal_max"]))

        # score_csc.append(left_trapezoidal(kwargs["biomasss"]/kwargs["volume"], 
        #                     kwargs["csc_suitable_min"], kwargs["csc_suitable_max"],
        #                     kwargs["csc_optimal_min"], kwargs["csc_optimal_max"]))

    
    # score_csc = left_trapezoidal(kwargs["biomass"]/kwargs["volume"], 
    #                         kwargs["csc_suitable_min"], kwargs["csc_suitable_max"], kwargs["csc_optimal_max"])

    f_uia = CubicSpline(doc, score_uia)
    f_o2 = CubicSpline(doc, score_o2)
    f_temp = CubicSpline(doc, score_temp)

    return f_uia, f_o2, f_temp

class Fungsi:
    def __init__(self, a, b, f_uia, f_o2, f_temp, score_csc):

        self.a = a
        self.b = b

        self.f_uia = f_uia
        self.f_o2 = f_o2
        self.f_temp = f_temp

        self.score_csc = score_csc

    def _integrate_function(self, t):
        if any((self.f_temp(t) == 0, self.f_o2(t) == 0, self.f_uia(t) == 0)):
            return 0
        else:
            return self.f_temp(t) + self.f_o2(t) + self.f_uia(t) + self.score_csc

    def get_integral(self):
        return quad(self._integrate_function, self.a, self.b, epsabs = 1e-4, limit=1000)

from lib.helpers import heaviside_step

class baseBiomass:
    def __init__(self, t0, t, wn, w0, alpha, n0: int, sr: float, m: float, 
        ph: list, doc: list, f_uia, f_o2, f_temp, score_csc, final_doc:int = 120):
        self.t0 = t0
        self.t = t
        self.wn = wn
        self.w0 = w0
        self.alpha = alpha
        self.n0 = n0
        self.sr = sr
        self.m = m
        self.ph = ph
        self.doc = doc
        self.final_doc = final_doc

        # self.biomassa_n_1 = biomass_n_1
        # self.area = area

        self.f_uia = f_uia
        self.f_o2 = f_o2
        self.f_temp = f_temp
        self.score_csc = score_csc


    def _fr(self):
        return Fungsi(self.t0, self.t, self.f_uia, self.f_o2, self.f_temp, self.score_csc).get_integral()[0]

    def wt(self):
        return (self.wn**(1/3) - (self.wn**(1/3) - self.w0**(1/3)) * np.exp(-self.alpha * self._fr()))**3

    def population(self):
        partial_harvest = []
        for i, j in enumerate(self.doc):
            partial_harvest.append(self.ph[i] * heaviside_step(self.t - j))

        if self.t >= self.final_doc:           
            partial_harvest.append((self.sr - sum(self.ph)) * heaviside_step(self.t - self.final_doc))
        
        result = self.n0 * (np.exp(-self.m * self.t) - sum(partial_harvest))
        return result

    def biomassa(self):
        # biomassa in gram
        result = self.wt() * self.population()
        return result