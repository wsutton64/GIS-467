# Geoid API: https://geodesy.noaa.gov/web_services/geoid.shtml 
# Geoid JSON Metadata: https://geodesy.noaa.gov/api/geoid/meta
# NCAT JSON Metadata: https://geodesy.noaa.gov/api/ncat/meta
# NCAT API: https://geodesy.noaa.gov/web_services/ncat/index.shtml 
# NCAT XYZ API: https://geodesy.noaa.gov/web_services/ncat/xyz-service.shtml 
import requests, json

# Initialize variables
ght_url = r"https://geodesy.noaa.gov/api/geoid/ght?"
ncat_url = r"https://geodesy.noaa.gov/api/ncat/xyz?"
xyz = []
latitude = ""
longitude = ""
ellipsoid_height = ""

def build_ght(lat, lon):
    # Build and return a URL to talk to the GHT API
    new_url = f"{ght_url}lat={lat}&lon={lon}"
    return new_url

def build_ncat(xyz_array):
    # Build and return a URL to talk to the NCAT API
    new_url = f"{ncat_url}inDatum=nad83(2011)&outDatum=nad83(2011)&x={xyz_array[0]}&y={xyz_array[1]}&z={xyz_array[2]}"
    return new_url

def call_api(url):
    # Pass in a URL and attempt a request
    response = requests.get(url)
    if response.status_code == 200:
        resp = response.json()
        return json.dumps(resp)
        # returning the JSON as a string because it creates a bug if it is returned as a dict
    else:
        # Request is not a success. Raise exception to notify the user.
        raise Exception("Response not a success. Response Code: ", response.status_code)

def convert_coordinates(xyz_array):
    # Calls on the NGS coordinate conversion API and returns an array with the converted values
    lat_lon_height = []
    data = json.loads(call_api(build_ncat(xyz_array)))
    lat_lon_height.append(data['srcLat'])
    lat_lon_height.append(data['srcLon'])
    lat_lon_height.append(data['srcEht'])
    return lat_lon_height

def clean_coordinate(coord):
    # Make sure the coordinate does not have extra whitespace or commas
    coord = coord.replace(",","")
    coord = coord.replace(" ","")
    return coord

def geodedic_height(lat, lon):
    # Calls on the NGS Geoid Height Service API. Returns the geoid height
    data = json.loads(call_api(build_ght(lat, lon)))
    if data == {}:
        raise Exception("Geoid Data Empty. Likely poor coordinates entered.")
    else:
        return data['geoidHeight']

# Attempts to cast the coordinate to a float. If it succeeds, return True
# If it throws an error, catch it and return False
def test_coord(input):
    try: 
        float(input)
        return True
    except:
        if input != "BLANKCOORD":
            print("Invalid input")
        return False
    
# Main method of the program
def main():
    # Initialize x,y,z
    x = y = z = "BLANKCOORD"
    # Prompt user to input their coordinates. Keeps prompting until user gives a valid coordinate
    print("Input your coordinates:")
    while not test_coord(x):
        x = input("X: ")
        x = clean_coordinate(x)
    while not test_coord(y):
        y = input("Y: ")
        y = clean_coordinate(y)    
    while not test_coord(z):
        z = input("Z: ")
        z = clean_coordinate(z)
    # Take the given coordinates and add them to the xyz array
    xyz.append(x)
    xyz.append(y)
    xyz.append(z)
    try:
        # Convert the XYZ coordinates to Latitude, Longitude, and Ellipsoid Height
        converted = convert_coordinates(xyz)
        latitude = converted[0]
        longitude = converted[1]
        ellipsoid_height = converted[2]
        # Calculate the elevation by getting the geoid height
        geoid_height = geodedic_height(latitude, longitude)
        elevation = float(ellipsoid_height) + float(geoid_height)
        # Display the outcome to the user
        print(f"\nLatitude: {latitude}\nLongitude: {longitude}\nEllipsoid Height: {ellipsoid_height}\nGeoid Height: {geoid_height}\nElevation: {elevation}")
    except Exception as e:
        print("An error has occured: ", e)

# Run the program
main()

# It is known to work with the coordinates:
# X: -217,687.297
# Y: -5,069,012.421
# Z: 3,852,223.063
# However, some coordinates do not return a geoid height and it is unknown why.
