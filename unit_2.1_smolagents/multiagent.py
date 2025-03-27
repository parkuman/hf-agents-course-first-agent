"""
The reception is approaching! With your help, Alfred is now nearly finished with the preparations.

But now there's a problem: the Batmobile has disappeared. Alfred needs to find a replacement, and find it quickly.

Fortunately, a few biopics have been done on Bruce Wayne's life, so maybe Alfred could get a car left behind on one of the movie set, and re-engineer it up to modern standards, which certainly would include a full self-driving option.

But this could be anywhere in the filming locations around the world - which could be numerous.

So Alfred wants your help. Could you build an agent able to solve this task?

    👉 Find all Batman filming locations in the world, calculate the time to transfer via boat to there, and represent them on a map, with a color varying by boat transfer time. Also represent some supercar factories with the same boat transfer time.

Let's build this!
"""

# We first make a tool to get the cargo plane transfer time.
import math
import os
from PIL import Image
from smolagents import CodeAgent, DuckDuckGoSearchTool, HfApiModel, VisitWebpageTool, OpenAIServerModel
from typing import Optional, Tuple

from smolagents import tool


@tool
def calculate_cargo_travel_time(
    origin_coords: Tuple[float, float],
    destination_coords: Tuple[float, float],
    # Average speed for cargo planes
    cruising_speed_kmh: Optional[float] = 750.0,
) -> float:
    """
    Calculate the travel time for a cargo plane between two points on Earth using great-circle distance.

    Args:
        origin_coords: Tuple of (latitude, longitude) for the starting point
        destination_coords: Tuple of (latitude, longitude) for the destination
        cruising_speed_kmh: Optional cruising speed in km/h (defaults to 750 km/h for typical cargo planes)

    Returns:
        float: The estimated travel time in hours

    Example:
        >>> # Chicago (41.8781° N, 87.6298° W) to Sydney (33.8688° S, 151.2093° E)
        >>> result = calculate_cargo_travel_time((41.8781, -87.6298), (-33.8688, 151.2093))
    """

    def to_radians(degrees: float) -> float:
        return degrees * (math.pi / 180)

    # Extract coordinates
    lat1, lon1 = map(to_radians, origin_coords)
    lat2, lon2 = map(to_radians, destination_coords)

    # Earth's radius in kilometers
    EARTH_RADIUS_KM = 6371.0

    # Calculate great-circle distance using the haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    distance = EARTH_RADIUS_KM * c

    # Add 10% to account for non-direct routes and air traffic controls
    actual_distance = distance * 1.1

    # Calculate flight time
    # Add 1 hour for takeoff and landing procedures
    flight_time = (actual_distance / cruising_speed_kmh) + 1.0

    # Format the results
    return round(flight_time, 2)


# print(calculate_cargo_travel_time((41.8781, -87.6298), (-33.8688, 151.2093)))

task = """
Find all Batman filming locations in the world, calculate the time to transfer via cargo plane to here (we're in Gotham, 40.7128° N, 74.0060° W), and return them to me as a pandas dataframe.
Also give me some supercar factories with the same cargo plane transfer time.
"""

model = OpenAIServerModel(
    model_id="qwen/qwq-32b:free",
    api_base="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

agent = CodeAgent(
    model=model,
    tools=[DuckDuckGoSearchTool(), VisitWebpageTool(),
           calculate_cargo_travel_time],
    additional_authorized_imports=["pandas"],
    max_steps=20,
)

result = agent.run(task)
