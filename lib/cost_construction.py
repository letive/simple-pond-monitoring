class ConstantCost:
    def __init__(self, t, final_doc) -> None:
        """
        t: time t-th
        """
        self.t = t
        self.final_doc = final_doc

    def energy_cost(self, e, d=820, max=24):
        """
        e: energy consumtion (HP)
        d: harga listrik per HP
        max: max hours. Default 24.
        """
        return e * d * max

    def probiotic_cost(self, p):
        """
        p: daily probiotics
        final_doc: doc for final harvest
        """
        return p if self.t < self.final_doc else 0

    def other_cost(self, o):
        """
        t: time t-th
        o: other daily cost
        final_doc: doc for final harvest
        """
        return o if self.t < self.final_doc else 0

    def labor_cost(self, labor_cost):
        return labor_cost if self.t < self.final_doc else 0
