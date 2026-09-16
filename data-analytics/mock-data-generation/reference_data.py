"""
Reference data for Saayam mock data generation (Issue #301).

Geography is real (country -> state -> city with true centroids) so the
generated rows satisfy the issue's "geographic relationships are logically
consistent" requirement. Names, emails, phones and addresses are synthetic.
"""

# ─────────────────────────────────────────────────────────
# Countries — (country_name, phone_code, country_code, is_eu_member)
# ─────────────────────────────────────────────────────────

COUNTRIES = [
    ("United States", "+1",   "USA", False),
    ("India",         "+91",  "IND", False),
    ("Canada",        "+1",   "CAN", False),
    ("United Kingdom","+44",  "GBR", False),
    ("Ireland",       "+353", "IRL", True),
    ("Germany",       "+49",  "DEU", True),
    ("France",        "+33",  "FRA", True),
    ("Australia",     "+61",  "AUS", False),
]

# ─────────────────────────────────────────────────────────
# States keyed by country_code.
# (state_id, state_name, state_code)
# state_id is a short slug — VARCHAR(50) in states, VARCHAR(30) in users,
# so it is kept well under 30 characters to satisfy both.
# ─────────────────────────────────────────────────────────

STATES = {
    "USA": [
        ("US-CA", "California",     "CA"),
        ("US-TX", "Texas",          "TX"),
        ("US-NY", "New York",       "NY"),
        ("US-FL", "Florida",        "FL"),
        ("US-IL", "Illinois",       "IL"),
        ("US-WA", "Washington",     "WA"),
        ("US-MA", "Massachusetts",  "MA"),
        ("US-GA", "Georgia",        "GA"),
        ("US-AZ", "Arizona",        "AZ"),
        ("US-CO", "Colorado",       "CO"),
    ],
    "IND": [
        ("IN-MH", "Maharashtra",    "MH"),
        ("IN-KA", "Karnataka",      "KA"),
        ("IN-DL", "Delhi",          "DL"),
        ("IN-TN", "Tamil Nadu",     "TN"),
        ("IN-TG", "Telangana",      "TG"),
        ("IN-GJ", "Gujarat",        "GJ"),
    ],
    "CAN": [
        ("CA-ON", "Ontario",        "ON"),
        ("CA-BC", "British Columbia","BC"),
        ("CA-QC", "Quebec",         "QC"),
        ("CA-AB", "Alberta",        "AB"),
    ],
    "GBR": [
        ("GB-ENG", "England",       "ENG"),
        ("GB-SCT", "Scotland",      "SCT"),
        ("GB-WLS", "Wales",         "WLS"),
    ],
    "IRL": [
        ("IE-D",  "Dublin",         "D"),
        ("IE-CK", "Cork",           "CK"),
        ("IE-G",  "Galway",         "G"),
    ],
    "DEU": [
        ("DE-BE", "Berlin",         "BE"),
        ("DE-BY", "Bavaria",        "BY"),
        ("DE-HH", "Hamburg",        "HH"),
    ],
    "FRA": [
        ("FR-IDF", "Ile-de-France", "IDF"),
        ("FR-PAC", "Provence",      "PAC"),
        ("FR-ARA", "Auvergne",      "ARA"),
    ],
    "AUS": [
        ("AU-NSW", "New South Wales","NSW"),
        ("AU-VIC", "Victoria",      "VIC"),
        ("AU-QLD", "Queensland",    "QLD"),
    ],
}

# ─────────────────────────────────────────────────────────
# Cities keyed by state_id.
# (city_name, latitude, longitude, zip_prefix)
# Coordinates are real centroids; volunteer/user location points are
# jittered around them so the coordinates stay inside the right region.
# ─────────────────────────────────────────────────────────

