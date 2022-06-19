import numpy as np
from lib.integrate_fr import Fungsi
from lib.helpers import heaviside_step


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
        # f_uia,
        # f_o2,
        # f_temp,
        # score_csc,
        # feeding_rate,
        # integrate_cumulation=0,
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

        # self.f_uia = f_uia
        # self.f_o2 = f_o2
        # self.f_temp = f_temp
        # self.score_csc = score_csc
        # self.feeding_rate = feeding_rate

        # self.integrate_cumulation = integrate_cumulation

    def wt(self):
        return (
            self.wn ** (1 / 3)
            - (self.wn ** (1 / 3) - self.w0 ** (1 / 3))
            * np.exp(-self.alpha * (self.t - self.t0))
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
