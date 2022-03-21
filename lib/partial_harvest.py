from lib.helpers import body_weight, heaviside_step, pl_harvest, feed_formula3
import numpy as np

class PartialHarvest:
    def __init__(self, t0, t, area, wn, w0, alpha, n0, m, partial1, partial2, partial3, 
            docpartial1, docpartial2, docpartial3, docfinal) -> None:

        self.t0 = t0
        self.t = t
        self.area = area
        self.wn = wn
        self.w0 = w0
        self.alpha = alpha
        self.n0 = n0
        self.m = m
        self.partial1 = partial1
        self.partial2 = partial2
        self.partial3 = partial3
        self.docpartial1 = docpartial1
        self.docpartial2 = docpartial2
        self.docpartial3 = docpartial3
        self.docfinal = docfinal

    def wt(self):
        return body_weight(self.wn, self.w0, self.alpha, self.t0, self.t)

    # def population(self):
    #     ph1 = self.partial1 * heaviside_step(self.t-self.docpartial1)
    #     ph2 = self.partial2 * heaviside_step(self.t-self.docpartial2)
    #     ph3 = self.partial3 * heaviside_step(self.t-self.docpartial3)
    #     final = heaviside_step(self.t-self.docfinal)
    #     result = self.n0 * (np.exp(-self.m*(self.t-self.t0)) - ph1 - ph2 - ph3 - final)
    #     return result

    def population(self):
        ph1 = self.partial1 * heaviside_step(self.t-self.docpartial1)
        ph2 = self.partial2 * heaviside_step(self.t-self.docpartial2)
        ph3 = self.partial3 * heaviside_step(self.t-self.docpartial3)
        # final = heaviside_step(self.t-self.docfinal)
        result = self.n0 * np.exp(-self.m*(self.t)) - ph1 - ph2 - ph3
        return result

    def biomassa(self):
        result = (self.area * self.wt() * self.population())
        return {"gr": result, "kg": result/1000}
    
    def biomassa_constant(self):
        return self.area * self.wt() * self.n0

    # def harvest_cost(self, h, pl, sr):
    #     """
    #     h: harvest cost per kg
    #     pl: intial postlarva 
    #     sr: survival rate
    #     """
        
    #     doc = [self.docpartial1, self.docpartial2, self.docpartial3, self.docfinal]
    #     plharvest1 = pl_harvest(pl, sr, self.partial1)
    #     plharvest2 = pl_harvest(pl, sr, self.partial2)
    #     plharvest3 = pl_harvest(pl, sr, self.partial3)
    #     plfinal = pl_harvest(pl, sr, 1 - self.partial1 - self.partial2 - self.partial3)
    #     plharvest = [plharvest1, plharvest2, plharvest3, plfinal]
    #     status = False
    #     for i in enumerate(doc):
    #         if self.t == i[1]:
    #             result = plharvest[i[0]]*h*self.wt()/1000 # dibagi 1000 untuk mengubahnya menjadi kg
    #             status = True
    #             break

    #     if not status:
    #         result = 0

    #     return result, plharvest

    def harvest_cost(self, h):
        """
        h: harvest cost per kg
        pl: intial postlarva 
        sr: survival rate
        """
        
        doc = [self.docpartial1, self.docpartial2, self.docpartial3]
        ph1 = self.partial1 * heaviside_step(self.t-self.docpartial1)
        ph2 = self.partial2 * heaviside_step(self.t-self.docpartial2)
        ph3 = self.partial3 * heaviside_step(self.t-self.docpartial3) 
        plharvest = [ph1, ph2, ph3]
        status = False
        for i in enumerate(doc):
            if self.t == i[1]:
                result = plharvest[i[0]]*h*self.wt()/1000 # dibagi 1000 untuk mengubahnya menjadi kg
                status = True
                break

        if not status:
            result = 0

        return result, plharvest

    def feed_cost(self, fc, formula_type=2, r=None):
        """
        r: feeding rate
        fc: feed cost per kg
        formula_type: formula_type for feeding cost calculation. There are 1 and 2.
        """
        if formula_type == 1:
            return self.biomassa()["kg"] * r * fc
        else:
            formula3 = feed_formula3("data/data-feeding-formula-3.csv", ",")
            if self.t < self.docfinal:
                return formula3[self.t] * self.area / 1000 * (1+0.2) * fc
            else:
                return 0

    def realized_revenue(self, f):
        doc = [self.docpartial1, self.docpartial2, self.docpartial3, self.docfinal]
        if self.t in doc:
            return self.biomassa()["kg"] * f(1000/self.wt())
        else:
            return 0

    def potential_revenue(self, f):
        pr = self.biomassa_constant()/1000 * f(1000/self.wt())
        return 0 if pr < 0 else pr

    def cost_function(self, f):
        return f(1000/self.wt())