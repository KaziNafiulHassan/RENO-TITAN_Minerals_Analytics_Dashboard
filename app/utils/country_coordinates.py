"""
Country coordinates for geospatial visualization.
Provides latitude and longitude for country centroids.
"""

# Country ISO3 codes mapped to their centroids (latitude, longitude)
COUNTRY_COORDINATES = {
    # Africa
    'DZA': (28.0339, 1.6596),      # Algeria
    'AGO': (-11.2027, 17.8739),    # Angola
    'BEN': (9.3077, 2.3158),       # Benin
    'BWA': (-22.3285, 24.6849),    # Botswana
    'BFA': (12.2383, -1.5616),     # Burkina Faso
    'BDI': (-3.3731, 29.9189),     # Burundi
    'CMR': (3.8480, 11.5021),      # Cameroon
    'CPV': (16.5388, -23.6385),    # Cape Verde
    'CAF': (6.6111, 20.9394),      # Central African Republic
    'TCD': (15.4730, 18.7322),     # Chad
    'COM': (-11.6455, 43.3333),    # Comoros
    'COG': (-4.0383, 21.7587),     # Congo
    'COD': (-4.0383, 21.7587),     # Democratic Republic of Congo
    'CIV': (7.5400, -5.5471),      # Côte d'Ivoire
    'DJI': (11.8254, 42.5903),     # Djibouti
    'EGY': (26.8206, 30.8025),     # Egypt
    'GNQ': (1.6508, 10.2679),      # Equatorial Guinea
    'ERI': (15.1794, 39.7823),     # Eritrea
    'ETH': (9.1450, 40.4897),      # Ethiopia
    'GAB': (-0.8037, 11.6045),     # Gabon
    'GMB': (13.4549, -15.3105),    # Gambia
    'GHA': (7.3697, -5.3631),      # Ghana
    'GIN': (9.9456, -9.6966),      # Guinea
    'GNB': (11.8037, -15.1804),    # Guinea-Bissau
    'KEN': (-0.0236, 37.9062),     # Kenya
    'LSO': (-29.6100, 28.2336),    # Lesotho
    'LBR': (6.4281, -9.4295),      # Liberia
    'LBY': (26.3351, 17.2283),     # Libya
    'MDG': (-18.7669, 46.8691),    # Madagascar
    'MWI': (-13.2543, 34.3015),    # Malawi
    'MLI': (17.5707, -3.9962),     # Mali
    'MRT': (21.0079, -10.9408),    # Mauritania
    'MUS': (-20.3484, 57.5522),    # Mauritius
    'MAR': (31.7917, -7.0926),     # Morocco
    'MOZ': (-18.6657, 35.5296),    # Mozambique
    'NAM': (-22.9375, 18.7332),    # Namibia
    'NER': (17.6078, 8.6753),      # Niger
    'NGA': (9.0820, 8.6753),       # Nigeria
    'RWA': (-1.9536, 29.8739),     # Rwanda
    'STP': (0.0000, 6.6131),       # São Tomé and Príncipe
    'SEN': (14.4974, -14.4524),    # Senegal
    'SYC': (-4.6796, 55.4920),     # Seychelles
    'SLE': (8.4606, -11.7799),     # Sierra Leone
    'SOM': (5.1521, 46.1996),      # Somalia
    'ZAF': (-30.5595, 22.9375),    # South Africa
    'SSD': (6.8770, 31.3070),      # South Sudan
    'SDN': (12.8628, 30.8025),     # Sudan
    'SWZ': (-26.5225, 31.4659),    # Eswatini
    'TZA': (-6.3690, 34.8888),     # Tanzania
    'TGO': (7.3697, 0.8449),       # Togo
    'TUN': (33.8869, 9.5375),      # Tunisia
    'UGA': (1.3733, 32.2903),      # Uganda
    'ZMB': (-13.1339, 27.8493),    # Zambia
    'ZWE': (-19.0154, 29.1549),    # Zimbabwe
    
    # Asia
    'AFG': (33.9391, 67.0099),     # Afghanistan
    'ARM': (40.0691, 45.0382),     # Armenia
    'AZE': (40.1431, 47.5769),     # Azerbaijan
    'BHR': (26.0667, 50.5577),     # Bahrain
    'BGD': (23.6850, 90.3563),     # Bangladesh
    'BTN': (27.5142, 90.4336),     # Bhutan
    'BRN': (4.5353, 114.7277),     # Brunei
    'KHM': (12.5657, 104.9910),    # Cambodia
    'CHN': (35.8617, 104.1954),    # China
    'GEO': (42.3154, 43.3569),     # Georgia
    'IND': (20.5937, 78.9629),     # India
    'IDN': (-0.7893, 113.9213),    # Indonesia
    'IRN': (32.4279, 53.6880),     # Iran
    'IRQ': (33.3157, 44.3615),     # Iraq
    'ISR': (31.0461, 34.8516),     # Israel
    'JPN': (36.2048, 138.2529),    # Japan
    'JOR': (30.5852, 36.2384),     # Jordan
    'KAZ': (48.0196, 66.9237),     # Kazakhstan
    'KWT': (29.3117, 47.4818),     # Kuwait
    'KGZ': (41.5015, 74.7659),     # Kyrgyzstan
    'LAO': (19.8524, 102.4955),    # Laos
    'LBN': (33.8547, 35.8623),     # Lebanon
    'MYS': (4.2105, 101.6964),     # Malaysia
    'MDV': (4.1694, 73.5093),      # Maldives
    'MNG': (46.8625, 103.8467),    # Mongolia
    'MMR': (21.9162, 95.9560),     # Myanmar
    'NPL': (28.3949, 84.1240),     # Nepal
    'PRK': (40.3399, 127.5101),    # North Korea
    'OMN': (21.4735, 55.9754),     # Oman
    'PAK': (30.3753, 69.3451),     # Pakistan
    'PSE': (31.9454, 35.2338),     # Palestine
    'PHL': (12.8797, 121.7740),    # Philippines
    'QAT': (25.3548, 51.1839),     # Qatar
    'SAU': (23.8859, 45.0792),     # Saudi Arabia
    'SGP': (1.3521, 103.8198),     # Singapore
    'KOR': (35.9078, 127.7669),    # South Korea
    'LKA': (7.8731, 80.7718),      # Sri Lanka
    'SYR': (34.8021, 38.9968),     # Syria
    'TWN': (23.6978, 120.9605),    # Taiwan
    'TJK': (38.8610, 71.2761),     # Tajikistan
    'THA': (15.8700, 100.9925),    # Thailand
    'TLS': (-8.8383, 125.7373),    # Timor-Leste
    'TUR': (38.9637, 35.2433),     # Turkey
    'TKM': (38.9697, 59.5563),     # Turkmenistan
    'ARE': (23.4241, 53.8478),     # UAE
    'UZB': (41.3775, 64.5853),     # Uzbekistan
    'VNM': (14.0583, 108.2772),    # Vietnam
    'YEM': (15.5527, 48.5164),     # Yemen
    
    # Europe
    'ALB': (41.1533, 20.1683),     # Albania
    'AND': (42.5406, 1.5948),      # Andorra
    'AUT': (47.5162, 14.5501),     # Austria
    'BLR': (53.7098, 27.9534),     # Belarus
    'BEL': (50.5039, 4.4699),      # Belgium
    'BIH': (43.9159, 17.6791),     # Bosnia and Herzegovina
    'BGR': (42.7339, 25.4858),     # Bulgaria
    'HRV': (45.1, 15.2),           # Croatia
    'CYP': (34.9249, 33.4299),     # Cyprus
    'CZE': (49.8175, 15.4730),     # Czech Republic
    'DNK': (56.2639, 9.5018),      # Denmark
    'EST': (58.5953, 25.0136),     # Estonia
    'FIN': (61.9241, 25.7482),     # Finland
    'FRA': (46.2276, 2.2137),      # France
    'DEU': (51.1657, 10.4515),     # Germany
    'GRC': (39.0742, 21.8243),     # Greece
    'HUN': (47.1625, 19.5033),     # Hungary
    'ISL': (64.9631, -19.0208),    # Iceland
    'IRL': (53.4129, -8.2439),     # Ireland
    'ITA': (41.8719, 12.5674),     # Italy
    'XKX': (42.6026, 21.1787),     # Kosovo
    'LVA': (56.8796, 24.6032),     # Latvia
    'LIE': (47.1660, 9.5554),      # Liechtenstein
    'LTU': (55.1694, 23.8813),     # Lithuania
    'LUX': (49.8153, 6.1296),      # Luxembourg
    'MLT': (35.9375, 14.3754),     # Malta
    'MDA': (47.4116, 28.3699),     # Moldova
    'MCO': (43.7384, 7.4246),      # Monaco
    'MNE': (42.7087, 19.3744),     # Montenegro
    'NLD': (52.1326, 5.2913),      # Netherlands
    'MKD': (41.6086, 21.7453),     # North Macedonia
    'NOR': (60.4720, 8.4689),      # Norway
    'POL': (51.9194, 19.1451),     # Poland
    'PRT': (39.3999, -8.2245),     # Portugal
    'ROU': (45.9432, 24.9668),     # Romania
    'RUS': (61.5240, 105.3188),    # Russia
    'SMR': (43.9424, 12.4578),     # San Marino
    'SRB': (44.0165, 21.0059),     # Serbia
    'SVK': (48.6690, 19.6990),     # Slovakia
    'SVN': (46.1512, 14.9955),     # Slovenia
    'ESP': (40.4637, -3.7492),     # Spain
    'SWE': (60.1282, 18.6435),     # Sweden
    'CHE': (46.8182, 8.2275),      # Switzerland
    'UKR': (48.3794, 31.1656),     # Ukraine
    'GBR': (55.3781, -3.4360),     # United Kingdom
    
    # Americas
    'ATG': (17.0578, -61.7964),    # Antigua and Barbuda
    'ARG': (-38.4161, -63.6167),   # Argentina
    'BHS': (25.0343, -77.3963),    # Bahamas
    'BRB': (13.1939, -59.5432),    # Barbados
    'BLZ': (17.1899, -88.7979),    # Belize
    'BOL': (-16.2902, -63.5887),   # Bolivia
    'BRA': (-14.2350, -51.9253),   # Brazil
    'CAN': (56.1304, -106.3468),   # Canada
    'CHL': (-35.6751, -71.5430),   # Chile
    'COL': (4.5709, -74.2973),     # Colombia
    'CRI': (9.7489, -83.7534),     # Costa Rica
    'CUB': (21.5218, -77.7812),    # Cuba
    'DMA': (15.4150, -61.3710),    # Dominica
    'DOM': (18.9712, -70.1622),    # Dominican Republic
    'ECU': (-1.8312, -78.1834),    # Ecuador
    'SLV': (13.7942, -88.8965),    # El Salvador
    'GRD': (12.0843, -61.6789),    # Grenada
    'GTM': (15.7835, -90.2308),    # Guatemala
    'GUY': (4.8604, -58.9302),     # Guyana
    'HTI': (18.9712, -72.2852),    # Haiti
    'HND': (15.2000, -86.2419),    # Honduras
    'JAM': (18.1096, -77.2975),    # Jamaica
    'MEX': (23.6345, -102.5528),   # Mexico
    'NIC': (12.8654, -85.2072),    # Nicaragua
    'PAN': (8.5380, -80.7821),     # Panama
    'PRY': (-23.4425, -58.4438),   # Paraguay
    'PER': (-9.1900, -75.0152),    # Peru
    'KNA': (17.2574, -62.6830),    # Saint Kitts and Nevis
    'LCA': (13.9094, -60.9789),    # Saint Lucia
    'VCT': (12.9843, -61.2872),    # Saint Vincent and the Grenadines
    'SUR': (3.9193, -56.0278),     # Suriname
    'TTO': (10.6918, -61.2225),    # Trinidad and Tobago
    'USA': (37.0902, -95.7129),    # United States
    'URY': (-32.5228, -55.7658),   # Uruguay
    'VEN': (6.4238, -66.5897),     # Venezuela
    
    # Oceania
    'AUS': (-25.2744, 133.7751),   # Australia
    'FJI': (-17.7134, 178.0650),   # Fiji
    'KIR': (1.3521, 172.9789),     # Kiribati
    'MHL': (7.1315, 171.1845),     # Marshall Islands
    'FSM': (7.4256, 150.5508),     # Micronesia
    'NRU': (-0.5228, 166.9315),    # Nauru
    'NZL': (-40.9006, 174.8860),   # New Zealand
    'PLW': (7.3150, 134.4807),     # Palau
    'PNG': (-6.3150, 143.9555),    # Papua New Guinea
    'WSM': (-13.7590, -172.1046),  # Samoa
    'SLB': (-9.6457, 160.1562),    # Solomon Islands
    'TON': (-21.1789, -175.1982),  # Tonga
    'TUV': (-8.5211, 179.1982),    # Tuvalu
    'VUT': (-17.7404, 168.3949),   # Vanuatu
}

def get_country_centroid(iso3: str) -> tuple:
    """
    Get latitude and longitude centroid for a country.
    
    Args:
        iso3: ISO3 country code (e.g., 'VNM', 'USA')
    
    Returns:
        Tuple of (latitude, longitude) or (0, 0) if not found
    """
    return COUNTRY_COORDINATES.get(iso3, (0, 0))
