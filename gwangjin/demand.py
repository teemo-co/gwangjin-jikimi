import geopandas as gpd
import pandas as pd


def load_kids_cafe(path):
    df = pd.read_csv(path)
    # 보통 키즈카페 파일은 위도, 경도 컬럼이 있으리라 가정합니다.
    df = df.dropna(subset=["위도", "경도"])
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["경도"], df["위도"]), crs="EPSG:4326").to_crs(epsg=5186)
    return gdf


private_kids_cafe_gdf = load_kids_cafe("kids_cafe_list.csv")


def load_seoul_kids_cafe(path):
    df = pd.read_csv(path)
    df = df.dropna(subset=["위도", "경도"])
    df["target_place"] = True
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["경도"], df["위도"]), crs="EPSG:4326").to_crs(epsg=5186)
    return gdf


seoul_kids_cafe_gdf = load_seoul_kids_cafe("seoul_kids_cafe_list.csv")
