from lib.helpers import body_weight, heaviside_step, feed_formula3
import numpy as np

# base function per m2 in t 

class PartialHarvest:
    def __init__(self, t0: int, t: int, wn: float, w0: float, alpha: float, n0: int, sr: float, m: float, 
        ph: list, doc: list, final_doc:int = 120) -> None:
        """
        t0: initial time
        t: current time
        wn: shrimp max weight 
        w0:  shrimp stocking weight g
        alpha: shrimp growth rate
        n0: shrimp stocking density
        sr: survival rate
        ph: partial harvest. list of the amount each partial harvest
        doc: day old culture. list of the partial harvest time
        """
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

    def wt(self):
        return body_weight(self.wn, self.w0, self.alpha, self.t0, self.t)

    # def SR(self):
    #     m = np.log(self.sr)/self.t if self.t != 0 else 0
    #     return m 

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
    
    def biomassa_constant(self):
        return self.wt() * self.n0

    #########################################
    # revenue
    #########################################
    def harvest_tmin1(self, t):
        obj = PartialHarvest(self.t0, t, self.wn, self.w0, self.alpha, self.n0, self.sr, self.m, self.ph, self.doc, self.final_doc)
        return obj.biomassa()

    def harvest_population(self):
        if (self.t in self.doc) or (self.t == self.final_doc):
            return self.population()
        else:
            return 0

    def harvest_biomass(self):
        if (self.t in self.doc):
            return (self.harvest_tmin1(self.t-1) - self.biomassa())/1000
        elif self.t == self.final_doc:
            return (self.harvest_tmin1(self.t-1) - self.biomassa())/1000
        else:
            return 0

    def realized_revenue(self, f):
        return self.harvest_biomass() * f(1000/self.wt()) # biomassa dikalikan dengan harga per size 

    def potential_revenue(self, f):
        pr = self.biomassa_constant()/1000 * f(1000/self.wt())
        return 0 if pr < 0 else pr

    #########################################
    # costing
    #########################################
    def feeding_formula(self, formula_type=2, r=None):
         # biomassa * feed_rate
        if formula_type == 1:
            return self.biomassa()/1000 * r
        else:
            formula3 = feed_formula3("data/data-feeding-formula-3.csv", ",")
            if self.t < self.final_doc:
                return (formula3[self.t] / 1000) * (1+0.2)
            else:
                return 0 

    def feed_cost(self, fc, formula_type=2, r=None):
        """
        r: feeding rate
        fc: feed cost per kg
        formula_type: formula_type for feeding cost calculation. There are 1 and 2.
        """
        feed_formula = self.feeding_formula(formula_type, r) * fc
        return feed_formula

    def harvest_cost(self, h):
        """
        h: harvest cost per kg
        """
        return self.harvest_biomass() * h

    # def fcr(self, formula_type=2, r=None):
    #     feed = self.feeding_formula(formula_type, r)
    #     biomass = self.biomassa()/1000
    #     try:
    #         return 0 if np.isnan(feed/biomass) else float(feed)/biomass
    #     except:
    #         return 0
        

    def adg(self):
        """
        average daily growth
        """
        result = self.wt()/self.t if self.t !=0 else 0
        return result