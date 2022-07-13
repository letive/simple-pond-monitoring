import numpy as np
from scipy.integrate import quad
from lib.helpers import normal_trapezoidal, left_trapezoidal, heaviside_step
from lib.v2.error import ErrorIndex

class ShrimpGrowth:

    # @staticmethod
    # def biochem_factor(t, temp, uia, do, cond_temp, cond_uia, cond_do, alpha=(1,1,1)):
    #     """
    #     biochem_factor funtions is respresent parameter condition for chemical & biological resouces
    #     temp: temperature function
    #     uia: unionized amonia function
    #     do: dissolved oxygen function
    #     cond_temp: conditional temperature. 
    #                The type is tuple with (suitable min, optimal min, optimal max, suitable max)
    #     cond_uia: conditional unionized amonia. 
    #                The type is tuple with (suitable min, optimal min, optimal max, suitable max)
    #     cond_do: conditional dissolved oxygen. 
    #                The type is tuple with (suitable min, optimal min, optimal max, suitable max)

    #     alpha: alpha parameter for each factor. 
    #             The type of input is tuple with order (temperature, unionized amonia, dissolved oxygen)
    #     """
        
    #     temperature = normal_trapezoidal(temp(t), cond_temp[0], cond_temp[3], cond_temp[1], cond_temp[2]) 
    #     unionized_amonia = left_trapezoidal(uia(t), cond_uia[0], cond_uia[3], cond_uia[2])
    #     dissolved_oxygen = normal_trapezoidal(do(t), cond_do[0], cond_do[3], cond_do[1], cond_do[2])

    #     if (temperature == 0) or (unionized_amonia == 0) or (dissolved_oxygen == 0):
    #         return 0
    #     else:
    #         return alpha[0]*temperature + alpha[1] * unionized_amonia + alpha[2] * dissolved_oxygen 

    @staticmethod
    def biochem_factor(t, df, cond_temp, cond_uia, cond_do, alpha=(1,1,1), col_temp="temperature", col_uia="unionized_amonia", col_do="dissolved_oxygen", col_doc="DOC"):
        try:
            temperature = normal_trapezoidal(df[df[col_doc] == t][col_temp].values[0], cond_temp[0], cond_temp[3], cond_temp[1], cond_temp[2]) 
        except:
            temperature = normal_trapezoidal(np.nan, cond_temp[0], cond_temp[3], cond_temp[1], cond_temp[2]) 

        try:
            unionized_amonia = left_trapezoidal(df[df[col_doc] == t][col_uia].values[0], cond_uia[0], cond_uia[3], cond_uia[2])
        except:
            unionized_amonia = left_trapezoidal(np.nan, cond_uia[0], cond_uia[3], cond_uia[2])

        try:
            dissolved_oxygen = normal_trapezoidal(df[df[col_doc] == t][col_do].values[0], cond_do[0], cond_do[3], cond_do[1], cond_do[2])
        except:
            dissolved_oxygen = normal_trapezoidal(np.nan, cond_do[0], cond_do[3], cond_do[1], cond_do[2])

        if (temperature == 0) or (unionized_amonia == 0) or (dissolved_oxygen == 0):
            return 0
        else:
            return alpha[0]*temperature + alpha[1] * unionized_amonia + alpha[2] * dissolved_oxygen 


    @staticmethod
    def csc_factor(biomassa, volume, cond_csc, alpha=1):
        """
        csc_factor funtions is respresent parameter condition for critical steady crop
        biomassa: biomassa at t-1 which gram unit
        cond_csc: conditional critical steady crop. 
                   The type is tuple with (suitable min, optimal min, optimal max, suitable max)
        """
        
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
            index_y = 9
        else:
            try:
                index_y = round(temperature/2) - 1
            except:
                index_y = None

        if (index_x != None) & (index_y != None):
            try:
                return alpha * df.loc[index_y, index_x].values[0]
            except ErrorIndex:
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


    @staticmethod
    def weight(t0, t, w0, wn, fr, alpha, constant_fr=1):
        """
        t: time at t
        t0: initial time
        w0: initial weight
        wn: weight at time t
        alpha: shrimp growth rate
        constant_fr: the function of F which will be integrated
        """
        if fr != 0:
            wt = (wn**(1/3) - (wn**(1/3) - w0**(1/3)) 
                * np.exp(-alpha*(fr + quad(lambda x: constant_fr, t0, t)[0])))**3
            return wt
        else:
            wt = (wn**(1/3) - (wn**(1/3) - w0**(1/3)) 
                * np.exp(0))**3
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