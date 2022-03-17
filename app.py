from lib.body_weight import body_weight_section

body_weight_section()

# options = {
#     "xAxis": {
#         "type": "category",
#         "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
#     },
#     "yAxis": {"type": "value"},
#     "series": [
#         {"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line"}
#     ],
# }

# pie_option = {
#   "tooltip": {
#     "trigger": 'item'
#   },
# #   "legend": {
# #     "top": '5%',
# #     "left": 'center'
# #   },
#   "series": [
#     {
#       "name": 'Access From',
#       "type": 'pie',
#       "radius": ['40%', '70%'],
#       "avoidLabelOverlap": False,
#       "label": {
#         "show": False,
#         "position": 'center'
#       },
#       "emphasis": {
#         "label": {
#         #   // show: true,
#           "fontSize": '40',
#           "fontWeight": 'bold'
#         }
#       },
#       "labelLine": {
#         "show": False
#       },
#       "data": [
#         { "value": 1048, "name": 'Search Engine' },
#         { "value": 735, "name": 'Direct' },
#         { "value": 580, "name": 'Email' },
#         { "value": 484, "name": 'Union Ads' },
#         { "value": 300, "name": 'Video Ads' }
#       ]
#     }
#   ]
# }

# bar_option = {
#   "xAxis": {
#     "type": 'category',
#     "data": ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
#   },
#   "yAxis": {
#     "type": 'value'
#   },
#   "series": [
#     {
#       "data": [120, 200, 150, 80, 70, 110, 130],
#       "type": 'bar'
#     }
#   ]
# }

# scatter_option = {
#   "xAxis": {},
#   "yAxis": {},
#   "series": [
#     {
#       "symbolSize": 20,
#       "data": [
#         [10.0, 8.04],
#         [8.07, 6.95],
#         [13.0, 7.58],
#         [9.05, 8.81],
#         [11.0, 8.33],
#         [14.0, 7.66],
#         [13.4, 6.81],
#         [10.0, 6.33],
#         [14.0, 8.96],
#         [12.5, 6.82],
#         [9.15, 7.2],
#         [11.5, 7.2],
#         [3.03, 4.23],
#         [12.2, 7.83],
#         [2.02, 4.47],
#         [1.05, 3.33],
#         [4.05, 4.96],
#         [6.03, 7.24],
#         [12.0, 6.26],
#         [12.0, 8.84],
#         [7.08, 5.82],
#         [5.02, 5.68]
#       ],
#       "type": 'scatter'
#     }
#   ]
# }
# st.title("Prototype Dashboard")

# st.sidebar.text_input("Sign Your Idea")

# col1, col2 = st.columns([2, 1])

# with col1:
#     st_echarts(options=options)

# with col2:
#     st_echarts(options=pie_option)

# st_echarts(options=bar_option)

# st_echarts(options=scatter_option)