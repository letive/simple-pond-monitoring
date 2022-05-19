import numpy as np
from lib.partial_harvest import PartialHarvest as ph
from lib.helpers import price_function

class constantCost:
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


def costing(t0, T, area, wn, w0, alpha, n0, sr, partial, doc, e, p, o, 
        labor_cost, bonus, h, r, fc, formula, final_doc=120):

    energy = []
    probiotics = []
    others = []
    feeds = []
    harvest = []
    biomassa = []
    bonusses = []
    realized_revenue = []
    labor = []
    adg = []
    fcr = []

    harvest_population = []
    harvest_biomass = []

    f = price_function("data/fixed_price.csv")

    m = np.log(sr)/T
    times = range(0, T+1)
    for t in times:
        sub_cost = constantCost(t, final_doc)
        energy.append(sub_cost.energy_cost(e))
        probiotics.append(sub_cost.probiotic_cost(p))
        others.append(sub_cost.other_cost(o))
        labor.append(sub_cost.labor_cost(labor_cost))

        obj = ph(t0, t, wn, w0, alpha, n0, sr, m, partial, doc)
        
        harvest.append(obj.harvest_cost(h) * area)
        feeds.append(obj.feed_cost(fc, formula, r)*area)

        biomassa.append(obj.biomassa()/1000 * area)
        bonusses.append(0)

        realized_revenue.append(obj.realized_revenue(f)*area)
        adg.append(obj.adg())
        fcr.append(obj.fcr(formula, r))

        harvest_population.append(obj.harvested_population()* area)
        harvest_biomass.append(obj.biomass_harvest()/1000 * area)


    bonusses[T] = bonus * sum(harvest_biomass)
    data = np.array([energy, probiotics, others, harvest, feeds, bonusses, labor])
    aggregate = data.sum(axis=1)/data.sum() 

    cost_perkg = data.sum()/sum(harvest_biomass)
    cost_perpl = data.sum()/sum(harvest_population)

    total_revenue = sum(realized_revenue)

    profit = total_revenue - data[:, :T].sum()
    try:
        revenue_perpl = total_revenue/sum(harvest_population)
    except:
        revenue_perpl = 0

    return_opex = profit/data.sum()
    margin = profit/total_revenue

    ### get profit for each time
    cost_t = [data[:, :ti].sum() for ti in range(T+1)]
    cum_revenue = np.cumsum(realized_revenue)
    profit_t = cum_revenue - cost_t

    yeild = (sum(harvest_biomass))/(area/1000)/1000 #ton/ha
    fcr_t = sum(fcr)
    print(fcr)
    result = {
        "index": ["energy_cost", "probiotics_cost", "others_cost",
            "harvest_cost", "feed_cost", "bonusses", "labor_cost"],
        "data": data.transpose().tolist(),
        "aggregate": aggregate.tolist(),
        "matrix": {
            "costPerKg": "Rp {:,.2f}".format(cost_perkg),
            "costPerPl": "Rp {:,.2f}".format(cost_perpl),
            "totalCost": "Rp {:,.2f}".format(data[:, :T].sum()),
            "totalRevenue": "Rp {:,.2f}".format(total_revenue),
            "profit":  "Rp {:,.2f}".format(profit),
            "revenuePerPl": "Rp {:,.2f}".format(revenue_perpl),
            "returnOnOpex": return_opex,
            "margin": margin,
            "yeild": yeild,
            "adg": adg[T],
            "fcr": fcr_t
        },
        "data_profit": {
            "revenue": cum_revenue.tolist(),
            "cost": cost_t,
            "profit": profit_t.tolist()
        }
    }
    return result