CITIES = {
    "US-CA": [("San Jose", 37.3382, -121.8863, "951"),
              ("Los Angeles", 34.0522, -118.2437, "900"),
              ("San Francisco", 37.7749, -122.4194, "941"),
              ("San Diego", 32.7157, -117.1611, "921"),
              ("Sacramento", 38.5816, -121.4944, "958")],
    "US-TX": [("Houston", 29.7604, -95.3698, "770"),
              ("Dallas", 32.7767, -96.7970, "752"),
              ("Austin", 30.2672, -97.7431, "787"),
              ("San Antonio", 29.4241, -98.4936, "782")],
    "US-NY": [("New York", 40.7128, -74.0060, "100"),
              ("Buffalo", 42.8864, -78.8784, "142"),
              ("Rochester", 43.1566, -77.6088, "146")],
    "US-FL": [("Miami", 25.7617, -80.1918, "331"),
              ("Tampa", 27.9506, -82.4572, "336"),
              ("Orlando", 28.5383, -81.3792, "328"),
              ("Jacksonville", 30.3322, -81.6557, "322")],
    "US-IL": [("Chicago", 41.8781, -87.6298, "606"),
              ("Springfield", 39.7817, -89.6501, "627"),
              ("Naperville", 41.7508, -88.1535, "605")],
    "US-WA": [("Seattle", 47.6062, -122.3321, "981"),
              ("Spokane", 47.6588, -117.4260, "992"),
              ("Tacoma", 47.2529, -122.4443, "984")],
    "US-MA": [("Boston", 42.3601, -71.0589, "021"),
              ("Worcester", 42.2626, -71.8023, "016"),
              ("Cambridge", 42.3736, -71.1097, "021")],
    "US-GA": [("Atlanta", 33.7490, -84.3880, "303"),
              ("Savannah", 32.0809, -81.0912, "314"),
              ("Augusta", 33.4735, -82.0105, "309")],
    "US-AZ": [("Phoenix", 33.4484, -112.0740, "850"),
              ("Tucson", 32.2226, -110.9747, "857"),
              ("Mesa", 33.4152, -111.8315, "852")],
    "US-CO": [("Denver", 39.7392, -104.9903, "802"),
              ("Colorado Springs", 38.8339, -104.8214, "809"),
              ("Boulder", 40.0150, -105.2705, "803")],

    "IN-MH": [("Mumbai", 19.0760, 72.8777, "400"),
              ("Pune", 18.5204, 73.8567, "411"),
              ("Nagpur", 21.1458, 79.0882, "440")],
    "IN-KA": [("Bengaluru", 12.9716, 77.5946, "560"),
              ("Mysuru", 12.2958, 76.6394, "570"),
              ("Mangaluru", 12.9141, 74.8560, "575")],
    "IN-DL": [("New Delhi", 28.6139, 77.2090, "110"),
              ("Dwarka", 28.5921, 77.0460, "110")],
    "IN-TN": [("Chennai", 13.0827, 80.2707, "600"),
              ("Coimbatore", 11.0168, 76.9558, "641"),
              ("Madurai", 9.9252, 78.1198, "625")],
    "IN-TG": [("Hyderabad", 17.3850, 78.4867, "500"),
              ("Warangal", 17.9689, 79.5941, "506")],
    "IN-GJ": [("Ahmedabad", 23.0225, 72.5714, "380"),
              ("Surat", 21.1702, 72.8311, "395")],

    "CA-ON": [("Toronto", 43.6532, -79.3832, "M5H"),
              ("Ottawa", 45.4215, -75.6972, "K1P")],
    "CA-BC": [("Vancouver", 49.2827, -123.1207, "V6B"),
              ("Victoria", 48.4284, -123.3656, "V8W")],
    "CA-QC": [("Montreal", 45.5017, -73.5673, "H3B"),
              ("Quebec City", 46.8139, -71.2080, "G1R")],
    "CA-AB": [("Calgary", 51.0447, -114.0719, "T2P"),
              ("Edmonton", 53.5461, -113.4938, "T5J")],

    "GB-ENG": [("London", 51.5074, -0.1278, "EC1"),
               ("Manchester", 53.4808, -2.2426, "M1"),
               ("Birmingham", 52.4862, -1.8904, "B1")],
    "GB-SCT": [("Edinburgh", 55.9533, -3.1883, "EH1"),
               ("Glasgow", 55.8642, -4.2518, "G1")],
    "GB-WLS": [("Cardiff", 51.4816, -3.1791, "CF1")],

    "IE-D":  [("Dublin", 53.3498, -6.2603, "D01")],
    "IE-CK": [("Cork", 51.8985, -8.4756, "T12")],
    "IE-G":  [("Galway", 53.2707, -9.0568, "H91")],

    "DE-BE": [("Berlin", 52.5200, 13.4050, "101")],
    "DE-BY": [("Munich", 48.1351, 11.5820, "803"),
              ("Nuremberg", 49.4521, 11.0767, "904")],
    "DE-HH": [("Hamburg", 53.5511, 9.9937, "200")],

    "FR-IDF": [("Paris", 48.8566, 2.3522, "750")],
    "FR-PAC": [("Marseille", 43.2965, 5.3698, "130"),
               ("Nice", 43.7102, 7.2620, "060")],
    "FR-ARA": [("Lyon", 45.7640, 4.8357, "690")],

    "AU-NSW": [("Sydney", -33.8688, 151.2093, "200")],
    "AU-VIC": [("Melbourne", -37.8136, 144.9631, "300")],
    "AU-QLD": [("Brisbane", -27.4698, 153.0251, "400")],
}

