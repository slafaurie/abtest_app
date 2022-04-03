import pandas as pd
import streamlit as st
from signf_app.analyzer import Analyzer
from signf_app.common import VarTypes
from signf_app.loader import Loader

# Streamlit docs
# https://docs.streamlit.io/library/api-reference/charts/st.pyplot
# inspiration https://share.streamlit.io/streamlit/example-app-ab-testing/main

################################ Funcs

@st.cache
def load_data(path, format='sql'):
    loader = Loader()
    loader.auth()
    try:
        data = loader.load_test_data(path, format)
    except Exception as e:
        print(e)
        data = pd.DataFrame()

    return data

def generate_msg_smr(p_val, alpha):
    # TODO add docstring
    warning = True
    if p_val < alpha:
        msg = 'Warning. SRM may be present.'
    else:
        msg =  'Probably no SRM.'
        warning = False
    return msg, warning

def generate_msg_power(power, min_power):
    msg = f'Power is {power:.2f}.'
    warning = True
    if power < min_power:
        msg += 'Warning. Test has low Power.'
    else:
        msg = 'Test has enough power'
        warning = False
    return msg, warning

def check_significance(p_val, alpha):
    return "YES" if p_val < alpha else "NO"

@st.cache
def do_h0_testing(analyzer):
    return analyzer.do_h0_testing(figsize=(800,500))


################################
st.write(
    """
# 📊 A/B Testing App
Upload your experiment results to see the significance of your A/B test.
"""
)



path = st.file_uploader("Load the test data", type='.csv')

if not path:
    st.stop()

################################

data = load_data(path, 'csv')
st.markdown("### Data preview")
st.dataframe(data.head())

st.markdown("### Select Column for analysis")
var_to_test = st.selectbox("Choose variable", data.select_dtypes(include='number').columns)
vart_type = st.radio("Choose variable", ('continuous', 'proportion'))


with st.expander("Adjust test parameters"):
        st.markdown("### Parameters")

        alpha = st.slider(
            "Significance level (α)",
            min_value=0.01,
            max_value=0.10,
            value=0.05,
            step=0.01,
            key="alpha",
            help="Percent of the time a difference will be detected, assuming one does NOT exist",
        )

        power = st.slider(
            "Power level (1−β)",
            min_value=0.01,
            max_value=1.0,
            value=0.8,
            step=0.01,
            key="power",
            help="Percent of the time the minimum effect size will be detected, assuming it exists",
        )

 
if not st.button('Run Test'):
    st.stop()

################################

analyzer = Analyzer(
    data = data,
    var_to_analyze = var_to_test,
    var_type = vart_type,
    alpha=alpha,
    power = power
)


st.markdown("### Sanity Checks")
smr_p_val, power_val = analyzer.do_sanity_checks()
smr_msg, warning = generate_msg_smr(smr_p_val, analyzer.alpha)

st.markdown("#### Sample Ratio Mismatch (SMR)")
if warning:
    st.warning(smr_msg)
else:
    st.info(smr_msg)

################################

st.markdown("### H0 Testing")
col1, col2 = st.columns(2)
# TODO -> figsize as an input


effect, p_val, f = do_h0_testing(analyzer)

with col1:
    st.metric(
        label="Average Treatment Effect",
        value = analyzer.variant_series.mean(),
        delta = effect

    )

with col2:
    st.metric("Significant?", value=check_significance(p_val, analyzer.alpha))

st.plotly_chart(f)


################################

if analyzer.var_type == VarTypes.PROPORTION.value:
    st.dataframe(Loader.aggregate_by_conversion(analyzer.data, analyzer.var_to_analyze))
    st.stop()

else:
    st.markdown("### Histogram and Quantile Treatment Effect")
    # # TODO -> figsize as an input
    hist_plot = analyzer.plot_histogram_treatment_effect(figsize=(800,500))
    st.plotly_chart(hist_plot)


    # # TODO -> figsize as an input
    quantile_plot = analyzer.do_quantile_treatment_effect(figsize=(800,500))
    st.plotly_chart(quantile_plot)