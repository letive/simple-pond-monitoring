import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import CubicSpline
from lib.helpers_mod.helpers import integrate_function, generate_interpolate_function
from scipy.integrate import quad
import re

class ParemeterEstimation:
    
    def __init__(self, df = None, path: str = None, sep: str =",", 
            col_temp="temperature", col_uia="unionized_amonia", col_do="dissolveed_oxygen", 
            col_doc="DOC", col_abw="ABW", col_adg="ADG"):

        if type(df) == pd.DataFrame:
            data = df
        else:
            data = pd.read_csv(path, sep=sep)
        
        data.reset_index(drop=True, inplace=True)

        cols = [re.sub(" ", "", i) for i in data.columns]
        data.columns = cols
        data.replace("#DIV/0!", 0, inplace=True)
        
        data = data[[col_doc, col_temp, col_uia, col_do, col_abw]]
        
        if (str(data[col_abw][0]).isnumeric() == False):
            df1 = pd.DataFrame({
                col_doc:[1],
                col_temp: [np.nan],
                col_uia: [np.nan],
                col_do: [np.nan],
                col_abw: [0.05]
            })
            data = pd.concat([df1, data.loc[1:]], axis=0, ignore_index=True)

        data[col_temp] = data[col_temp].fillna(data[col_temp].mean())
        data[col_uia] = data[col_uia].astype("float")
        data[col_uia] = data[col_uia].fillna(data[col_uia].mean())
        data[col_do] = data[col_do].fillna(data[col_do].mean())

        self.df = data[data[col_abw].notna()].reset_index(drop=True)
        
        self.wt_min_1 = 0
        self.biomass_min_1 = 0

        self.col_temp = col_temp
        self.col_uia = col_uia
        self.col_do = col_do
        self.col_doc = col_doc
        self.col_abw = col_abw


    def set_conditional_parameter(self, cond_temp, cond_uia, cond_do, cond_csc=None):
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

    # def set_food_availablelity_data(self, path=None, sep=","):
    #     if path:
    #         df = pd.read_csv(path, sep=sep)
    #     else:
    #         df = pd.DataFrame(
    #             {
    #                 "wt": ["1-3", "3-5", "5-7", "7-9", "9-11", "11-13", "13-15", "15-17", "17-30"],
    #                 "21-24": [0.08, 0.07, 0.065, 0.06, 0.055, 0.05, 0.045, 0.04, 0.03],
    #                 "24-28": [0.06, 0.05, 0.045, 0.04, 0.035, 0.03, 0.024, 0.025, 0.02],
    #                 "28-32": [0.07, 0.06, 0.055, 0.05, 0.045, 0.04, 0.035, 0.03, 0.025],
    #             }
    #         )

    #     self.fa_data = df

    def set_growth_paremater(self, t0, w0, wn, n0=None, sr=None):
        self.t0 = t0
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
        self.f_nh4 = generate_interpolate_function(df, self.col_doc, self.col_uia)
        self.f_do = generate_interpolate_function(df, self.col_doc, self.col_do)

    def integrate_temp(self, t):
        return self.f_temp_crit(self.f_temp(t))

    def weight(self, data, alpha, alpha1, alpha2, alpha3):
        
        integrale1, integrale2, integrale3 = 0, 0, 0
        wt = []
        for t in data:
            if (t-1 == 0) or (t-self.t0 == 0):
                integrale1 = integrale1 + quad(self.integrate_temp, self.t0, t)[0]
                integrale2 = integrale2 + quad(integrate_function, self.t0, t, args=(self.f_nh4, self.cond_uia, "nh4"))[0]
                integrale3 = integrale3 + quad(integrate_function, self.t0, t, args=(self.f_do, self.cond_do, "do"))[0]
                integrale4 = t - self.t0
            else:
                integrale1 = integrale1 + quad(self.integrate_temp, t-1, t)[0]
                integrale2 = integrale2 + quad(integrate_function, t-1, t, args=(self.f_nh4, self.cond_uia, "nh4"))[0]
                integrale3 = integrale3 + quad(integrate_function, t-1, t, args=(self.f_do, self.cond_do, "do"))[0]
                integrale4 = t - self.t0

            wt_i = (self.wn**(1/3) - (self.wn**(1/3) - self.w0**(1/3)) * 
                np.exp(-1 * (alpha*integrale1 + alpha1*integrale2 + alpha2*integrale3 + alpha3*integrale4))
            )**3
            
            if wt:
                if (wt_i < wt[-1]):
                    wt.append(wt[-1])
                else:
                    wt.append(wt_i)
            else:
                wt.append(wt_i)

        return wt


    def fit(self):
        df = self.df.copy()
        self.set_interpolate_biochem(df)
        alpha = curve_fit(self.weight, df[self.col_doc].values, df[self.col_abw].values, bounds=((-1, 1)))[0]
        self.alpha = alpha
        return alpha

    def mse(self):
        alpha, alpha1, alpha2, alpha3 = self.alpha
        df = self.df.copy()
        weight = np.asarray(self.weight(df[self.col_doc], alpha, alpha1, alpha2, alpha3))
        data = (df[self.col_abw] - weight)**2
        return np.mean(data)

        