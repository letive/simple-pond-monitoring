import numpy as np
from lib.helpers import heaviside_step
from scipy.optimize import curve_fit


class Biomassa:
    def __init__(
        self,
        t0,
        t,
        wn,
        w0,
        alpha,
        n0: int,
        sr: float,
        m: float,
        ph: list,
        doc: list,
        f_uia,
        f_o2,
        f_temp,
        score_csc,
        feeding_rate,
        alpha2,
        alpha3,
        alpha4,
        alpha5,
        alpha6,
        final_doc: int = 120,
    ):
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

        self.f_uia = f_uia
        self.f_o2 = f_o2
        self.f_temp = f_temp
        self.score_csc = score_csc
        self.feeding_rate = feeding_rate

        self.alpha2 = alpha2
        self.alpha3 = alpha3
        self.alpha4 = alpha4
        self.alpha5 = alpha5
        self.alpha6 = alpha6


    def wt(self):
        fr = (
            self.alpha * (self.t - self.t0) 
            + self.alpha2 * self.f_temp(self.t) 
            + self.alpha3 * self.f_o2(self.t) 
            + self.alpha4 * self.f_uia(self.t)
            + self.alpha5 * self.score_csc 
            + self.alpha6 * self.feeding_rate
        )

        return (
            self.wn ** (1 / 3)
            - (self.wn ** (1 / 3) - self.w0 ** (1 / 3))
            * np.exp(-1 * fr)
        ) ** 3

    def population(self):
        t = self.t
        ph = self.ph
        partial_harvest = [
            ph[i] * heaviside_step(t - j) for i, j in enumerate(self.doc)
        ]

        if t >= self.final_doc:
            partial_harvest.append(
                (self.sr - sum(ph)) * heaviside_step(t - self.final_doc)
            )

        result = self.n0 * (np.exp(-self.m * t) - sum(partial_harvest))
        return result

    def biomassa(self):
        # biomassa in gram
        return self.wt() * self.population()

    def biomassa_constant(self):
        return self.n0 * self.wt()


from lib.helpers import source_data, score_csc_compute
from lib.uem.feeding_rate import feeding_rate

f_uia, f_o2, f_temp, temperature = source_data(
    # path = "data/growth_full2.csv",
    path = None,
    temp_suitable_min = 25,
    temp_suitable_max = 33,
    temp_optimal_min = 28,
    temp_optimal_max = 32,
    do_suitable_min = 4,
    do_suitable_max = 10,
    do_optimal_min = 6,
    do_optimal_max = 9,
    ua_suitable_min = 0.00,
    ua_suitable_max = 0.16,
    ua_optimal_min = 0.00,
    ua_optimal_max = 0.06,
)

csc_suitable_min = 0.00
csc_suitable_max = 5
csc_optimal_min = 0.00
csc_optimal_max = 3


import functools
class Estimate:
    def __init__(self, t0, w0, wn, n0, sr, ph, doc, T, y, final_doc=12) -> None:
        self.t0 = t0
        self.w0 = w0 
        self.wn = wn 
        self.n0 = n0
        self.sr = sr
        self.ph = ph
        self.doc = doc
        self.final_doc = final_doc
        
        self.T = T
        self.y = y

    @functools.lru_cache(maxsize=18000)
    def single_wt1(self, t, sr, m, alpha, alpha2, alpha3, alpha4, alpha5,  alpha6):
        try:
            feedRate = feeding_rate(0, float(temperature[temperature["DOC"]==t]["Temp"]), 0)
        except  :
            feedRate = 0

        if t == 0:
            score_csc = score_csc_compute(0/1000, self.n0*10, csc_suitable_min, csc_suitable_max, csc_optimal_max)
        else:
            _, bio_1 = self.single_wt1(t-1, sr, m, alpha, alpha2, alpha3, alpha4, alpha5, alpha6)
            score_csc = score_csc_compute(bio_1/1000, self.n0*10, csc_suitable_min, csc_suitable_max, csc_optimal_max)
            
        obj = Biomassa(self.t0, t, self.wn, self.w0, alpha, self.n0, sr, m, self.ph, self.doc, f_uia, f_o2, f_temp, feedRate, score_csc, 
            alpha2, alpha3, alpha4, alpha5, alpha6, final_doc=self.final_doc)

        return  obj.wt(), obj.biomassa()


    def multi_wt(self, T, alpha, alpha2, alpha3, alpha4, alpha5, alpha6):
        # sr = 0.92
        m = -np.log(self.sr)/T[-1]
        res = np.asarray([self.single_wt1(t, self.sr, m, alpha, alpha2, alpha3, alpha4, alpha5, alpha6)[0] for t in T])
        return res

    
    def fitting(self):
        alpha, alpha2, alpha3, alpha4, alpha5, alpha6 = curve_fit(self.multi_wt, self.T, self.y,  p0=[0.05, 0.05, 0.05,0.05, 0.05,0.05], method="dogbox", ftol=1e-05)[0]
        return alpha, alpha2, alpha3, alpha4, alpha5, alpha6
