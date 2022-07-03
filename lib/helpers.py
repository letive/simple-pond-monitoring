import pandas as pd
import numpy as np
from scipy.interpolate import CubicSpline


def heaviside_step(x):
    return np.heaviside([x], 1)[0]


def normal_trapezoidal(m, suitable_min, suitable_max, optimal_min, optimal_max):
    """
    m: value in t
    """
    if np.isnan(m):
        ret = 0.25
    elif (m < suitable_min) or (m > suitable_max):
        ret = 0
    else:
        ret = min(
            (
                (m - suitable_min) / (optimal_min - suitable_min),
                1,
                (suitable_max - m) / (suitable_max - optimal_max),
            )
        )

    return ret


def left_trapezoidal(m, suitable_min, suitable_max, optimal_max):
    """
    m: value in t
    """
    if np.isnan(m):
        ret = 0.25
    elif (m < suitable_min) or (m > suitable_max):
        ret = 0
    else:
        ret = min((1, (suitable_max - m) / (suitable_max - optimal_max)))

    return ret


def source_data(**kwargs):
    if kwargs["path"]:
        df = pd.read_csv(kwargs["path"], sep=";") #Temp;DO;NH4;NO2;ABW;DOC
        doc = df["DOC"].tolist()
        score_uia = []
        score_o2 = []
        score_temp = []

        for i in doc:
            score_uia.append(
                left_trapezoidal(
                    df[df["DOC"] == i]["NH4"].values[0],
                    kwargs["ua_suitable_min"],
                    kwargs["ua_suitable_max"],
                    kwargs["ua_optimal_max"],
                )
            )

            score_o2.append(
                normal_trapezoidal(
                    df[df["DOC"] == i]["DO"].values[0],
                    kwargs["do_suitable_min"],
                    kwargs["do_suitable_max"],
                    kwargs["do_optimal_min"],
                    kwargs["do_optimal_max"],
                )
            )

            score_temp.append(
                normal_trapezoidal(
                    df[df["DOC"] == i]["Temp"].values[0],
                    kwargs["temp_suitable_min"],
                    kwargs["temp_suitable_max"],
                    kwargs["temp_optimal_min"],
                    kwargs["temp_optimal_max"],
                )
            )

            suhu = df[["DOC", "Temp"]]

    else:
        try:
            chem = pd.read_csv(kwargs["chemical_path"])
            bio = pd.read_csv(kwargs["biological_path"])

            bio.replace("-", np.nan, inplace=True)
            bio.fillna(np.nan, inplace=True)
            
            chem.replace("-", np.nan, inplace=True)
            chem.fillna(np.nan, inplace=True)
        except:
            chem = pd.read_csv("data/data_chemical_v2.csv")
            bio = pd.read_csv("data/data_sample - biological.csv")

        doc = chem["Doc"].tolist()

        score_uia = []
        score_o2 = []
        score_temp = []

        for i in doc:
            score_uia.append(
                left_trapezoidal(
                    chem[chem["Doc"] == i]["uia"].values[0],
                    kwargs["ua_suitable_min"],
                    kwargs["ua_suitable_max"],
                    kwargs["ua_optimal_max"],
                )
            )

            score_o2.append(
                normal_trapezoidal(
                    bio[bio["DOC"] == i]["DO_s"].values[0],
                    kwargs["do_suitable_min"],
                    kwargs["do_suitable_max"],
                    kwargs["do_optimal_min"],
                    kwargs["do_optimal_max"],
                )
            )

            score_temp.append(
                normal_trapezoidal(
                    bio[bio["DOC"] == i]["Suhu_s"].values[0],
                    kwargs["temp_suitable_min"],
                    kwargs["temp_suitable_max"],
                    kwargs["temp_optimal_min"],
                    kwargs["temp_optimal_max"],
                )
            )

            suhu = bio[["DOC", "Suhu_s"]]

    f_uia = CubicSpline(doc, score_uia)
    f_o2 = CubicSpline(doc, score_o2)
    f_temp = CubicSpline(doc, score_temp)

    

    return f_uia, f_o2, f_temp, suhu


def score_csc_compute(
    biomass, volume, csc_suitable_min=0.00, csc_suitable_max=5, csc_optimal_max=3
):

    return left_trapezoidal(
        biomass / volume, csc_suitable_min, csc_suitable_max, csc_optimal_max
    )


def price_function(path, sep=";", col_size="size_count", col_price="price"):
    """
    path: path file for the price's data
    sep: delimiter/separator for the csv file
    col_size: columns name for size count of shrimp
    col_price: columns name for price of shrimp
    """
    df = pd.read_csv(path, sep=sep)
    x_sample = df[col_size].tolist()[::-1]
    y_sample = df[col_price].tolist()[::-1]
    f = CubicSpline(x_sample, y_sample, bc_type="natural")
    return f


def feed_formula3(path, sep=";", colname="Formula 3"):
    df = pd.read_csv(path, sep=sep)
    return df[colname].tolist()
