import pandas as pd
import numpy as np
from prophet import Prophet
from scipy.optimize import minimize


def preprocess(uploaded_file, sku_code):
    """
        read csv  -> group by -> add ln / log
    """
    df = pd.read_csv(uploaded_file, parse_dates=['order date'], dayfirst=True)
    df = df[df['sku_code'] == sku_code]

    df = df.groupby('order date').agg({
        'customer ID': 'first',
        'sku_code': 'first',
        'SKU id': 'first',
        'sku_name': 'first',
        'order_qty': 'sum',
        'order_unit': 'first',
        'unit_selling_price': 'first'
    }).reset_index()

    df['ln_order_qty'] = np.log(df['order_qty'])
    df['ln_unit_selling_price'] = np.log(df['unit_selling_price'])
    return df

def calculate_base_sale(df):
    """
        Remove external noise affecting sales
    """
    timestamp_var = "order date"
    baseline_dep_var = "order_qty"
    changepoint_prior_scale_value = 0.3

    # Preparing the datasecloset
    df['ds'] = df[timestamp_var]
    df['y'] = df[baseline_dep_var]
    df['ds'] = pd.to_datetime(df['ds'])

    # Default value is 0.05
    model = Prophet(changepoint_prior_scale= changepoint_prior_scale_value)
    model.fit(df)

    forecast = model.predict(df)
    trend_component = forecast[['ds', 'trend']]  # Extracting only the relevant columns
    df['ds'] = pd.to_datetime(df['ds'])
    df = pd.merge(df, trend_component, how='left', on='ds')
    return df


def calculate_elasticity(df):
    """
        Percentage change in sales for a 1% change in the price.
    """
    x = df
    x["intercept"] = 1
    x = x[["intercept","ln_unit_selling_price","trend"]].values.T
    # x_t = x.T
    actuals = x[2]

    def objective(x0):
        return sum(((x[0]*x0[0] + x[1]*x0[1]) - actuals)**2)

    x0 = [1, -1]

    bounds = ((None, None), (-3,-0.5))

    result = minimize(objective, x0, bounds=bounds, method='L-BFGS-B')

    price_elasticity = result.x[1]
    df["price_elasticity"] = result.x[1]
    return df


def optimize_price(uploaded_file, sku_code):
    """
        Percentage change in sales for a 1% change in the price.
    """
    df = preprocess(uploaded_file, sku_code)

    df = calculate_base_sale(df)
    df = calculate_elasticity(df)

    df["LB_price"] = df["unit_selling_price"] - (0.2*df["unit_selling_price"])
    df["UB_price"] = df["unit_selling_price"] + (0.2*df["unit_selling_price"])

    def objective(opti_price):
        df["opti_price"] = opti_price[0]
        df["optimized_units"] = df["order_qty"] + (
            df["order_qty"] * (
                (df["opti_price"] / df["unit_selling_price"]) - 1
            ) * df["price_elasticity"]
        )
        df["optimized_revenue"] = df["optimized_units"]*df["opti_price"]
        
        return -sum(df["optimized_revenue"])

    opti_price = df["unit_selling_price"][0]
    bounds = ((df["LB_price"][0], df["UB_price"][0]),)
    result = minimize(objective, opti_price, bounds=bounds)
    return df["unit_selling_price"][0], result.x
