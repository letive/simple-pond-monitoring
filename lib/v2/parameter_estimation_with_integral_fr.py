from lib.v2.shrimp_growth_v2 import ShrimpGrowth
import functools
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import CubicSpline
from lib.helpers import get_cycle_data, generate_spline_function, generate_interpolate_function

class ParemeterEstimation:
    
    def __init__(self, df = None, path: str = None, sep: str =",", 
            col_temp="temperature", col_uia="unionized_amonia", col_do="dissolveed_oxygen", 
            col_doc="DOC", col_abw="ABW", col_adg="ADG"):

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

    def set_temperature_interpolation(self):
        X = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0],
            [7, 0], [8, 0], [9, 0], [10, 0], [11, 0], [12, 0], [13, 0], 
            [14, 0], [15, 0], [16, 0], [17, 0.001], [18, 0.002], [19, 0.004], 
            [20, 0.005],[21, 0.0055], [22, 0.006], [23, 0.0065], [24, 0.007], 
            [25, 0.008], [26, 0.009], [27, 0.012], [28, 0.0155], [29, 0.0175], 
            [30, 0.022],[31, 0.021], [32, 0.019], [33, 0.01], [34, 0.005], 
            [35, 0.001], [36, 0.000]]
        X = np.array(X)
        x_sample = X[:,0]
        y_sample = X[:,1]

        self.f_temp_crit = CubicSpline(x_sample, y_sample, bc_type="natural")

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

    # def __set_pass_condtion(self, wt, biomass):
    #     self.wt_min_1 = wt
    #     self.biomass_min_1 = biomass

    # def __set_fr_params(self, csc, fa):
    #     self.csc = csc
    #     self.fa = fa

    def __set_fr(self, index,  alpha, m=1):
        temperature, nh4, do = ShrimpGrowth.biochem_factor(index, self.df, self.cond_temp, self.cond_uia, self.cond_do, self.col_temp, self.col_uia, self.col_do, self.col_doc)

        # temperature = self.f_temp_crit(self.df.loc[index, self.col_temp])
        
        # if (temperature == 0) or (nh4 == 0) or (do == 0):
        #     self.__is_in_condition = False
        # else:

        #     self.__is_in_condition = True

        # self.fr = alpha[0] * temperature + alpha[1] * nh4 + alpha[2] * do

        self.temperature = (temperature, alpha[0] * temperature)
        self.nh4 = (nh4, alpha[1] * nh4)
        self.do = (do, alpha[2] * do)

        self.fr = alpha[0] * temperature + alpha[1] * nh4 + alpha[2] * do

    def set_interpolate_biochem(self):
        self.f_temp = generate_interpolate_function(self.df, self.col_doc, self.col_temp)
        self.f_nh4 = generate_interpolate_function(self.df, self.col_doc, self.col_uia)
        self.f_do = generate_interpolate_function(self.df, self.col_doc, self.col_do)


    @functools.lru_cache(maxsize=18000)
    def single_operation(self, t0, data, alpha1, alpha2, alpha3):
        selected_cycle = get_cycle_data(data[0], data[1], self.df)
        f_temp = generate_spline_function(selected_cycle, self.col_doc, self.cond_temp, self.col_temp, biochem_type="temperature")
        f_nh4 = generate_spline_function(selected_cycle, self.col_doc, self.cond_uia, self.col_uia, biochem_type="nh4")
        f_do = generate_spline_function(selected_cycle, self.col_doc, self.cond_do, self.col_do, biochem_type="do")
        
        weight = ShrimpGrowth.weight(t0, data[1], self.w0, self.wn, (f_temp, f_nh4, f_do), (alpha1, alpha2, alpha3))    
        return weight, 0

    def multiple_operation(self, data, alpha, alpha2, alpha3):
        _, m = data.shape
        res = np.asarray([self.single_operation(0, tuple(data[:, t]), alpha, alpha2, alpha3)[0] for t in range(m)])
        return res
    
    def fit(self):
        data = np.asarray([self.df.index.tolist(), self.df[self.col_doc].tolist()])
        alpha = curve_fit(self.multiple_operation, data, self.df[self.col_abw].tolist())[0]
        self.alpha = alpha
        return alpha

    def mse(self):
        alpha, alpha2, alpha3 = self.alpha
        data = []
        for i in self.df.iterrows():
            data.append((i[1][self.col_abw] - self.single_operation(0, tuple([i[0], i[1][self.col_doc]]), alpha, alpha2, alpha3))**2)
    
        return np.mean(data)

        