# ─────────────────────────────────────────────────────────
# help_categories — official materialized-path cat_ids.
# Source: request repo wiki, "1.0 MVP Help Categories".
# (cat_id, cat_name, cat_desc)
# ─────────────────────────────────────────────────────────

HELP_CATEGORIES = [
    ("0.0.0.0.0", "GENERAL_CATEGORY", "Uncategorised requests that do not fit a specific category"),

    ("1",     "FOOD_AND_ESSENTIALS",            "Food, groceries and daily essentials support"),
    ("1.1",   "FOOD_ASSISTANCE",                "Direct food assistance for individuals and families"),
    ("1.2",   "GROCERY_SHOPPING_AND_DELIVERY",  "Help with grocery shopping and home delivery"),
    ("1.3",   "COOKING_HELP",                   "Assistance with meal preparation and cooking"),
    ("1.3.1", "MEAL_PREP_BASIC",                "Basic meal preparation for the week"),
    ("1.3.2", "FESTIVE_OR_BULK_COOKING",        "Cooking in bulk or for festive occasions"),
    ("1.3.3", "NUTRITIONAL_MEAL_PLANNING",      "Planning balanced and nutritional meals"),
    ("1.3.4", "CULTURAL_CUISINE_GUIDANCE",      "Guidance on preparing cultural cuisine"),
    ("1.3.5", "OTHER_COOKING_HELP",             "Other cooking assistance not otherwise listed"),

    ("2",   "CLOTHING_ASSISTANCE",           "Clothing donation, lending and tailoring support"),
    ("2.1", "DONATE_CLOTHES",                "Donating clothing to those in need"),
    ("2.2", "BORROW_CLOTHES",                "Borrowing clothing for a short period"),
    ("2.3", "EMERGENCY_CLOTHING_ASSISTANCE", "Urgent clothing support in emergencies"),
    ("2.4", "TAILORING",                     "Tailoring, alteration and repair of clothing"),

    ("3",      "HOUSING_ASSISTANCE",              "Housing, tenancy and home maintenance support"),
    ("3.1",    "LEASE_SUPPORT",                   "Help reviewing and understanding lease agreements"),
    ("3.2",    "TENANT_RENT_SUPPORT",             "Support with rent payments and tenant rights"),
    ("3.3",    "REPAIR_MAINTENANCE_SUPPORT",      "Home repair and maintenance assistance"),
    ("3.3.1",  "PLUMBING",                        "Plumbing repair and installation help"),
    ("3.3.2",  "HANDYMAN",                        "General handyman and small repair tasks"),
    ("3.3.3",  "ELECTRICIAN",                     "Electrical repair and installation help"),
    ("3.3.4",  "CARPENTRY",                       "Carpentry and woodwork assistance"),
    ("3.3.5",  "GARDEN",                          "Gardening and outdoor maintenance help"),
    ("3.3.6",  "HVAC_AIR_CONDITIONING",           "Heating, ventilation and air conditioning support"),
    ("3.3.7",  "ROOFING",                         "Roof inspection and repair assistance"),
    ("3.3.8",  "LOCKSMITH",                       "Lock repair, replacement and key services"),
    ("3.3.9",  "PAINTING",                        "Interior and exterior painting help"),
    ("3.3.10", "MASONRY_OR_CONCRETE",             "Masonry, brickwork and concrete repairs"),
    ("3.3.11", "METALWORK_OR_WELDING",            "Metalwork and welding assistance"),
    ("3.3.12", "POOL_AND_SPA_MAINTENANCE",        "Pool and spa cleaning and maintenance"),
    ("3.3.13", "OTHER_REPAIR_MAINTENANCE_SUPPORT","Other repair work not otherwise listed"),
    ("3.4",    "UTILITIES_SETUP_SUPPORT",         "Help setting up utilities at a new residence"),
    ("3.5",    "LOOKING_FOR_RENTAL",              "Assistance finding suitable rental housing"),
    ("3.6",    "FIND_ROOMATE",                    "Help finding a compatible roommate"),
    ("3.7",    "MOVE_IN_HELP",                    "Assistance with moving into a new home"),
    ("3.8",    "BOOKING_PACKERS_MOVERS_SUPPORT",  "Support booking packers and movers"),
    ("3.9",    "BUY_THINGS",                      "Help purchasing household items"),
    ("3.10",   "SELL_THINGS",                     "Help selling household items"),

    ("4",     "EDUCATION_CAREER_SUPPORT",   "Education, tutoring and career guidance"),
    ("4.1",   "COLLEGE_APPLICATION_HELP",   "Guidance through the college application process"),
    ("4.2",   "SOP_ESSAY_REVIEW",           "Review of statements of purpose and essays"),
    ("4.3",   "TUTORING",                   "Subject tutoring for students of all levels"),
    ("4.3.1", "MATH",                       "Mathematics tutoring and problem solving"),
    ("4.3.2", "ENGLISH",                    "English language and literature tutoring"),
    ("4.3.3", "SCIENCE",                    "Science subject tutoring"),
    ("4.3.4", "COMPUTER_SCIENCE",           "Computer science and programming tutoring"),
    ("4.3.5", "TEST_PREP",                  "Standardised test preparation support"),
    ("4.3.6", "OTHER_SUBJECTS",             "Tutoring in subjects not otherwise listed"),
    ("4.4",   "SCHOLARSHIP_KNOWLEDGE",      "Information and guidance on scholarships"),
    ("4.5",   "STUDY_GROUP_FORMATION",      "Help forming and joining study groups"),
    ("4.6",   "CAREER_GUIDANCE",            "Career planning and professional guidance"),
    ("4.7",   "EDUCATION_RESOURCE_SHARING", "Sharing textbooks and learning resources"),

    ("5",      "HEALTHCARE_AND_WELLNESS",                "Healthcare consultation and wellness support"),
    ("5.1",    "MEDICAL_CONSULTATION",                   "Consultation with volunteer medical professionals"),
    ("5.1.1",  "GENERAL_CONSULTATION",                   "General health consultation and advice"),
    ("5.1.2",  "ENT_EAR_NOSE_AND_THROAT",                "Ear, nose and throat related consultation"),
    ("5.1.3",  "DENTAL_OR_ORAL_HEALTH",                  "Dental and oral health consultation"),
    ("5.1.4",  "EYE_OR_VISION_CARE",                     "Eye examination and vision care guidance"),
    ("5.1.5",  "CARDIAC_OR_BLOOD_PRESSURE",              "Cardiac and blood pressure related guidance"),
    ("5.1.6",  "ORTHOPEDIC_OR_PHYSIOTHERAPY",            "Orthopedic and physiotherapy support"),
    ("5.1.7",  "SKIN_OR_DERMATOLOGY",                    "Skin and dermatology consultation"),
    ("5.1.8",  "WOMENS_OR_REPRODUCTIVE_HEALTH",          "Women's and reproductive health guidance"),
    ("5.1.9",  "VACCINATIONS_AND_PREVENTIVE_SCREENINGS", "Vaccination and preventive screening information"),
    ("5.1.10", "PEDIATRICS_OR_CHILD_HEALTH",             "Child health and pediatric consultation"),
    ("5.1.11", "OTHER_MEDICAL_CONCERN",                  "Medical concerns not otherwise listed"),
    ("5.2",    "MEDICINE_DELIVERY",                      "Delivery of prescribed medicines"),
    ("5.3",    "MENTAL_WELLBEING_SUPPORT",               "Mental wellbeing and emotional support"),
    ("5.4",    "MEDICATION_REMINDERS",                   "Reminders to take prescribed medication"),
    ("5.5",    "HEALTH_EDUCATION_GUIDANCE",              "Health education and preventive care guidance"),

    ("6",   "ELDERLY_COMMUNITY_ASSISTANCE",       "Support services for elderly community members"),
    ("6.1", "SENIOR_RELOCATION_SUPPORT",          "Assistance relocating elderly residents"),
    ("6.2", "DIGITAL_SUPPORT_FOR_SENIORS",        "Help using phones, tablets and computers"),
    ("6.3", "MEDICATION_MANAGEMENT",              "Organising and managing daily medication"),
    ("6.4", "MEDICAL_DEVICES_SETUP",              "Setting up and explaining medical devices"),
    ("6.5", "ERRANDS_EVENTS_TRANSPORTATION",      "Errands, events and general transportation"),
    ("6.6", "TRANSPORTATION_APPOINTMENTS_EVENTS", "Transport to appointments and events"),
    ("6.7", "SCHEDULING_APPOINTMENTS_OR_TASKS",   "Scheduling appointments and daily tasks"),
    ("6.8", "SOCIAL_CONNECTION",                  "Companionship and social connection visits"),
    ("6.9", "MEAL_SUPPORT",                       "Meal preparation and delivery for seniors"),
]

