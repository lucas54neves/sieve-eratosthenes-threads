import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

def read_data():
    data = []

    with open('../doc/log.txt', 'r') as file_log:
        line = file_log.readline()

        while line:
            data_line = line.split(':')

            time = round(float(data_line[1].split(' seg')[0]), 6)

            number_of_threads = int(data_line[2].split(',')[0])

            limit = int(data_line[3])

            data.append(
                {
                    'time': time,
                    'threads': number_of_threads,
                    'limit': limit
                }
            )

            line = file_log.readline()

        file_log.close()
    
    return pd.DataFrame(data)

def save_data_to_csv(dataframe, csv_path, mode = 'w', header = True):
    dataframe.to_csv(
        csv_path,
        index = False,
        mode = mode,
        header = header
    )

def save_dataframe_to_png(dataframe, image_path):
    fig = ff.create_table(
        dataframe,
        index = True
    )

    fig.update_layout(
        autosize = False,
        width = 600,
        height = 200,
    )

    fig.write_image(
        image_path,
        scale = 2
    )

def get_mean_and_std_by_thread(dataframe):
    data = {}

    for thread in [1, 2, 4, 8]:
        df_by_number_of_threads = dataframe[dataframe['threads'] == thread]

        df_by_number_of_threads_groupby_limit = df_by_number_of_threads.groupby(['limit'])

        processed_data = df_by_number_of_threads_groupby_limit['time'].mean()

        processed_data = processed_data.reset_index()

        processed_data.rename(
            columns = {
                'time': 'mean'
            },
            inplace = True
        )
        std_data = df_by_number_of_threads_groupby_limit['time'].std()

        processed_data['std'] = std_data.reset_index()['time']

        if thread == 1:
            number = 'um'

        if thread == 2:
            number = 'dois'

        if thread == 4:
            number = 'quatro'

        if thread == 8:
            number = 'oito'

        fig = px.line(
            processed_data,
            x = 'limit',
            y = 'mean',
            title = f'Tempo médio por quantidade de números com {number} {"threads" if thread == 1 else "threads"}'
        )

        fig.update_xaxes(
            title_text = 'Quantidade de números'
        )

        fig.update_yaxes(
            title_text = 'Tempo em segundos'
        )

        fig.write_image(f'../images/thread{thread}-mean.png')

        fig = px.line(
            processed_data,
            x = 'limit',
            y = 'std',
            title = f'Desvio padrão por quantidade de números com {number} {"threads" if thread == 1 else "threads"}'
        )

        fig.update_xaxes(
            title_text = 'Quantidade de números'
        )

        fig.update_yaxes(
            title_text = 'Desvio padrão em segundos'
        )

        fig.write_image(f'../images/thread{thread}-std.png')

        processed_data['threads'] = thread

        data[thread] = processed_data

        df_table = processed_data.copy()[['mean', 'std']]

        df_table['mean'] = df_table['mean'].apply(lambda x: round(float(x), 6))

        df_table['std'] = df_table['std'].apply(lambda x: round(float(x), 6))

        df_table.index = [
            '100',
            '1 k',
            '10 k',
            '100 k',
            '1 M',
            '10 M',
            '100 M'
        ]

        df_table.columns = [
            'Tempo médio',
            'Desvio padrão'
        ]

        save_dataframe_to_png(
            df_table,
            f'../images/thread{thread}-table.png'
        )
    
    return data

def save_image_with_mean_and_std_for_all_threads(data):
    for thread, processed_data in data.items():
        if thread == 1:
            data_merged = list(data.values())[0]
        else:
            data_merged = pd.concat(
                [data_merged, processed_data],
                ignore_index = True
            )
    
    fig = px.line(
        data_merged,
        x = 'limit',
        y = 'mean',
        color = 'threads'
    )

    fig.update_layout(
        title = 'Quantidade de números por tempo médio de cada thread',
        xaxis_title = 'Quantidade de números',
        yaxis_title = 'Tempo em segundos',
        legend_title = 'Threads'
    )

    fig.write_image(f'../images/mean-all.png')
    
    return data_merged

def get_speedup_by_thread(data):
    speedup_list = []

    data_thread_1 = data[data['threads'] == 1]

    dict_thread_1 = {}

    def get_dict_thread_1(row):
        dict_thread_1[int(row['limit'])] = row['mean']

    data_thread_1.apply(
        lambda row: get_dict_thread_1(row),
        axis = 1
    )

    def get_speedups(row):
        speedup_list.append(
            {
                'limit': int(row['limit']),
                'threads': int(row['threads']),
                'speedup': dict_thread_1[row['limit']] / row['mean']
            }
        )

    for thread in [2, 4, 8]:
        thread_data = data[data['threads'] == thread]

        thread_data.apply(
            lambda row: get_speedups(row),
            axis = 1
        )
    
    speedup_df = pd.DataFrame(speedup_list)

    speedup_df = speedup_df.astype(
        {
            'limit': int,
            'threads': int
        }
    )
    
    fig = px.line(
        speedup_df,
        x = 'limit',
        y = 'speedup',
        color = 'threads'
    )

    fig.update_layout(
        title = 'Quantidade de números por speedup',
        xaxis_title = 'Quantidade de números',
        yaxis_title = 'Speedup',
        legend_title = 'Threads'
    )

    fig.write_image(f'../images/speedup.png')

    speedup_table_df = pd.DataFrame()

    for thread in [2, 4, 8]:
        thread_list = [data['speedup'] for data in speedup_list if data['threads'] == thread]

        thread_serie = pd.Series(thread_list, name = f'Thread {thread}')

        speedup_table_df = speedup_table_df.append(thread_serie)
    
    speedup_table_df.columns = [
        '100',
        '1 k',
        '10 k',
        '100 k',
        '1 M',
        '10 M',
        '100 M'
    ]

    save_dataframe_to_png(
        speedup_table_df.transpose(),
        '../images/speedup-table.png'
    )

    return speedup_df

