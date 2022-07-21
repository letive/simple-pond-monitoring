from re import L
from lib.v2.shrimp_growth import ShrimpGrowth
from lib.v2.interpolation import Interpolate
import functools
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

class ParemeterEstimation:
    
    def __init__(self, df = None, path: str = None, sep: str =",", 
            col_temp="temperature", col_uia="unionized_amonia", col_do="dissolveed_oxygen", 
            col_doc="DOC", col_abw="ABW"):

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
        self.col_abw = col_abw

    def set_data_for_interpolation(self,  df = None, path: str = None, sep: str =","):
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

    # def __set_fr_params(self, csc, fa):
    #     self.csc = csc
    #     self.fa = fa

    def __set_fr(self, index,  alpha, m=1):
        temperature, nh4, do = ShrimpGrowth.biochem_factor(index, self.df, self.cond_temp, self.cond_uia, self.cond_do, self.col_temp, self.col_uia, self.col_do, self.col_doc)
        
        if (temperature == 0) or (nh4 == 0) or (do == 0):
            self.__is_in_condition = False
        else:

            self.__is_in_condition = True

        # self.fr = alpha[0] * temperature + alpha[1] * nh4 + alpha[2] * do

        self.temperature = (temperature, alpha[0] * temperature)
        self.nh4 = (nh4, alpha[1] * nh4)
        self.do = (do, alpha[1] * do)

    @functools.lru_cache(maxsize=18000)
    def single_operation(self, t0, index, t, m, alpha, alpha2, alpha3, alpha4):
        if t == 0:
            self.__set_pass_condtion(0, 0)
            
        self.__set_fr(index, (alpha2, alpha3, alpha4), m=m) # ini

        temperature = self.temperature
        nh4 = self.nh4
        do = self.do

        weight = ShrimpGrowth.weight(t0, t, self.w0, self.wn, 0, alpha)

        # if self.__is_in_condition:
        #     weight = ShrimpGrowth.weight(t0, t, self.w0, self.wn, self.fr, alpha)
        # else:
        #     weight = ShrimpGrowth.weight_out_condition(t0, t, self.w0, self.wn, self.fr, alpha)
        
        population = ShrimpGrowth.population(t, self.n0, self.sr, m, self.ph, self.doc, self.final_doc)
        biomassa = weight * population
        self.__set_pass_condtion(weight, biomassa)    # ini
        
        return weight, biomassa

   

    def multiple_operation(self, T, alpha, alpha2, alpha3, alpha4):
        m = -np.log(self.sr)/self.df[self.col_doc].max()

        res = np.asarray([self.single_operation(0, t[1], t[0], m, alpha, alpha2, alpha3, alpha4)[0] for t in enumerate(T)])
        return res
    
    def fit(self):
        alpha, alpha2, alpha3, alpha4 = curve_fit(self.multiple_operation, 
                                                    self.df[self.col_doc].tolist(), self.df[self.col_abw].tolist(),  
                                                    p0=[0.05, 0.05, 0.05, 0.05], method="lm", ftol=1e-05)[0]
        return alpha, alpha2, alpha3, alpha4


    @functools.lru_cache(maxsize=18000)
    def single_operation_v2(self, t0, t, alpha, alpha2, alpha3, alpha4):
        temperature, nh4, do = ShrimpGrowth.biochem_factor(t, self.df, self.cond_temp, self.cond_uia, self.cond_do, self.col_temp, self.col_uia, self.col_do, self.col_doc)
        if (temperature == 0) or (nh4 == 0) or (do == 0):
            weight = ShrimpGrowth.weight(t0, t, self.w0, self.wn, alpha2*temperature+alpha3*nh4+alpha4*do, alpha)    
        else:
            weight = ShrimpGrowth.weight(t0, t, self.w0, self.wn, alpha2*temperature+alpha3*nh4+alpha4*do, alpha)
        return weight, 0

    def multiple_operation_v2(self, T, alpha, alpha2, alpha3, alpha4):
        m = -np.log(self.sr)/self.df[self.col_doc].max()
        res = np.asarray([self.single_operation_v2(0, t[1], alpha, alpha2, alpha3, alpha4)[0] for t in enumerate(T)])
        return res
    
    def fit_v2(self):
        alpha = curve_fit(self.multiple_operation_v2, self.df[self.col_doc].tolist(), self.df[self.col_abw].tolist())[0]
        self.alpha = alpha
        return alpha

    def mse(self):
        alpha, alpha2, alpha3, alpha4 = self.alpha
        data = []
        for i in self.df.iterrows():
            data.append((i[1][self.col_abw] - self.single_operation_v2(0, i[1][self.col_doc], alpha, alpha2, alpha3, alpha4))**2)
    
        return np.mean(data)