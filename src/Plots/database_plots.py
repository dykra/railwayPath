from PriceEstimatorComponent.database_handler import execute_sql_statement
import matplotlib.pyplot as plt
import seaborn as sns
import sys

sns.set(style="white")
sns.set(style="whitegrid", color_codes=True)


# TODO -  zaleznosc danych od wyniku (wykresy) : cena , lattitude i longitude :)
def show_statistics(data, column_name, plot_name=""):
    sns.countplot(x=column_name, data=data, palette='hls')
    plt.show()
    if plot_name != "":
        plt.savefig('count_plot')


def show():
    data = execute_sql_statement(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4],
                                 'select Price_Group '
                                 ' FROM FILTERED_PARCEL')
    show_statistics(data, column_name='Price_Group')
