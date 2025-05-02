import folium
import geopandas as gpd


def initialize_map(gdf: gpd.GeoDataFrame) -> folium.Map:
    return folium.Map(
        location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()],
        zoom_start=14,
        tiles="cartodbpositron",
    )


def add_circle_makers(
    folium_map: folium.Map,
    gdf: gpd.GeoDataFrame,
    meters: float,
    label_column: str | None = None,
    group_name: str = "Circles",
) -> folium.Map:
    circle_group = folium.FeatureGroup(name=group_name)
    for _, row in gdf.iterrows():
        folium.CircleMarker(
            location=[row.geometry.centroid.y, row.geometry.centroid.x],
            radius=meters / 10,
            color="black",
            fill_opacity=0.0,
            tooltip=row[label_column] if label_column else None,
        ).add_to(circle_group)
    folium_map.add_child(circle_group)
    return folium_map


def add_heatmap(folium_map: folium.Map, gdf: gpd.GeoDataFrame, data_column: str) -> folium.Map:
    from branca.colormap import linear

    colormap = linear.OrRd_09.scale(gdf[data_column].min(), gdf[data_column].max())

    def style_function(feature):
        score = feature["properties"][data_column]
        return {
            "fillColor": colormap(score),
            "color": "black",
            "weight": 0.3,
            "fillOpacity": 0.7,
        }

    folium.GeoJson(
        gdf[[data_column, "geometry"]].to_json(),
        name="Polygon Heatmap",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(fields=[data_column]),
    ).add_to(folium_map)
    folium_map.add_child(colormap)
    return folium_map
