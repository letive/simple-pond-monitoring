from lib.helpers import feed_formula3
import numpy as np


class Compute:
    def __init__(
        self,
        t0: int,
        t: int,
        doc: list,
        wt: float,
        nt: int,
        biomassa_t: float,
        biomass_t_1: float,
        constant_biomass: float,
        final_doc: int = 120,
    ) -> None:
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
        self.doc = doc
        self.final_doc = final_doc
        self.biomassa = biomassa_t
        self.biomassa_t_1 = biomass_t_1
        self.constant_biomass = constant_biomass
        self.population = nt
        self.wt = wt

    #########################################
    # Partial Harvest
    #########################################
    def harvest_population(self):
        t = self.t
        if (t in self.doc) or (t == self.final_doc):
            return self.population
        else:
            return 0

    def harvest_biomass(self):
        t = self.t
        if (t in self.doc) or (t == self.final_doc):
            return (self.biomassa_t_1 - self.biomassa)/ 1000
        else:
            return 0

    #########################################
    # revenue
    #########################################

    def realized_revenue(self, f):
        return self.harvest_biomass() * f(
            1000 / self.wt
        )  # biomassa dikalikan dengan harga per size
    
    def potential_revenue(self, f):
        pr = self.constant_biomass/1000 * f(1000/self.wt)
        return 0 if pr < 0 else pr

    #########################################
    # feeding
    #########################################
    def _feeding_formula(self, formula_type=2, r=None):
        # biomassa * feed_rate
        if formula_type == 1:
            return self.biomassa / 1000 * r
        else:
            formula3 = feed_formula3("data/data-feeding-formula-3.csv", ",")
            t = self.t
            if t < self.final_doc:
                return (formula3[t] / 1000) * (1 + 0.2)
            else:
                return 0

    def feeding_expense(self, fc, formula_type=2, r=None):
        """
        r: feeding rate
        fc: feed cost per kg
        formula_type: formula_type for feeding cost expense calculation. There are 1 and 2.
        """
        feed_formula = self._feeding_formula(formula_type, r) * fc
        return feed_formula

    def harvest_expense(self, h):
        """
        h: harvest cost per kg
        """
        return self.harvest_biomass() * h

    def fcr(self, formula_type=2, r=None):
        feed = self._feeding_formula(formula_type, r)
        biomass = self.biomassa/1000
        try:
            return 0 if np.isnan(feed/biomass) else float(feed)/biomass
        except:
            return 0

    def adg(self):
        """
        average daily growth
        """
        result = self.wt / self.t if self.t != 0 else 0
        return result
