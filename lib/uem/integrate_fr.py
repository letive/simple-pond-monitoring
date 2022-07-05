from scipy.integrate import quad


class Fungsi:
    def __init__(self, a, b, f_uia, f_o2, f_temp, score_csc, feeding_rate):

        self.a = a
        self.b = b

        self.f_uia = f_uia
        self.f_o2 = f_o2
        self.f_temp = f_temp

        self.score_csc = score_csc
        self.feeding_rate = feeding_rate

    def _integrate_function(self, t):
        temp = self.f_temp(t)
        o2 = self.f_o2(t)
        uia = self.f_uia(t)

        if (temp == 0) or (o2 == 0) or (uia == 0):
            return 0
        else:
            return temp + o2 + uia + self.score_csc + self.feeding_rate

    def get_integral(self):
        return quad(self._integrate_function, self.a, self.b, limit=3000)