def save_images_of_runs(data):
    for thread in [1, 2, 4 , 8]:
        data_thread = data[data['threads'] == thread]

        dict_times_of_runs = {}

        def get_times_of_runs(row):
            if not dict_times_of_runs.get(row['limit']):
                dict_times_of_runs[int(row['limit'])] = []
            
            dict_times_of_runs[row['limit']].append(row['time'])

        data_thread.apply(
            lambda row: get_times_of_runs(row),
            axis = 1
        )

        dataframe = pd.DataFrame(dict_times_of_runs)

        dataframe.index = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        dataframe.columns = [
            '100',
            '1 k',
            '10 k',
            '100 k',
            '1 M',
            '10 M',
            '100 M',
        ]

        save_dataframe_to_png(
            dataframe,
            f'../images/thread{thread}-runs.png'
        )

def calculate_efficiency(data):
    data['efficiency'] = data.apply(
        lambda row: round((row['speedup'] / row['threads']), 6),
        axis = 1
    )

    fig = px.line(
        data,
        x = 'limit',
        y = 'efficiency',
        color = 'threads'
    )

    fig.update_layout(
        title = 'Quantidade de números por eficiência',
        xaxis_title = 'Quantidade de números',
        yaxis_title = 'Eficiência',
        legend_title = 'Threads'
    )

    fig.write_image(f'../images/efficiency.png')

    efficiency_table_df = pd.DataFrame()

    for thread in [2, 4, 8]:
        thread_df = data[data['threads'] == thread]

        thread_list = list(thread_df['efficiency'])

        thread_serie = pd.Series(thread_list, name = f'Thread {thread}')

        efficiency_table_df = efficiency_table_df.append(thread_serie)
    
    efficiency_table_df.columns = [
        '100',
        '1 k',
        '10 k',
        '100 k',
        '1 M',
        '10 M',
        '100 M'
    ]

    save_dataframe_to_png(
        efficiency_table_df.transpose(),
        '../images/efficiency-table.png'
    )

def calculate_karp_flatt_metric(data):
    data['karp_flatt_metric'] = data.apply(
        lambda row: round(((1 / row['speedup']) - (1 / row['threads'])) / (1 - (1 / row['threads'])), 6),
        axis = 1
    )

    fig = px.line(
        data,
        x = 'limit',
        y = 'karp_flatt_metric',
        color = 'threads'
    )

    fig.update_layout(
        title = 'Quantidade de números pela métrica Karp-Flatt',
        xaxis_title = 'Quantidade de números',
        yaxis_title = 'Métrica Karp-Flatt',
        legend_title = 'Threads'
    )

    fig.write_image(f'../images/karp-flatt-metric.png')

    karp_flatt_metric_table_df = pd.DataFrame()

    for thread in [2, 4, 8]:
        thread_df = data[data['threads'] == thread]

        thread_list = list(thread_df['karp_flatt_metric'])

        thread_serie = pd.Series(thread_list, name = f'Thread {thread}')

        karp_flatt_metric_table_df = karp_flatt_metric_table_df.append(thread_serie)
    
    karp_flatt_metric_table_df.columns = [
        '100',
        '1 k',
        '10 k',
        '100 k',
        '1 M',
        '10 M',
        '100 M'
    ]

    save_dataframe_to_png(
        karp_flatt_metric_table_df.transpose(),
        '../images/karp-flatt-metric-table.png'
    )

if __name__ == '__main__':
    data = read_data()
    print('Dados lidos')

    save_data_to_csv(data, '../doc/logs.csv')
    print('Dados salvos como csv')

    save_images_of_runs(data)
    print('Dados dos tempos salvos')

    dict_with_mean_and_std_by_thread = get_mean_and_std_by_thread(data)
    print('Tempo medio e desvio padrao calculados')

    df_with_mean_and_std_all_threads = save_image_with_mean_and_std_for_all_threads(dict_with_mean_and_std_by_thread)
    print('Imagem salda dos tempos medios e desvios padoes de todas threads')

    speedup_df = get_speedup_by_thread(df_with_mean_and_std_all_threads)
    print('Speedup calculados')

    calculate_efficiency(speedup_df)
    print('Eficiencia calculada')

    calculate_karp_flatt_metric(speedup_df)
    print('Metrica calculada')