import numpy as np
from lib.partial_harvest import PartialHarvest as ph
from lib.helpers import biomass_harvest, price_function

class SubCost:
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
        return e*d*max


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

def costing(t0, T, area, wn, w0, alpha, n0, sr, partial1, partial2, partial3,
        docpartial1, docpartial2, docpartial3, docfinal, e, p, o, 
        labor_cost, bonus, h, r, fc, formula):

    m = -np.log(sr)/T
    energy = []
    probiotics = []
    others = []
    feeds = []
    harvest = []
    biomassa = []
    bonusses = []
    realized_revenue = []
    labor = []

    f = price_function("data/fixed_price.csv")

    times = range(0, T+1)
    for t in times:
        sub_cost = SubCost(t, docfinal)
        energy.append(sub_cost.energy_cost(e))
        probiotics.append(sub_cost.probiotic_cost(p))
        others.append(sub_cost.other_cost(o))
        labor.append(sub_cost.labor_cost(labor_cost))

        obj = ph(t0, t, area, wn, w0, alpha, n0, m, sr, partial1, partial2, partial3,
            docpartial1, docpartial2, docpartial3, docfinal)

        # hv = obj.harvest_cost(h, pl, sr)
        hv = obj.harvest_cost(h)
        harvest.append(hv[0])
        feeds.append(obj.feed_cost(fc, formula, r))

        biomassa.append(obj.biomassa()["kg"])
        bonusses.append(0)

        realized_revenue.append(obj.realized_revenue(f))

    # total biomassa which harvested
    total = sum(biomass_harvest(biomassa, T, docpartial1, docpartial2, docpartial3))

    bonusses[T] = bonus * total

    data = np.array([energy, probiotics, others, harvest, feeds, bonusses, labor])
    aggregate = data.sum(axis=1)/data.sum() 

    plharvested = hv[1]
    cost_perkg = data.sum()/total
    cost_perpl = data.sum()/sum(plharvested)

    total_revenue = sum(realized_revenue)
    profit = total_revenue - data.sum()
    try:
        revenue_perpl = total_revenue/total
    except:
        revenue_perpl = 0

    return_opex = profit/data.sum()
    margin = profit/total_revenue

    ### get profit for each time
    cost_t = [data[:, :t].sum() for t in times]
    cum_revenue = np.cumsum(realized_revenue)
    profit_t = cum_revenue - cost_t
    result = {
        "index": ["energy_cost", "probiotics_cost", "others_cost",
            "harvest_cost", "feed_cost", "bonusses", "labor_cost"],
        "data": data.transpose().tolist(),
        "aggregate": aggregate.tolist(),
        "matrix": {
            "costPerKg": cost_perkg,
            "costPerPl": cost_perpl,
            "totalCost": data.sum(),
            "totalRevenue": total_revenue,
            "profit": profit,
            "revenuePerPl": revenue_perpl,
            "returnOnOpex": return_opex,
            "margin": margin
        },
        "data_profit": {
            "revenue": cum_revenue.tolist(),
            "cost": cost_t,
            "profit": profit_t.tolist()
        }
    }
    return result