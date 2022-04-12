import numpy as np
from sklearn.preprocessing import MinMaxScaler


class DSC2Info:
    def __init__(self, dataset):
        working_df = dataset.dataframe.copy()

        space = 1.0 / dataset.vertex_count
        space_array = np.repeat(space, repeats=dataset.vertex_count)
        #space_array[0] = 80

        scaler = MinMaxScaler((0, space))
        working_df[dataset.attribute_names] = scaler.fit_transform(working_df[dataset.attribute_names])

        for name in dataset.class_names:
            df_name = working_df[working_df['class'] == name]
            df_name = df_name.drop(columns='class', axis=1)

            # positions
            values = df_name.to_numpy()
            values = values.ravel()
            values = np.reshape(values, (-1, 2))

            scaffolds = np.asarray([[0, 0]])
            for i in range(len(df_name.index) * dataset.vertex_count):
                if i % dataset.vertex_count == 0:
                    scaffolds = np.append(scaffolds, [[-1 + values[i][0], -1 + values[i][1]]], 0)
                else:
                    scaffolds = np.append(scaffolds, [[scaffolds[i][0] + values[i][0], scaffolds[i][1] + values[i][1]]], 0)

            scaffolds = np.delete(scaffolds, 0, 0)
            dataset.positions.append(scaffolds)

        dataset.axis_positions = [[-1, -1], [-1, 1], [-1, -1], [1, -1]]
        dataset.axis_count = 2

