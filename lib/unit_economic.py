from lib.uem.metrices import Compute
from lib.uem.biomass import Biomassa
from lib.helpers_mod import price_function, source_data, score_csc_compute
from lib.uem.feeding_rate import feeding_rate
from lib.uem.cost_construction import ConstantCost
import numpy as np

def set_global_variable(
    temp_suit_min=25,
    temp_suit_max=33,
    temp_opt_min=28,
    temp_opt_max=32,
    do_suit_min=4,
    do_suit_max=10,
    do_opt_min=6,
    do_opt_max=9,
    ua_suit_min=0.00,
    ua_suit_max=0.16,
    ua_opt_min=0.00,
    ua_opt_max=0.06,
    csc_suit_min = 0.00,
    csc_suit_max = 5,
    csc_opt_min = 0.00,
    csc_opt_max = 3,
    chem_path = "data/data_chemical_v2.csv",
    bio_path = "data/data_sample - biological.csv"
):
    global f
    global f_uia, f_o2, f_temp, temperature
    global csc_suitable_min, csc_suitable_max, csc_optimal_min, csc_optimal_max

    f = price_function("data/fixed_price.csv")

    f_uia, f_o2, f_temp, temperature = source_data(
        path = None,
        temp_suitable_min=temp_suit_min,
        temp_suitable_max=temp_suit_max,
        temp_optimal_min=temp_opt_min,
        temp_optimal_max=temp_opt_max,
        do_suitable_min=do_suit_min,
        do_suitable_max=do_suit_max,
        do_optimal_min=do_opt_min,
        do_optimal_max=do_opt_max,
        ua_suitable_min=ua_suit_min,
        ua_suitable_max=ua_suit_max,
        ua_optimal_min=ua_opt_min,
        ua_optimal_max=ua_opt_max,
        chemical_path = chem_path,
        biological_path = bio_path
    )


    csc_suitable_min = csc_suit_min
    csc_suitable_max = csc_suit_max
    csc_optimal_min = csc_opt_min
    csc_optimal_max = csc_opt_max


def revenue(t0, T, area, wn, w0, alpha, n0, sr, partial, doc, final_doc=120, **kwargs):

    m = -np.log(sr) / T
    weight = []
    biomassa = []
    revenue = []
    potential_revenue = []
    population = []

    adg = []
    feed_formula = []
    feed_cost = []
    harvest_population = []
    harvest_biomass = []
    harvest_cost = []

    cum_integral = 0
    growth_curve = []

    for i in range(T + 1):
        if i == 0:
            score_csc = score_csc_compute(
                0 / 1000, 0.01, csc_suitable_min, csc_suitable_max, csc_optimal_max
            )
            feedRate = feeding_rate(
                0, float(temperature[temperature["DOC"] == i - 1]["Suhu_s"]), 0
            )
            obj = Biomassa(
                t0,
                i,
                wn,
                w0,
                alpha,
                n0,
                sr,
                m,
                partial,
                doc,
                f_uia,
                f_o2,
                f_temp,
                score_csc,
                feedRate,
                cum_integral,
                final_doc,
            )
            wt = obj.wt()
            nt = obj.population()
            biomass = obj.biomassa()
            constant_biomass = obj.biomassa_constant()

            cum_integral = obj._fr()
            ph = Compute(t0, i, doc, wt, nt, biomass, 0, constant_biomass, final_doc)
        else:
            score_csc = score_csc_compute(
                biomassa[-1] / 1000,
                1000,
                csc_suitable_min,
                csc_suitable_max,
                csc_optimal_max,
            )
            feedRate = feeding_rate(
                weight[-1],
                float(temperature[temperature["DOC"] == i - 1]["Suhu_s"]),
                biomassa[-1] / 1000,
            )
            obj = Biomassa(
                i - 1,
                i,
                wn,
                w0,
                alpha,
                n0,
                sr,
                m,
                partial,
                doc,
                f_uia,
                f_o2,
                f_temp,
                score_csc,
                feedRate,
                cum_integral,
                final_doc,
            )
            wt = obj.wt()
            nt = obj.population()
            biomass = obj.biomassa()
            constant_biomass = obj.biomassa_constant()

            cum_integral = obj._fr()
            
            ph = Compute(
                t0, i, doc, wt, nt, biomass, biomassa[-1]*1000/area, constant_biomass, final_doc
            )

        weight.append(wt)
        biomassa.append(biomass * area / 1000)

        population.append(nt * area)
        revenue.append(ph.realized_revenue(f) * area)
        potential_revenue.append(ph.potential_revenue(f) * area)

        growth_curve.append(cum_integral)

        adg.append(ph.adg())
        feed_formula.append(ph._feeding_formula(kwargs["formula"], kwargs["r"]) * area)
        feed_cost.append(
            ph.feeding_expense(kwargs["fc"], kwargs["formula"], kwargs["r"]) * area
        )
        harvest_population.append(ph.harvest_population() * area)
        harvest_biomass.append(ph.harvest_biomass() * area)
        harvest_cost.append(ph.harvest_expense(kwargs["h"]) * area)

    result = {
        "body_weight": weight,
        "population": population,
        "biomassa": biomassa,
        "potential_revenue": potential_revenue,
        "realized_revenue": revenue,
        "cumulative_revenue": np.cumsum(np.array(revenue)).tolist(),
        "total_revenue": sum(revenue),
        "adg": adg,
        "feed_formula": feed_formula,
        "feed_cost": feed_cost,
        "harvest_population": harvest_population,
        "harvest_biomass": harvest_biomass,
        "harvest_cost": harvest_cost,
        "growth_curve": growth_curve
    }

    return result


