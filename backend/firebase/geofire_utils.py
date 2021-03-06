import math

# Default geohash length
g_GEOHASH_PRECISION = 10;

# Characters used in location geohashes
g_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz";

# The meridional circumference of the earth in meters
g_EARTH_MERI_CIRCUMFERENCE = 40007860;

# Length of a degree latitude at the equator
g_METERS_PER_DEGREE_LATITUDE = 110574;

# Number of bits per geohash character
g_BITS_PER_CHAR = 5;

# Maximum length of a geohash in bits
g_MAXIMUM_BITS_PRECISION = 22*g_BITS_PER_CHAR;

# Equatorial radius of the earth in meters
g_EARTH_EQ_RADIUS = 6378137.0;

# The following value assumes a polar radius of
# var g_EARTH_POL_RADIUS = 6356752.3;
# The formulate to calculate g_E2 is
# g_E2 == (g_EARTH_EQ_RADIUS^2-g_EARTH_POL_RADIUS^2)/(g_EARTH_EQ_RADIUS^2)
# The exact value is used here to avoid rounding errors
g_E2 = 0.00669447819799;

# Cutoff for rounding errors on double calculations
g_EPSILON = 1e-12;



def validate_key(key):
  error = None

  if not isinstance(key, basestring):
    error = "key must be a string"
  elif len(key) == 0:
    error = "key cannot be the empty string"
  elif 1 + g_GEOHASH_PRECISION + len(key) > 755:
    # Firebase can only stored child paths up to 768 characters
    # The child path for this key is at the least: "i/<geohash>key"
    error = "key is too long to be stored in Firebase";
  elif '.' in key or '#' in key or '$' in key or ']' in key or '[' in key or '/' in key:
    # Firebase does not allow node keys to contain the following characters
    error = "key cannot contain any of the following characters: . # $ ] [ /";

  if error:
    raise Exception("Invalid GeoFire key '" + key + "': " + error)

def validate_location(location):
  error = None

  if not isinstance(location, list):
    error = "location must be an array"
  elif len(location) != 2:
    error = "expected array of length 2, got length " + location.length
  else:
    latitude = location[0];
    longitude = location[1];

    if not isinstance(latitude, (int, long, float)) or math.isnan(latitude):
      error = "latitude must be a number"
    elif latitude < -90 or latitude > 90:
      error = "latitude must be within the range [-90, 90]"
    if not isinstance(longitude, (int, long, float)) or math.isnan(longitude):
      error = "longitude must be a number";
    elif longitude < -180 or longitude > 180:
      error = "longitude must be within the range [-180, 180]";

  if error:
    raise Exception("Invalid GeoFire location '" + str(location) + "': " + error)

def validateGeohash(geohash):
  error = None

  if not isinstance(geohash, basestring):
    error = "geohash must be a string";
  elif len(geohash) == 0:
    error = "geohash cannot be the empty string";
  else:
    for c in geohash:
      if c not in g_BASE32:
        error = "geohash cannot contain \"" + c + "\""

  if error:
    raise Exception("Invalid GeoFire geohash '" + geohash + "': " + error);

def encode_geohash(location, precision = None):
  validate_location(location)

  if precision is not None:
    if not isinstance(precision, (int, long, float)) or math.isnan(precision):
      raise Exception("precision must be a number")
    elif precision <= 0:
      raise Exception("precision must be greater than 0")
    elif precision > 22:
      raise Exception("precision cannot be greater than 22")
    elif not isinstance(precision, (int, long)):
      raise Exception("precision must be an integer")
  else:
    precision = g_GEOHASH_PRECISION

  latitudeRange = {
    'min': -90,
    'max': 90
  };
  longitudeRange = {
    'min': -180,
    'max': 180
  };
  hash = "";
  hashVal = 0;
  bits = 0;
  even = 1;

  while len(hash) < precision:
    val = location[1] if even else location[0]
    range = longitudeRange if even else latitudeRange
    mid = (range['min'] + range['max']) / 2.0

    if val > mid:
      hashVal = (hashVal << 1) + 1
      range['min'] = mid
    else:
      hashVal = (hashVal << 1) + 0
      range['max'] = mid

    even = not even;
    if bits < 4:
      bits += 1
    else:
      bits = 0
      hash += g_BASE32[hashVal]
      hashVal = 0

  return hash

def encode_geofire_object(location, geohash):
  validate_location(location)
  validateGeohash(geohash)
  return {
    "g": geohash,
    "l": location
  }


#fb = Firebase('https://alpire.firebaseio.com/')
#geofire = GeoFire(fb)
