# Ordena o DataFrame por data de envio (ordem crescente)
dados_df['noau_dt_envio'] = pd.to_datetime(dados_df['noau_dt_envio'])
dados_df.sort_values('noau_dt_envio', inplace=True)