# ─────────────────────────────────────────────────────────
# Synthetic name pools — deliberately invented, not sourced
# from any real directory or dataset.
# ─────────────────────────────────────────────────────────

FIRST_NAMES = [
    "Amara", "Bryn", "Caius", "Dalia", "Ewan", "Farrah", "Gideon", "Hana",
    "Idris", "Juno", "Kiran", "Lior", "Mira", "Nadir", "Orla", "Priya",
    "Quill", "Rhea", "Soren", "Tova", "Ulric", "Vesna", "Wren", "Xenia",
    "Yusuf", "Zarina", "Anika", "Bodhi", "Cyra", "Dmitri", "Esha", "Finn",
    "Gita", "Hugo", "Isla", "Jarek", "Kaia", "Lucian", "Maren", "Niko",
    "Odette", "Pavel", "Rania", "Sana", "Tariq", "Uma", "Viktor", "Yara",
]

LAST_NAMES = [
    "Alden", "Brightwater", "Calder", "Dunmore", "Ellery", "Fairbourne",
    "Galloway", "Hartwell", "Ipsen", "Jarvie", "Kestrel", "Lockhart",
    "Marchetti", "Nordstrom", "Okonjo", "Pellegrin", "Quintero", "Ravensworth",
    "Sandoval", "Thorne", "Ulvang", "Vasquez", "Whitfield", "Xiang",
    "Yarrow", "Zelenko", "Ashford", "Blackwood", "Castellan", "Devereux",
    "Eastwick", "Fontaine", "Greystone", "Havelock", "Ironside", "Jorgensen",
]

