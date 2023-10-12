import base64
from io import BytesIO

import pandas as pd
import matplotlib.pyplot as plt


def get_table(data: dict, cell_colors: dict, col_colors: dict, default_cell_color='white'):
    plt.figure(figsize=(6, 4))
    df = pd.DataFrame(data)
    plt.axis('off')

    # Create a table with cell colors
    cell_colors_list = [[cell_colors.get((i, j), default_cell_color) for j in range(len(df.columns))] for i in range(len(df))]
    table = plt.table(cellText=df.values, colLabels=df.columns, cellLoc='center', cellColours=cell_colors_list, loc='upper left')

    # Set column header colors
    for j, label in enumerate(df.columns):
        table[0, j].set_facecolor(col_colors.get(j, 'white'))

    img_bytes = BytesIO()

    plt.savefig(img_bytes, format='png', bbox_inches='tight', pad_inches=0.2)
    plt.close()
    img_bytes.seek(0)
    return img_bytes