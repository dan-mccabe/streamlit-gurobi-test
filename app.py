import streamlit as st
import pyomo.environ as pyo
import numpy as np
import gurobipy as gp
import os

try:
    # Set up the Gurobi environment with the WLS license
    e = gp.Env(empty=True)

    wlsaccessID = os.getenv('GRB_WLSACCESSID','undefined')
    e.setParam('WLSACCESSID', wlsaccessID)

    licenseID = os.getenv('GRB_LICENSEID', '0')
    e.setParam('LICENSEID', int(licenseID))

    wlsSecrets = os.getenv('GRB_WLSSECRET','undefined')
    e.setParam('WLSSECRET', wlsSecrets)

    e.setParam('CSCLIENTLOG', int(3))

    e.start()

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')

st.title('Test app with Gurobi, Streamlit, and Docker')

solver = pyo.SolverFactory('gurobi', solver_io='python')

st.write('Initialized solver successfully!')

# Create a simple knapsack problem
n = st.slider(
    'Select the number of items in the knapsack problem', 5, 10000)
r = np.random.randint(10, size=n)
w = np.random.randint(10, size=n)
cap = 3*n
m = pyo.ConcreteModel()
items = list(range(n))
m.ks_items = pyo.Set(initialize=items)
m.x = pyo.Var(m.ks_items, within=pyo.Binary, initialize=0)

m.obj = pyo.Objective(expr=sum(r[i]*m.x[i] for i in m.ks_items), sense=-1)
m.weight_constr = pyo.Constraint(
    expr=sum(w[i]*m.x[i] for i in m.ks_items) <= cap)

results = solver.solve(m)
try:
    st.success('Model solved! Objective value: {}'.format(
        int(pyo.value(m.obj))))
except ValueError as verr:
    st.write(verr)
    st.write(results.solver.status)
    st.write(results.solver.termination_condition)

