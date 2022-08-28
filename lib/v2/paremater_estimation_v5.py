import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import CubicSpline
from lib.helpers_mod.helpers import integrate_function, generate_interpolate_function
from scipy.integrate import quad

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
        y_sample = X[:,1] * (1/0.022)

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

    def set_interpolate_biochem(self, df=None):
        
        if type(df) !=  pd.DataFrame:
            df = self.df.copy()

        self.f_temp = generate_interpolate_function(df, self.col_doc, self.col_temp)
        self.f_nh4 =  generate_interpolate_function(df, self.col_doc, self.col_uia)
        self.f_do = generate_interpolate_function(df, self.col_doc, self.col_do)

    def integrate_temp(self, t):
        return self.f_temp_crit(self.f_temp(t))

    def multiple_operation_v2(self, data, alpha1, alpha2, alpha3, alpha4):
        integrale1, integrale2, integrale3 = 0, 0, 0
    
        wt = []
        for t in data:
            if t-1 == 0:
                integrale1, integrale2, integrale3 = 0, 0, 0
                integrale1 = integrale1 + quad(integrate_function, 0, t-1, args=(self.f_temp, self.cond_temp, "temperature"))[0]
                integrale2 = integrale2 + quad(integrate_function, 0, t-1, args=(self.f_nh4, self.cond_uia, "nh4"))[0]
                integrale3 = integrale3 + quad(integrate_function, 0, t-1, args=(self.f_do, self.cond_do, "do"))[0]
            else:
                integrale1 = integrale1 + quad(integrate_function, t-2, t-1, args=(self.f_temp, self.cond_temp, "temperature"))[0]
                integrale2 = integrale2 + quad(integrate_function, t-2, t-1, args=(self.f_nh4, self.cond_uia, "nh4"))[0]
                integrale3 = integrale3 + quad(integrate_function, t-2, t-1, args=(self.f_do, self.cond_do, "do"))[0]

            wt.append((self.wn**(1/3) - (self.wn**(1/3) - self.w0**(1/3)) * np.exp(-1 * (alpha1*integrale1 + alpha2*integrale2 + alpha3*integrale3 + alpha4*(t-1 - 0))))**3)
        return wt


    def fit(self):
        df = self.df.copy()
        self.set_interpolate_biochem(df)
        alpha = curve_fit(self.multiple_operation_v2, df[self.col_doc].values, df[self.col_abw].values, bounds=((-1, 1)))[0]
        self.alpha = alpha
        return alpha

    def mse(self):
        alpha, alpha1, alpha2, alpha3 = self.alpha
        weight = np.asarray(self.multiple_operation_v2(self.df[self.col_doc], alpha, alpha1, alpha2, alpha3))
        data = (self.df[self.col_abw] - weight)**2
        return np.mean(data)

        