STREET_NAMES = [
    "Alder", "Birchwood", "Cedar Ridge", "Dovetail", "Elmshade", "Fernbank",
    "Gladstone", "Hollybrook", "Ironwood", "Juniper", "Kingfisher", "Larkspur",
    "Maplecrest", "Northgate", "Oakhollow", "Primrose", "Quarry", "Rosewood",
    "Stonebridge", "Thistledown", "Umberwood", "Violet", "Willowmere", "Yewtree",
]

STREET_TYPES = ["St", "Ave", "Rd", "Ln", "Dr", "Blvd", "Way", "Ct", "Pl", "Ter"]

EMAIL_DOMAINS = ["example.com", "example.org", "example.net", "mail.example.com"]

GENDERS = ["Male", "Female", "Non-binary", "Prefer not to say"]

TIME_ZONES = [
    "America/Los_Angeles", "America/Denver", "America/Chicago",
    "America/New_York", "Asia/Kolkata", "Europe/London", "Europe/Dublin",
    "Europe/Berlin", "Europe/Paris", "Australia/Sydney", "America/Toronto",
]

# users.language_1/2/3 are BIGINT FKs to supporting_languages(language_id).
# That table is out of scope for this issue, so a small fixed set of ids is
# used and documented in the README rather than inventing unbounded values.
LANGUAGE_IDS = [1, 2, 3, 4, 5, 6, 7, 8]

