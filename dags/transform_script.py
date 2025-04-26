import pandas as pd
from tqdm import tqdm

def transform(profit_table, date, product=None):
    """
    Собирает таблицу флагов активности по продуктам.
    Если передан product — рассчитывает только для него.
    """
    start_date = pd.to_datetime(date) - pd.DateOffset(months=2)
    end_date = pd.to_datetime(date) + pd.DateOffset(months=1)
    date_list = pd.date_range(
        start=start_date, end=end_date, freq='M'
    ).strftime('%Y-%m-01')

    filtered = profit_table[profit_table['date'].isin(date_list)]
    if 'date' in filtered.columns:
        filtered = filtered.drop(columns='date')

    df_tmp = filtered.groupby('id').sum()

    if product:
        df_tmp[f'flag_{product}'] = (
            df_tmp.apply(
                lambda x: x[f'sum_{product}'] != 0 and x[f'count_{product}'] != 0,
                axis=1
            ).astype(int)
        )
        df_tmp = df_tmp[[f'flag_{product}']].reset_index()
    else:
        product_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
        for p in tqdm(product_list):
            df_tmp[f'flag_{p}'] = (
                df_tmp.apply(
                    lambda x: x[f'sum_{p}'] != 0 and x[f'count_{p}'] != 0,
                    axis=1
                ).astype(int)
            )
        df_tmp = df_tmp.filter(regex='flag').reset_index()
        df_tmp['calc_date'] = date

    return df_tmp