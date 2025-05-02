import numpy as np
import pandas as pd


def haversine(lat1: float, lng1: float, lat2: float, lng2: float):
    """
    Calculate the great-circle distance between two points
    on the earth (specified in decimal degrees) in meters.
    """
    # Convert decimal degrees to radians
    lng1, lat1, lng2, lat2 = map(np.radians, [lng1, lat1, lng2, lat2])

    # Haversine formula
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371000  # Radius of earth in meters.
    return c * r


def calculate_parking_scores(
    poi_df: pd.DataFrame, parking_df: pd.DataFrame, child_walking_speed_mps: float, min_distance_m: float = 1.0
) -> pd.DataFrame:
    """Calculate parking scores for each POI based on the number of parking lots

    Parameters
    ----------
    poi_df
        pandas DataFrame containing points of interest (POIs) with 'lat' and 'lng' columns
    parking_df
        pandas DataFrame containing parking lots with 'lat', 'lng', and 'n_parkings' columns
    child_walking_speed_mps
        walking speed of a child in meters per second
    min_distance_m, optional
        minimum distance in meters to consider a parking lot, by default 1.0

    Returns
    -------
    pandas DataFrame
        DataFrame containing the original POI data with an additional 'parking_score' column
    """
    if not all(col in poi_df.columns for col in ["lat", "lng"]):
        raise ValueError("poi_df must contain 'lat' and 'lng' columns.")
    if not all(col in parking_df.columns for col in ["lat", "lng", "n_parkings"]):
        raise ValueError("parking_df must contain 'lat', 'lng', and 'n_parkings' columns.")

    # 1. Calculate dynamic distance cutoff (15 minutes walk)
    max_walk_time_seconds = 15 * 60
    distance_cutoff_m = child_walking_speed_mps * max_walk_time_seconds

    raw_scores = []

    # 2. Iterate through each POI
    for _, poi_row in poi_df.iterrows():
        poi_lat: float = poi_row["lat"].item()
        poi_lng: float = poi_row["lng"].item()
        poi_raw_score = 0.0

        # 3. Iterate through each parking lot
        for _, park_row in parking_df.iterrows():
            park_lat: float = park_row["lat"].item()
            park_lng: float = park_row["lng"].item()
            n_parkings = park_row["n_parkings"]

            # Calculate distance
            distance = haversine(poi_lat, poi_lng, park_lat, park_lng)

            # 4. Check if within distance cutoff
            if distance <= distance_cutoff_m:
                # Apply minimum distance floor
                effective_distance = np.maximum(distance, min_distance_m)

                contribution = n_parkings / effective_distance
                poi_raw_score += contribution

        raw_scores.append(poi_raw_score)

    # 5. Normalize scores (Min-Max scaling to 0-100)
    raw_scores_np = np.array(raw_scores)
    min_raw_score = np.min(raw_scores_np)
    max_raw_score = np.max(raw_scores_np)

    if max_raw_score == min_raw_score:
        # Handle case where all scores are identical (avoid division by zero)
        # Assign a neutral score (e.g., 50) or boundary (0 or 100)
        normalized_scores = np.full_like(raw_scores_np, 50.0)
    else:
        normalized_scores = ((raw_scores_np - min_raw_score) / (max_raw_score - min_raw_score)) * 100

    # Add scores to the DataFrame
    poi_df_result = poi_df.copy()
    poi_df_result["parking_score"] = normalized_scores

    return poi_df_result
