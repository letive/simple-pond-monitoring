from lib.helpers import source_data, score_csc_compute
from lib.uem.feeding_rate import feeding_rate

from lib.parameter_estimation import Biomassa
from lib.parameter_estimation import f_uia, f_o2, f_temp, temperature
from lib.parameter_estimation import csc_optimal_max, csc_suitable_min, csc_suitable_max

# f_uia, f_o2, f_temp, temperature = source_data(
#     # path = "data/growth_full2.csv",
#     path = None,
#     temp_suitable_min = 25,
#     temp_suitable_max = 33,
#     temp_optimal_min = 28,
#     temp_optimal_max = 32,
#     do_suitable_min = 4,
#     do_suitable_max = 10,
#     do_optimal_min = 6,
#     do_optimal_max = 9,
#     ua_suitable_min = 0.00,
#     ua_suitable_max = 0.16,
#     ua_optimal_min = 0.00,
#     ua_optimal_max = 0.06,
# )

# csc_suitable_min = 0.00
# csc_suitable_max = 5
# csc_optimal_min = 0.00
# csc_optimal_max = 3

def single_wt(t, sr, m, alpha, alpha2, alpha3, alpha4, alpha5,  alpha6, **kwargs):
    try:
        feedRate = feeding_rate(0, float(temperature[temperature["DOC"]==t]["Temp"]), 0)
    except  :
        feedRate = 0

    if t == 0:
        score_csc = score_csc_compute(0/1000, kwargs["n0"]*1, csc_suitable_min, csc_suitable_max, csc_optimal_max)
    else:
        _, bio_1 = single_wt(t-1, sr, m, alpha, alpha2, alpha3, alpha4, alpha5, alpha6, 
                n0=kwargs["n0"], t0=kwargs["t0"], w0=kwargs["w0"], wn=kwargs["wn"], 
                ph=kwargs["ph"], doc=kwargs["doc"], final_doc=kwargs["final_doc"])
        score_csc = score_csc_compute(bio_1/1000, 1000, csc_suitable_min, csc_suitable_max, csc_optimal_max)
        
    obj = Biomassa(kwargs["t0"], t, kwargs["wn"], kwargs["w0"], alpha, kwargs["n0"]*1, sr, m, kwargs["ph"], kwargs["doc"], f_uia, f_o2, f_temp, feedRate, score_csc, 
        alpha2, alpha3, alpha4, alpha5, alpha6, final_doc=kwargs["final_doc"])

    return  obj.wt(), obj.biomassa()