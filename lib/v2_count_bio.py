from lib.v2.parameter_estimation import ParemeterEstimation

estimator = ParemeterEstimation(path = "data/growth_full2.csv", sep=";", col_temp="Temp", col_uia="NH4", col_do="DO", col_doc="DOC")

# intial setup
estimator.set_data_for_interpolation(path = "data/biochem.csv")
estimator.set_conditional_parameter(cond_temp=(25, 28, 32, 33), cond_uia=(0, 0.0001, 0.06, 1),
                                cond_do=(4, 6, 9, 10), cond_csc=(0, 0, 0.5, 3))
estimator.set_food_availablelity_data()
estimator.set_growth_paremater(w0=0.05, wn=40, n0=100, sr=0.92)
estimator.set_partial_harvest_parameter(doc=[60, 90, 100], ph=[0.1, 0.1, 0.1], final_doc=120)
estimator.set_pond_data(area=1000)

estimator.fit()