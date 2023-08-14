import streamlit as st
import pandas as pd
import numpy as np

games = pd.read_csv(f'https://docs.google.com/spreadsheets/d/1AjuzZDECOTwhLJ_8Q6Jp8DFv11gSJ43dgYUdpcvXueU/export?format=csv&gid=0').assign(game = lambda x: np.where(x['Opponent']!= x['Park'], x['Pitcher'] + ' vs '+ x['Opponent'], x['Pitcher'] + ' @ '+x['Opponent']))['game'].sort_values().to_list()

k_list = [str(x) for x in range(12)] + ['12+']
hit_list = [str(x) for x in range(11)] + ['11+']
bb_list = [str(x) for x in range(6)] + ['6+']
run_list = [str(x) for x in range(7)] + ['7+']
out_list = [str(x) for x in range(8,24)] + ['24+']

prop_ids = {
    'Strikeouts':[0,k_list,5],
    'Hits':[504337972,hit_list,5],
    'Walks':[682826722,bb_list,1],
    'Runs':[2063469959,run_list,2],
    'Outs':[2134418880,out_list,9],
}

# Inputs
player = st.selectbox('Choose a pitcher:', games)
player = player[:-6].strip()
prop = st.selectbox('Choose a prop:', prop_ids.keys())
o_u_val = st.selectbox('Select the Over/Under line:', [int(x)+0.5 for x in prop_ids[prop][1][:-1]], value=prop_ids[prop][2])
u_odds_amer = st.number_input('Under Value (American Odds)', 
                              min_value=-300, max_value=300, value=-115, step=5)
o_odds_amer = st.number_input('Over Value (American Odds)', 
                              min_value=-300, max_value=300, value=-115, step=5)

props = pd.read_csv(f'https://docs.google.com/spreadsheets/d/1AjuzZDECOTwhLJ_8Q6Jp8DFv11gSJ43dgYUdpcvXueU/export?format=csv&gid={prop_ids[prop][0]}')
for val in prop_ids[prop][1]:
    props[val] = props[val].str[:-1].astype('float').div(100)
    
u_val = props.loc[props['Pitcher']==player,
                  [str(x) for x in range(int(o_u_val+0.5))]
                 ].sum(axis=1).item()
o_val = 1-u_val

for side in ['under','over']:
    if side=='under':
        val = u_val
        odds_amer = u_odds_amer
    else:
        val = o_val
        odds_amer = o_odds_amer
    odds_frac = abs(odds_amer)/(abs(odds_amer)+100) if odds_amer<0 else 100/(odds_amer+100)
    odds_frac_vig_adj = odds_frac*215/115/2
    odds_dec = 1/(odds_frac)
    if val <= odds_frac:
        continue

    kelly = (val*odds_dec-1)/(odds_dec-1)*0.2 / 3 # 20% Kelly
    regr_factor = ((val*odds_dec-1)/(odds_dec-1)*val+(1-(val*odds_dec-1)/(odds_dec-1))*odds_frac-odds_frac_vig_adj)/(val-odds_frac_vig_adj)
    regr_pred = regr_factor*val+(1-regr_factor)*odds_frac_vig_adj
    regr_kelly = (regr_pred*odds_dec-1) / (odds_dec-1) / 3 #33% regressed Kelly
    st.write(f'Suggested Bet: {side.title()} @ {regr_kelly*100:.1f}%')
st.write("Individual probabilities found here](https://docs.google.com/spreadsheets/d/1AjuzZDECOTwhLJ_8Q6Jp8DFv11gSJ43dgYUdpcvXueU/edit#gid=0)")
