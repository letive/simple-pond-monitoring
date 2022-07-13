from lib.v2.shrimp_growth import ShrimpGrowth
from lib.v2.interpolation import Interpolate
import functools
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

class ParemeterEstimation:
    
    def __init__(self, df = None, path: str = None, sep: str =",", col_temp="temperature", col_uia="uionized_amonia", col_do="dissolveed_oxygen", col_doc="DOC"):
        if type(df) == pd.DataFrame:
            self.df = df
        else:
            self.df = pd.read_csv(path, sep=sep)
        
        self.wt_min_1 = 0
        self.biomass_min_1 = 0

        self.col_temp = col_temp
        self.col_uia = col_uia
        self.col_do = col_do
        self.col_doc = col_doc

    def set_data_for_interpolation(self,  df = None, path: str = None, sep: str =",", ):
        if type(df) == pd.DataFrame:
            self.data_biochem = df
        else:
            self.data_biochem = pd.read_csv(path, sep=sep)

    def set_conditional_parameter(self, cond_temp, cond_uia, cond_do, cond_csc):
        self.cond_temp = cond_temp
        self.cond_uia = cond_uia
        self.cond_do = cond_do
        self.cond_csc = cond_csc

    def set_biochem_interpolate_function(self, temperature: tuple, unionized_amonia: tuple, dissolved_oxygen: tuple):
        self.f_temperature = Interpolate(df=self.data_biochem).get_function(temperature[0], temperature[1], self.cond_temp)
        self.f_uia = Interpolate(df=self.data_biochem).get_function(unionized_amonia[0], unionized_amonia[1], self.cond_uia)
        self.f_do = Interpolate(df=self.data_biochem).get_function(dissolved_oxygen[0], dissolved_oxygen[1], self.cond_do)

    def set_food_availablelity_data(self, path=None, sep=","):
        if path:
            df = pd.read_csv(path, sep=sep)
        else:
            df = pd.DataFrame(
                {
                    "wt": ["1-3", "3-5", "5-7", "7-9", "9-11", "11-13", "13-15", "15-17", "17-30"],
                    "21-24": [0.08, 0.07, 0.065, 0.06, 0.055, 0.05, 0.045, 0.04, 0.03],
                    "24-28": [0.06, 0.05, 0.045, 0.04, 0.035, 0.03, 0.024, 0.025, 0.02],
                    "28-32": [0.07, 0.06, 0.055, 0.05, 0.045, 0.04, 0.035, 0.03, 0.025],
                }
            )

        self.fa_data = df


    def set_growth_paremater(self, w0, wn, n0, sr):
        self.w0 = w0
        self.wn = wn
        self.n0 = n0
        self.sr = sr
    
    def set_partial_harvest_parameter(self, doc, ph, final_doc=120):
        self.doc = doc
        self.ph = ph
        self.final_doc = final_doc

    def set_pond_data(self, area):
        self.area = area

    def __set_pass_condtion(self, wt, biomass):
        self.wt_min_1 = wt
        self.biomass_min_1 = biomass


    def __set_fr(self, t,  alpha):
        biochem = ShrimpGrowth.biochem_factor(t, self.df, self.cond_temp, self.cond_uia, self.cond_do, alpha[:3], self.col_temp, self.col_uia, self.col_do, self.col_doc)
        csc = ShrimpGrowth.csc_factor(self.biomass_min_1, self.area, self.cond_csc, alpha[3])
        fa = ShrimpGrowth.feed_availablelity_factor(self.wt_min_1, self.df.query("DOC == {}".format(t))[self.col_temp].values[0], self.fa_data, alpha[4])

        if (biochem == 0) or (csc == 0):
            self.fr = 0
        else: 
            self.fr = biochem + csc + fa


    @functools.lru_cache(maxsize=18000)
    def single_operation(self, t0, t, m, alpha, alpha2, alpha3, alpha4, alpha5, alpha6):
        self.__set_fr(t, (alpha2, alpha3, alpha4, alpha5, alpha6))
        weight = ShrimpGrowth.weight(t0, t, self.w0, self.wn, self.fr, alpha)
        population = ShrimpGrowth.population(t, self.n0, self.sr, m, self.ph, self.doc, self.final_doc)
        biomassa = weight * population
        self.__set_pass_condtion(weight, biomassa)      
        
        return weight, biomassa


    def multiple_operation(self, T, alpha, alpha2, alpha3, alpha4, alpha5, alpha6):
        m = -np.log(self.sr)/T[-1]
        res = np.asarray([self.single_operation(0, t, m, alpha, alpha2, alpha3, alpha4, alpha5, alpha6)[0] for t in T])
        return res

    
    def fit(self):
        alpha, alpha2, alpha3, alpha4, alpha5, alpha6 = curve_fit(self.multiple_operation, 
                                                    self.df["DOC"].tolist(), self.df["ABW"].tolist(),  
                                                    p0=[0.05, 0.05, 0.05,0.05, 0.05,0.05], method="dogbox", ftol=1e-05)[0]
        return alpha, alpha2, alpha3, alpha4, alpha5, alpha6

    