import matplotlib.pyplot as plt
import geopandas as gpd


# Liste der Farben für die Gemeinden
farben = {
    'Meilen': 'blue',
    'Egg': 'green',
    'Uster': 'red'
}
def plot_points(ax, punkt, farbe, label):
    ax.scatter(punkt.x, punkt.y, color=farbe, label=label)

def plot_demand_distribution(gemeindengrenzen_gdf, gemeinden_zentral_gdfs,
                             gemeinden_höhere_Dichte_gdfs, gemeinden_niedrige_Dichte_gdfs,
                             strassennetz_gdf, alle_punkte):

    fig, ax = plt.subplots(figsize=(10, 10))
    gemeindengrenzen_gdf.plot(ax=ax, color='black', edgecolor='black', alpha=0.5, label='Gemeindengrenzen')
    gemeinden_zentral_gdfs.plot(ax=ax, color='orange', edgecolor='gray', alpha=0.5, label='Zentral')
    gemeinden_höhere_Dichte_gdfs.plot(ax=ax, color='lightblue', edgecolor='gray', alpha=0.5, label='Höhere Dichte')
    gemeinden_niedrige_Dichte_gdfs.plot(ax=ax, color='lightgreen', edgecolor='gray', alpha=0.5, label='Niedrige Dichte')

    strassennetz_gdf.plot(ax=ax, color='gray', alpha=0.5, label='Straßennetz')
    plt.title('Verteilung der Nachfragepunkte in den Zonen')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    legend_labels = set()

    for index, row in alle_punkte.iterrows():
        punkt = row.geometry
        gemeinde = row.gemeinde
        if gemeinde not in legend_labels:
            plot_points(ax, punkt, farben[gemeinde], gemeinde)
            legend_labels.add(gemeinde)
        else:
            plot_points(ax, punkt, farben[gemeinde], None)

    ax.set_xlim([strassennetz_gdf.total_bounds[0], strassennetz_gdf.total_bounds[2]])
    ax.set_ylim([strassennetz_gdf.total_bounds[1], strassennetz_gdf.total_bounds[3]])
    ax.legend(title='Legende', loc='upper left')  # Legende außerhalb der Schleife platzieren

    plt.show()

