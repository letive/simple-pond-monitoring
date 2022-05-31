from lib.quality_scoring import data_scoring, single_data_scoring
import pandas as pd
import numpy as np

# def aggregator(data: list):
#     df = pd.DataFrame({ 
#         "sal_score_m": sal_m,
#         "w_sal_score_m": w_sal_m,
#         "sal_score_a": sal_a,
#         "w_sal_score_a": w_sal_a,

#         "ph_score_m": ph_m,
#         "w_ph_score_m": w_ph_m,

#         "ph_score_a": ph_a,
#         "w_ph_score_a": w_ph_a,

#         "temperature_score_m": temp_m,
#         "temperature_score_a": temp_a,
#         "w_temp_m": w_temp_m,
#         "w_temp_a": w_temp_a,
#     })
#     return data



def water_quality_index(df):
    """
    df: Dataframe of parameters
    """
    cols = [col for col in df.columns if 'w_' in col]
    df =  df[cols]
    quality = df.sum(axis=1).tolist()
    alert = []
    x,_ = df.shape
    for i in range(x):
        count_positive = np.count_nonzero(df.loc[i] >= 0)
        if count_positive != df.loc[i].count():
            alert.append(df.loc[i].sum()*-1)
        else:
            alert.append(df.loc[i].sum())
    
    return quality, alert


class Scoring:

    def __init__(self, bio: pd.DataFrame, chem: pd.DataFrame):
        self.bio = bio 
        self.chem = chem

    def _pH(self, suitable_min, suitable_max, optimal_min, optimal_max, limit, weight=1):
        ph_m, ph_a, w_ph_m, w_ph_a = data_scoring(
            self.bio["pH_p"], 
            self.bio["pH_p.1"], 
            suitable_min, 
            suitable_max, 
            optimal_min, 
            optimal_max, 
            limit, 
            weight
        )
        return ph_m, ph_a, w_ph_m, w_ph_a         

    def _temperature(self, suitable_min, suitable_max, optimal_min, optimal_max, limit, weight=1):
        temp_m, temp_a, w_temp_m, w_temp_a = data_scoring(
            self.bio["Suhu_p"], 
            self.bio["Suhu_s"], 
            suitable_min, 
            suitable_max, 
            optimal_min, 
            optimal_max, 
            limit, 
            weight
        )
        return temp_m, temp_a, w_temp_m, w_temp_a

    def _salinity(self, suitable_min, suitable_max, optimal_min, optimal_max, limit, weight=1):
        sal_m, sal_a, w_sal_m, w_sal_a = data_scoring(
            self.bio["Salinitas_p"], 
            self.bio["Salinitas_s"], 
            suitable_min, 
            suitable_max, 
            optimal_min, 
            optimal_max, 
            limit, 
            weight
        )
        return sal_m, sal_a, w_sal_m, w_sal_a

    def _do(self, suitable_min, suitable_max, optimal_min, optimal_max, limit, weight=1):
        do_s, do_m, w_do_s, w_do_m = data_scoring(
            self.bio["DO_s"], 
            self.bio["DO_m"], 
            suitable_min, 
            suitable_max, 
            optimal_min, 
            optimal_max, 
            limit, 
            weight
        )
        return do_s, do_m, w_do_s, w_do_m

    # def _unionized_ammonia(suitable_min, suitable_max, optimal_min, optimal_max, limit, weight=1):
    #     pass 

    def _alkalinity(self, suitable_min, suitable_max, optimal_min, optimal_max, limit, weight=1):
        alk, w_alk = single_data_scoring(
            self.chem["Alkalinitas"],
            suitable_min, 
            suitable_max, 
            optimal_min, 
            optimal_max, 
            limit, 
            weight
        )
        return alk, w_alk

    def _no2(self, suitable_min, suitable_max, optimal_min, optimal_max, limit, weight=1):
        no2_m, no2_a, w_no2_m, w_no2_a = data_scoring(
            self.chem["NO2_p"], 
            self.chem["NO2_s"], 
            suitable_min, 
            suitable_max, 
            optimal_min, 
            optimal_max, 
            limit, 
            weight
        )
        return no2_m, no2_a, w_no2_m, w_no2_a

    def _no3(self, suitable_min, suitable_max, optimal_min, optimal_max, limit, weight=1):
        no3_m, no3_a, w_no3_m, w_no3_a = data_scoring(
            self.chem["NO3_p"], 
            self.chem["NO3_s"],
            suitable_min, 
            suitable_max, 
            optimal_min, 
            optimal_max, 
            limit, 
            weight
        )
        return no3_m, no3_a, w_no3_m, w_no3_a

    def _nh4(self, suitable_min, suitable_max, optimal_min, optimal_max, limit, weight=1):
        nh_m, nh_a, w_nh_m, w_nh_a = data_scoring(
            self.chem["NH4_p"], 
            self.chem["NH4_s"],
            suitable_min, 
            suitable_max, 
            optimal_min, 
            optimal_max, 
            limit, 
            weight
        )
        return nh_m, nh_a, w_nh_m, w_nh_a

    def _tom(self, suitable_min, suitable_max, optimal_min, optimal_max, limit, weight=1):
        tom_m, w_tom_m = single_data_scoring(
            self.chem["TOM"],
            suitable_min, 
            suitable_max, 
            optimal_min, 
            optimal_max, 
            limit, 
            weight
        )
        return tom_m, w_tom_m

    def _plankton(self, suitable_min, suitable_max, optimal_min, optimal_max, limit, weight=1):
        plank_p = self.bio["plankton_p"].str.replace(",", "").astype(float)
        plank_s = self.bio["plankton_s"].str.replace(",", "").astype(float)
        plank_m, plank_a, w_plank_m, w_plank_a =data_scoring(
            plank_p,
            plank_s,
            suitable_min, 
            suitable_max, 
            optimal_min, 
            optimal_max, 
            limit, 
            weight
        )

        return plank_m, plank_a, w_plank_m, w_plank_a