def cost_structure(
    t0,
    T,
    area,
    wn,
    w0,
    alpha,
    n0,
    sr,
    partial,
    doc,
    e,
    p,
    o,
    labor,
    bonus,
    h,
    r,
    fc,
    formula,
    final_doc=120,
):

    energy_cost = []
    probiotics_cost = []
    others_cost = []
    bonusses_cost = [0] * (T + 1)
    labor_cost = []

    for t in range(T + 1):
        sub_cost = ConstantCost(t, final_doc)
        energy_cost.append(sub_cost.energy_cost(e))
        probiotics_cost.append(sub_cost.probiotic_cost(p))
        others_cost.append(sub_cost.other_cost(o))
        labor_cost.append(sub_cost.labor_cost(labor))

    data = revenue(
        t0,
        T,
        area,
        wn,
        w0,
        alpha,
        n0,
        sr,
        partial,
        doc,
        final_doc,
        r=r,
        fc=fc,
        formula=formula,
        h=h,
    )
    cum_harvest_biomass = np.cumsum(data["harvest_biomass"])
    harvest_population = data["harvest_population"]

    bonusses_cost[T] = bonus * cum_harvest_biomass[-1]
    data_cost = np.array(
        [
            energy_cost,
            probiotics_cost,
            others_cost,
            data["harvest_cost"],
            data["feed_cost"],
            bonusses_cost,
            labor_cost,
        ]
    )

    total_cost = data_cost.sum()

    aggregate = data_cost.sum(axis=1) / total_cost
    cost_perkg = total_cost / cum_harvest_biomass[-1]
    cost_perpl = total_cost / sum(harvest_population)
    total_revenue = data["total_revenue"]
    profit = total_revenue - total_cost

    try:
        revenue_perpl = total_revenue / sum(harvest_population)
    except:
        revenue_perpl = 0

    return_opex = profit / total_cost
    margin = profit / total_revenue

    ### get profit for each time
    cost_t = np.array([data_cost[:, :ti].sum() for ti in range(T + 1)])
    cum_revenue = data["cumulative_revenue"]
    profit_t = cum_revenue - cost_t

    yeild = round(((cum_harvest_biomass[-1]) / 1000) / (area / 10000), 2)  # ton/ha
    fcr_t = round(np.cumsum(data["feed_formula"])[-1] / cum_harvest_biomass[-1], 2)

    result = {
        "index": [
            "energy_cost",
            "probiotics_cost",
            "others_cost",
            "harvest_cost",
            "feed_cost",
            "bonusses",
            "labor_cost",
        ],
        "data": data_cost.transpose().tolist(),
        "aggregate": aggregate.tolist(),
        "matrix": {
            "costPerKg": "Rp {:,.2f}".format(cost_perkg),
            "costPerPl": "Rp {:,.2f}".format(cost_perpl),
            "totalCost": "Rp {:,.2f}".format(total_cost),
            "totalRevenue": "Rp {:,.2f}".format(total_revenue),
            "profit": "Rp {:,.2f}".format(profit),
            "revenuePerPl": "Rp {:,.2f}".format(revenue_perpl),
            "returnOnOpex": return_opex,
            "margin": margin,
            "yeild": yeild,
            "adg": data["adg"][T],
            "fcr": fcr_t,
        },
        "data_profit": {
            "revenue": cum_revenue,
            "cost": cost_t.tolist(),
            "profit": profit_t.tolist(),
        },
        "revenue": {
            "biomassa": data["biomassa"],
            "revenue": data["cumulative_revenue"],
            "potential_revenue": data["potential_revenue"],
            "body_weight": data["body_weight"],
            "population": data["population"],
            "fr": data["growth_curve"]
        },
    }
    return result