EXTERNAL_AUTH_PROVIDERS = [None, None, None, "GOOGLE", "FACEBOOK", "APPLE"]

SKILL_LEVELS = ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"]

AVAILABILITY_DAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]

AVAILABILITY_TIMES = [
    "06:00-09:00", "09:00-12:00", "12:00-15:00",
    "15:00-18:00", "18:00-21:00", "21:00-00:00",
]

# ─────────────────────────────────────────────────────────
# Organisation name components — synthetic, non-existent orgs
# ─────────────────────────────────────────────────────────

ORG_PREFIXES = [
    "Bright", "Open", "Common", "United", "Rising", "Green", "Clear",
    "Steady", "Kind", "Anchor", "Beacon", "Harbor", "Summit", "Meadow",
    "River", "Northstar", "Cornerstone", "Evergreen", "Lantern", "Compass",
]

ORG_MIDDLES = [
    "Hands", "Roots", "Bridge", "Table", "Circle", "Haven", "Path",
    "Harvest", "Shelter", "Works", "Commons", "Collective", "Alliance",
]

ORG_SUFFIXES = [
    "Foundation", "Trust", "Initiative", "Network", "Society", "Coalition",
    "Project", "Services", "Partners", "Group", "Center", "Association",
]

ORG_MISSION_OPENERS = [
    "Working to ensure every household has reliable access to",
    "Committed to expanding community access to",
    "Dedicated to removing barriers around",
    "Partnering with local volunteers to improve",
    "Building sustainable community programmes for",
    "Connecting neighbours and resources to strengthen",
    "Providing practical, dignified assistance with",
    "Advocating for equitable access to",
]

ORG_MISSION_SUBJECTS = [
    "nutritious food and grocery support",
    "safe and stable housing",
    "affordable primary healthcare",
    "educational resources and tutoring",
    "support services for older adults",
    "clothing and essential household goods",
    "emergency relief during local crises",
    "job readiness and career development",
    "mental health and wellbeing services",
    "transportation for medical appointments",
]

ORG_MISSION_CLOSERS = [
    "across the communities we serve.",
    "for families facing financial hardship.",
    "through a volunteer-led service model.",
    "in partnership with local organisations.",
    "with a focus on underserved neighbourhoods.",
    "while preserving the dignity of every person served.",
]
