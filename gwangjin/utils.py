import re
from collections.abc import Iterator, Sequence

import geopandas as gpd
import numpy as np
from geopy.geocoders import Nominatim


def remove_text_in_parentheses(text: str) -> str:
    """Remove text in parentheses from a string."""
    pattern = r"\(.*?\)"
    result = re.sub(pattern, "", text)
    return result.strip()


def get_lat_lng(addresses: Sequence[str]) -> Iterator[tuple[float, float]]:
    """Get latitude and longitude for a list of addresses using Nominatim geocoder."""
    geolocator = Nominatim(user_agent="agent")
    for address in addresses:
        location = geolocator.geocode(address, timeout=10)
        if location:
            lat, lng = location.latitude, location.longitude
        else:
            lat, lng = np.nan, np.nan
        yield lat, lng


def get_grid_idx_within_buffer(gdf: gpd.GeoDataFrame, center_geom, radius_m: float) -> list[int]:
    """Get grid indices within a buffer around a center geometry.

    Parameters
    ----------
    gdf: gpd.GeoDataFrame
        GeoDataFrame containing the grid data
        
    center_geom: geopandas.GeoSeries
        Geometry object representing the center point for the buffer
    radius_m: float
        Radius in meters for the buffer

    Returns
    -------
    list[int]
        List of indices of the grid cells that intersect with the buffer
    """
    grid_sindex = gdf.sindex
    buffer = center_geom.buffer(radius_m)
    candidate_indices = grid_sindex.intersection(buffer.bounds)
    return list(gdf.iloc[candidate_indices][gdf.iloc[candidate_indices].intersects(buffer)].index)


def get_address(lats: list[float], lngs: list[float]) -> Iterator[list]:
    """Get address and zip code for a list of latitude and longitude pairs using Nominatim geocoder.

    Parameters
    ----------
    lats: list[float]
        List of latitudes
    lngs: list[float]
        List of longitudes

    Yields
    ------
    list
        List containing the detailed address and zip code for each latitude and longitude pair
    """
    geo_local = Nominatim(user_agent="South Korea", timeout=None)
    for lat, lng in zip(lats, lngs):
        try:
            address = geo_local.reverse([lat, lng], exactly_one=True, language="ko")
            detail_address = address.address  # 상세주소
            zip_code = address.raw["address"]["postcode"]  # 우편번호
            x_y = [detail_address, zip_code]
        except:
            x_y = [0, 0]
        yield x_y
