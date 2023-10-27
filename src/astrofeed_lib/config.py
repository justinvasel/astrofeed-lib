"""Package configuration. For now, it just takes from environment variables."""
import os


# --- HOST CONFIGURATION ----------------------
# Server host variables
# Todo: change how these are set
# HOSTNAME = os.environ.get("HOSTNAME", None)
# SERVICE_DID = os.environ.get("SERVICE_DID", None)
# if HOSTNAME is None:
#     raise RuntimeError('You should set "HOSTNAME" environment variable first.')
HOSTNAME = "feed-all.astronomy.blue"
SERVICE_DID = None

if SERVICE_DID is None:
    SERVICE_DID = f"did:web:{HOSTNAME}"

# --- FEED CONFIGURATION ----------------------
# Feed variables
FEED_URI = "at://did:plc:jcoy7v3a2t4rcfdh6i4kza25/app.bsky.feed.generator/"

# Dict containing all feeds *to be published*! key:value pairs of the short name and name as published.
# The short name is used throughout databases. The name as published is the URI where the feed is.
# The actual inner workings of feeds are housed in feeds.py. This variable specifies which feeds the firehose and
# server should try to host, however.
FEED_URIS = {
    FEED_URI + "astro-all": "all",
    FEED_URI + "astro": "astro",
}

# Dict containing all terms to search for in strings
FEED_TERMS = {
    "all": None,
    "astro": ("🔭", "#astro", "#astronomy"),
    # "exoplanets": ("🪐", "#exoplanet", "#exoplanets"),
    # "planetary": ("🌍", "🌎", "🌏", "#planetaryscience", "#planetsci"),
    # "stars": ("⭐", "#star", "#stars"),
    # "astrophotos": ("🔭📷", "#astrophotos", "#astrophotography"),
}


# --- ACCOUNT SYSTEM CONFIGURATION ----------------------
# Bluesky client integration for DID queries
HANDLE = "emily.space"  # os.getenv("BLUESKY_HANDLE")
PASSWORD = os.getenv("BLUESKY_PASSWORD")
if HANDLE is None or PASSWORD is None:
    raise ValueError("Bluesky account environment variables not set.")

# Google Sheets integration
SHEET_LINK = "https://docs.google.com/spreadsheets/d/1aUjkLr5uzoVQuT8Iy_7QpmkdSfCXuR7S3MV3-zYKnFk/export?format=csv&gid=1795057871"
QUERY_INTERVAL = 60 * 10


# --- DATABASE CONFIGURATION ----------------------
# Database stuff
class DatabaseConfig:
    def __init__(self):
        self.name, self.params = "", dict()
        
        try:
            self._set_params_from_connection_string()
        except ValueError:
            self._set_params_from_environment_variables()

    def _set_params_from_connection_string(self):
        """Fetches parameters from a connection string, which will look like:

        mysql://USER:PASSWORD@HOST:PORT/NAME?ssl-mode=REQUIRED
        """
        connection_string = os.environ.get("BLUESKY_DATABASE", None)

        if connection_string is None:
            raise ValueError("must set database environment variables!")

        # Split it into three segments
        connection_string = connection_string.replace("mysql://", "")
        first_half, second_half = connection_string.split("/")
        user_details, host_details = first_half.split("@")

        # Deal with user & host
        self.params["user"], self.params["password"] = user_details.split(":")
        self.params["host"], self.params["port"] = host_details.split(":")
        self.params["port"] = int(self.params["port"])

        # Deal with name and flags
        self.name, flags = second_half.split("?")

        if "ssl-mode=REQUIRED" in flags:
            self.params["ssl_disabled"] = False

    def _set_params_from_environment_variables(self):
        """Fetches parameters from individual environment variables."""
        print(
            "WARNING! Setting parameters of database from individual env vars. This will be deprecated."
            " In future, use BLUESKY_DATABASE instead."
        )

        self.params["host"] = os.environ.get("DATABASE_HOST", None)
        self.params["port"] = int(os.environ.get("DATABASE_PORT", 25060))
        self.params["user"] = os.environ.get("DATABASE_USER", None)
        self.params["password"] = os.environ.get("DATABASE_PASSWORD", None)
        self.name = os.environ.get("DATABASE_NAME", None)
        if self.name is None or any([value is None for value in self.params.values()]):
            raise ValueError("You must specify a database to use!")

        # Hard-set (since this will be deprecated)
        self.params["ssl_disabled"] = False
