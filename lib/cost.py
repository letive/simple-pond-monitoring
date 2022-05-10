import numpy as np
from lib.partial_harvest import PartialHarvest as ph
from lib.helpers import biomass_harvest, price_function, pl_harvest

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
        labor_cost, bonus, h, r, fc, formula):

    # m = -np.log(sr)/T
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

    f = price_function("data/fixed_price.csv")

    m = np.log(sr)/T
    times = range(0, T+1)
    for t in times:
        sub_cost = constantCost(t, doc[-1])
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

        ### harvested

    # harvest = obj.harvest_cost(h)*area

    # total biomassa which harvested
    # total_pl = sum(pl_harvest(T, n0, sr, partial, doc))

    total_pl = obj.harvested_population()*area


    bonusses[T] = bonus * total_pl
    data = np.array([energy, probiotics, others, harvest, feeds, bonusses, labor])
    aggregate = data.sum(axis=1)/data.sum() 

    # total_biomassa = sum(biomass_harvest(T, biomassa, doc)) 
    total_biomassa = obj.biomass_harvest()/1000

    cost_perkg = data.sum()/total_biomassa
    cost_perpl = data.sum()/total_pl

    total_revenue = sum(realized_revenue) * area
    profit = total_revenue - data.sum()
    try:
        revenue_perpl = total_revenue/total_pl
    except:
        revenue_perpl = 0

    return_opex = profit/data.sum()
    margin = profit/total_revenue

    ### get profit for each time
    cost_t = [data[:, :t].sum() for t in times]
    cum_revenue = np.cumsum(realized_revenue) * area
    profit_t = cum_revenue - cost_t

    yeild = (total_biomassa/1000)/(area/10000) #ton/ha
    fcr_t = sum(fcr)
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