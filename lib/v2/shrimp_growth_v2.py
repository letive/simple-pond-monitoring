# from numbers import Integral
import numpy as np
from scipy.integrate import quad
from lib.helpers import normal_trapezoidal, left_trapezoidal, heaviside_step
# from lib.v2.error import ErrorIndex

class ShrimpGrowth:

    @staticmethod
    def biochem_factor(t, df, cond_temp, cond_uia, cond_do, col_temp="temperature", col_uia="unionized_amonia", col_do="dissolved_oxygen", col_doc="DOC"):
        temperature = normal_trapezoidal(df.loc[t, col_temp], cond_temp[0], cond_temp[3], cond_temp[1], cond_temp[2]) 
        unionized_amonia = left_trapezoidal(df.loc[t, col_uia], cond_uia[0], cond_uia[3], cond_uia[2])
        dissolved_oxygen = normal_trapezoidal(df.loc[t, col_do], cond_do[0], cond_do[3], cond_do[1], cond_do[2])

        return temperature, unionized_amonia, dissolved_oxygen

    @staticmethod
    def biochem_function():
        pass


    @staticmethod
    def csc_factor(biomassa, volume, cond_csc, alpha=1):
        """
        csc_factor funtions is respresent parameter condition for critical steady crop
        biomassa: biomassa at t-1 which gram unit
        cond_csc: conditional critical steady crop. 
                   The type is tuple with (suitable min, optimal min, optimal max, suitable max)
        """
        # print(biomassa/1000, biomassa/1000/volume, volume)
        csc = left_trapezoidal((biomassa/1000)/volume, cond_csc[0], cond_csc[3], cond_csc[2])
        return alpha * csc

    @staticmethod
    def feed_availablelity_factor(wt, temperature, df, alpha=1):
        """
        feed_availablelity_factor funtions is respresent parameter condition for feed availablelity
        wt: weight at t-1 which gram unit
        temperature: temperature at time t-1
        """

       
        # check wt
        index_x = None
        if (wt < 21) or (wt > 32):
            index_x = None
        elif wt <= 24:
            index_x = "21-24"
        elif wt > 28:
            index_x = "28-32"
        else:
            index_x = "24-28"

        # check temperature
        index_y = None
        if (temperature<1) & (temperature>30):
            index_y = None
        elif temperature > 17:
            index_y = 8
        else:
            try:
                index_y = round(temperature/2) - 1
            except:
                index_y = None

        if (index_x != None) & (index_y != None):
            try:
                return alpha * df.loc[index_y, index_x]
            except:
                print("Index not found")
        else:
            return 0


    # @staticmethod
    # def fr(biochem, csc, fa):
    #     """
    #     biochem: biological and chemistry parameter which is temperature, unionized amonia, & dissolved oxygen 
    #     csc: critical steady crop
    #     fa: food avaiablelity
    #     """
        
    #     return biochem + csc + fa

    def integrate_function(t, function, condition, type):
        """
        t: the time value
        function: interpolation function
        condition: list of condition
        type: type of function. ex: temperature
        """
        if (type == "temperature") or (type == "do"):
            return normal_trapezoidal(function(t), condition[0], condition[3], condition[1], condition[2])
        elif type == "nh4":
            return left_trapezoidal(function(t), condition[0], condition[3], condition[2])

    def integrate_function_v2(t, function, condition, alpha):
        """
        t: the time value
        function: list interpolation function
        condition: list of condition
        type: list type of function. ex: temperature
        """
        
        temp = alpha[0] * normal_trapezoidal(function[0](t), condition[0][0], condition[0][3], condition[0][1], condition[0][2])
        do = alpha[2] * normal_trapezoidal(function[2](t), condition[2][0], condition[2][3], condition[2][1], condition[2][2])
        nh4 = alpha[1] * left_trapezoidal(function[1](t), condition[1][0], condition[1][3], condition[1][2])

        return temp+do+nh4


    @staticmethod
    def weight(t0, t, w0, wn, fr, alpha):
    # def weight(t0, t, w0, wn, fr, alpha, condition):
        """
        t: time at t
        t0: initial time
        w0: initial weight
        wn: weight at time t
        alpha: list/tuple of params
        fr: list/tuple of function
        condition: list of list condition
        """
        integrale1 = alpha[0]*quad(fr[0], t0, t, limit=200)[0]
        integrale2 = alpha[1]*quad(fr[1], t0, t, limit=200)[0]
        integrale3 = alpha[2]*quad(fr[2], t0, t, limit=200)[0]

        # # integrale1 = alpha[0]*quad(ShrimpGrowth.integrate_function, t0, t, args=(fr[0], condition[0], "temperature"))[0]
        # # integrale2 = alpha[1]*quad(ShrimpGrowth.integrate_function, t0, t, args=(fr[1], condition[1], "nh4"))[0]
        # # integrale3 = alpha[2]*quad(ShrimpGrowth.integrate_function, t0, t, args=(fr[2], condition[2], "do"))[0]

        # # f = quad(ShrimpGrowth.integrate_function_v2, t0, t, args=(fr, condition, alpha))[0]
        # wt = (wn**(1/3) - (wn**(1/3) - w0**(1/3))* np.exp(-1 * (integrale1 + integrale2 + integrale3)))**3

        # integrale1 = quad(ShrimpGrowth.integrate_function, t0, t, args=(fr[0], condition[0], "temperature"))[0]
        # integrale2 = quad(ShrimpGrowth.integrate_function, t0, t, args=(fr[1], condition[1], "nh4"))[0]
        # integrale3 = quad(ShrimpGrowth.integrate_function, t0, t, args=(fr[2], condition[2], "do"))[0]

        # f = quad(ShrimpGrowth.integrate_function_v2, t0, t, args=(fr, condition, alpha), limit=200)[0]

        wt = (wn**(1/3) - (wn**(1/3) - w0**(1/3))* np.exp(-alpha[3] * (alpha[0]*integrale1 + alpha[1]*integrale2 + alpha[2]*integrale3)))**3
        # wt = (wn**(1/3) - (wn**(1/3) - w0**(1/3))* np.exp(-alpha * (abs(integrale1) + abs(integrale2) + abs(integrale3))))**3
        return wt


    @staticmethod
    def population(t, n0, sr, m, ph, doc, final_doc=120):
        """
        t: time at t
        n0: initial 
        sr: survival rate
        m: mortality rate (it depends on the global T)
        ph: the amount of partial harvest percentation
        doc: the list of time which will be partial harvest
        final_doc: The final harvest
        """
        partial_harvest = [ph[i] * heaviside_step(t - j) for i, j in enumerate(doc)]

        if t >= final_doc:
            partial_harvest.append((sr - sum(ph)) * heaviside_step(t - final_doc))

        result = n0 * (np.exp(-m * t) - sum(partial_harvest))
        return result

    @staticmethod
    def biomassa(weight, population):
        return weight * population