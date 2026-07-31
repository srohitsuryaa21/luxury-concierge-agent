"""Seed data for the commission catalogue.

All figures are illustrative sales-discovery data authored for this project.
Bespoke commission pricing is not published by any manufacturer, so there is no
public source to draw from; these numbers are internally consistent and
plausible rather than real. Anything client-facing must repeat that caveat.
"""

from __future__ import annotations

# (name, tier, body, powertrain, base_price_eur, positioning)
MODELS: tuple[tuple[str, str, str, str, int, str], ...] = (
    (
        "Phantom", "flagship", "saloon", "V12",
        520_000,
        "Ceremonial flagship for presence, privacy and chauffeur-led occasions.",
    ),
    (
        "Ghost", "core", "saloon", "V12",
        365_000,
        "Discreet driver's saloon for owners who want luxury without theatre.",
    ),
    (
        "Cullinan", "core", "SUV", "V12",
        410_000,
        "All-terrain luxury for families, estates, mountain routes and distance.",
    ),
    (
        "Spectre", "electric", "coupe", "electric",
        430_000,
        "Electric grand tourer for quiet, modern, sustainability-led commissions.",
    ),
)

# (name, family, finish, price_eur, extra_lead_weeks, keywords)
PAINTS: tuple[tuple[str, str, str, int, int, str], ...] = (
    ("Commissioned Midnight Sapphire", "blue", "gloss", 0, 0, "default,understated,formal,sapphire"),
    ("Black Diamond over Anthracite", "black", "gloss", 12_000, 2, "black,formal,onyx,ceremonial,chauffeur"),
    ("Arctic White with hand-painted coachline", "white", "gloss", 18_000, 4, "white,wedding,arctic,ivory,bridal"),
    ("Bespoke Emerald Aurora", "green", "gloss", 22_000, 5, "green,forest,emerald,nature,woodland"),
    ("Bespoke Burgundy Nocturne", "red", "gloss", 22_000, 5, "burgundy,oxblood,claret,wine"),
    ("Salamanca Blue over Andalusian White", "blue", "two-tone", 34_000, 7, "navy,marine,ocean,cobalt,nautical,two-tone"),
    ("Magma Red single-tone", "red", "gloss", 26_000, 5, "crimson,scarlet,ruby,magma"),
    ("Amethyst Twilight with pearlescent flake", "purple", "pearlescent", 41_000, 8, "amethyst,violet,purple,unrepeatable"),
    ("Bronze Patina with hand-polished brightwork", "bronze", "satin", 37_000, 7, "bronze,copper,autumn,patina"),
    ("Desert Gold satin", "gold", "satin", 29_000, 5, "champagne,desert,dune,sand,gold,golden"),
    ("English White over Silver Sand", "silver", "two-tone", 31_000, 6, "silver,platinum,gunmetal,graphite,slate"),
    ("Oyster Pearl with tonal coachline", "white", "pearlescent", 27_000, 5, "pearl,bone,taupe,oyster"),
    ("Jubilee Silver", "silver", "gloss", 9_000, 1, "grey,gray,understated,discreet"),
    ("Tempest Grey", "grey", "gloss", 9_000, 1, "storm,charcoal,urban"),
    ("Gunmetal over Black", "grey", "two-tone", 28_000, 6, "gunmetal,sinister,dark"),
    ("Iguazu Blue", "blue", "gloss", 14_000, 2, "bright,azure,coastal"),
    ("Belladonna Purple", "purple", "gloss", 24_000, 4, "expressive,statement"),
    ("Petra Gold", "gold", "gloss", 21_000, 4, "warm,honey,sunset"),
    ("Scala Red", "red", "gloss", 16_000, 3, "sporting,vivid"),
    ("Andalusian White", "white", "gloss", 7_000, 1, "clean,simple,bright"),
)

# (name, family, price_eur, vegan, keywords)
LEATHERS: tuple[tuple[str, str, int, int, str], ...] = (
    ("Grace White full-grain leather", "white", 0, 0, "default,formal,bright,ceremonial"),
    ("Ardent Tan natural-grain leather", "tan", 14_000, 0, "warm,brown,tan,cognac,caramel,chestnut"),
    (
        "Scivaro Grey technical textile and responsibly sourced leather accents",
        "technical", 11_000, 1,
        "vegan,sustainable,sustainably,sustainability,responsible,cruelty-free,plant-based",
    ),
    ("Seashell Cream full-grain leather", "cream", 12_000, 0, "cream,ivory,seashell,soft"),
    ("Navy Blue full-grain leather", "blue", 12_000, 0, "navy,blue,cobalt"),
    ("Hotspur Red full-grain leather", "red", 16_000, 0, "crimson,scarlet,hotspur,burgundy,oxblood"),
    ("Anthracite Slate full-grain leather", "grey", 12_000, 0, "charcoal,slate,anthracite,grey,gray"),
    ("Black Grace full-grain leather", "black", 10_000, 0, "black,onyx,noir"),
    ("Forest Green full-grain leather", "green", 17_000, 0, "forest,emerald,green"),
    ("Selby Grey and Cobalto Blue duotone", "duotone", 21_000, 0, "duotone,contrast,two-tone,playful"),
    ("Mandarin and Black duotone", "duotone", 22_000, 0, "vivid,energetic,bold"),
    ("Casden Tan and Espresso duotone", "duotone", 20_000, 0, "layered,rich,heritage"),
    ("Arctic White technical textile", "technical", 13_000, 1, "modern,clinical,minimal"),
    ("Consort Red and Black", "red", 19_000, 0, "dramatic,theatrical"),
)

# (name, price_eur, sustainable, keywords)
VENEERS: tuple[tuple[str, int, int, str], ...] = (
    ("Piano Black technical veneer", 0, 0, "default,piano,gloss,black,formal,onyx,modern"),
    ("Open-pore Circassian walnut", 13_000, 0, "warm,walnut,brown,chestnut,heritage"),
    ("Sustainably harvested bamboo veneer", 15_000, 1, "bamboo,vegan,sustainable,sustainably,eco,responsible"),
    ("Technical carbon-fibre twill", 19_000, 0, "carbon,technical,sport,sports,performance,dynamic"),
    ("Burr Oak with mirror-matched book leaves", 21_000, 0, "oak,burr,heritage,traditional,classic"),
    ("Pale Obeche open-pore veneer", 12_000, 0, "pale,light,nordic,obeche,blonde"),
    ("Smoked Ash open-pore", 14_000, 0, "smoked,ash,contemporary"),
    ("Santos Palissander", 18_000, 0, "exotic,striped,rosewood"),
    ("Grand Piano Ebony", 16_000, 0, "ebony,deep,lacquer"),
    ("Canadel Panelling in Ardent Tan", 34_000, 0, "canadel,apex,handcrafted,craft"),
)

# (name, size_inch, price_eur, use_case, keywords)
WHEELS: tuple[tuple[str, int, int, str, str], ...] = (
    ("22-inch part-polished forged wheel", 22, 0, "balanced", "default,balanced"),
    ("21-inch part-polished disc wheel", 21, 6_000, "chauffeur", "formal,ceremonial,chauffeur,wedding,bridal,comfort"),
    ("23-inch forged alloy in gloss black", 23, 14_000, "performance", "performance,dynamic,sport,sports,driver"),
    (
        "22-inch all-terrain forged wheel with protective finish", 22, 11_000, "terrain",
        "mountain,mountains,terrain,off-road,estate,safari,adventure,snow,alpine,winter,ski",
    ),
    ("23-inch aero-optimised forged wheel", 23, 12_000, "electric", "electric,ev,quiet,aero,efficiency"),
    ("21-inch fully polished wheel", 21, 8_000, "show", "polished,shine,show,event"),
    ("22-inch two-tone forged wheel", 22, 10_000, "expressive", "two-tone,expressive,contrast"),
    ("20-inch comfort-biased wheel", 20, 4_000, "comfort", "comfort,ride,city,urban"),
)

# (name, category, price_eur, keywords, description)
OPTIONS: tuple[tuple[str, str, int, str, str], ...] = (
    # Signature / theatre
    ("Starlight headliner", "signature", 16_000, "star,starlight,night,sky", "Fibre-optic headliner."),
    ("Starlight headliner with bespoke constellation", "signature", 27_000, "constellation,bespoke,date,anniversary", "Sky rendered for a chosen date and place."),
    ("Shooting Star headliner effect", "signature", 9_000, "shooting,meteor,theatre", "Animated meteor effect."),
    ("Illuminated fascia", "signature", 18_000, "fascia,illuminated,gallery,light", "Backlit constellation fascia."),
    ("Bespoke audio tuning", "technology", 14_000, "audio,music,sound", "Cabin-matched audio calibration."),
    ("Bespoke 18-speaker audio calibration", "technology", 23_000, "concert,audiophile,speakers", "Full concert-grade calibration."),
    ("Rear theatre configuration", "rear", 21_000, "theatre,screens,entertainment", "Rear screens and controls."),
    ("Rear entertainment tablets", "rear", 11_000, "tablets,children,kids", "Detachable rear tablets."),
    # Chauffeur / rear compartment
    ("Privacy suite", "rear", 19_000, "privacy,discreet,confidential,chauffeur", "Rear privacy partition and glazing."),
    ("Champagne cooler", "rear", 12_000, "champagne,cooler,celebration,hospitality", "Chilled rear compartment cooler."),
    ("Rear picnic tables", "rear", 7_000, "picnic,tables,work,rear", "Veneered fold-out tables."),
    ("Laminated privacy glazing", "rear", 8_000, "privacy,security,glazing,tinted", "Acoustic and privacy laminate."),
    ("Rear business console", "rear", 15_000, "business,executive,work,corporate", "Console with power and connectivity."),
    ("Secure document safe", "rear", 6_000, "safe,secure,documents,confidential", "Concealed lockable safe."),
    ("Rear step illumination", "exterior", 4_000, "step,illumination,ceremonial,arrival", "Illuminated sill projection."),
    ("Discreet-arrival lighting mode", "exterior", 5_000, "discreet,arrival,low-key", "Reduced-signature lighting."),
    ("Welcome-light projection", "exterior", 4_500, "welcome,projection,event,gala", "Ground-projected marque."),
    ("Illuminated treadplates", "exterior", 3_500, "treadplates,night,evening", "Lit treadplates."),
    # Performance
    ("Dynamic drive package", "performance", 24_000, "performance,driver,dynamic,handling", "Retuned damping and steering."),
    ("Driver-focused seat contouring", "performance", 9_000, "seat,contouring,support,driver", "Bolstered front seats."),
    ("Dynamic drive calibration", "performance", 17_000, "calibration,response,sharp", "Sharper throttle and shift maps."),
    ("Sports exhaust voicing", "performance", 12_000, "exhaust,sound,sporting", "Tuned exhaust note."),
    ("Carbon-ceramic braking", "performance", 26_000, "brakes,braking,carbon,stopping", "Carbon-ceramic discs."),
    # Family / estate / terrain
    ("Rear child-seat provisioning", "family", 5_000, "child,children,kids,family,seat", "Integrated anchors and trim."),
    ("Cabin partition storage", "family", 6_500, "storage,partition,practical", "Additional cabin stowage."),
    ("All-terrain tyre package", "terrain", 8_000, "terrain,tyres,off-road,gravel", "All-terrain tyres and spare."),
    ("Elevated ride-height calibration", "terrain", 9_500, "ride-height,clearance,off-road", "Raised suspension mapping."),
    ("Boot-mounted viewing suite", "terrain", 13_000, "viewing,estate,shooting,picnic", "Deployable boot seating."),
    ("Cabin pet suite with washable lining", "family", 7_500, "pet,pets,dog,dogs,hound", "Washable rear pet compartment."),
    ("Fitted golf-bag housing", "leisure", 6_000, "golf,polo,sport,leisure", "Bespoke golf-bag fitment."),
    ("Extended touring luggage set", "leisure", 18_000, "luggage,touring,travel,tour,weekend", "Matched fitted luggage."),
    ("Rear refrigeration compartment", "leisure", 10_000, "refrigeration,cool,travel,distance", "Cooled rear compartment."),
    # Climate / regional
    ("Heat-reflective glazing", "climate", 9_000, "heat,sun,desert,dune,gcc,dubai,riyadh,doha", "Solar-reflective glazing."),
    ("Sand-sealed underbody protection", "climate", 11_000, "sand,desert,dust,arid,gritty", "Sealed underbody and filtration."),
    ("Cold-climate pack with heated everything", "climate", 12_000, "winter,snow,alpine,cold,ski", "Heated screens, seats and wheel."),
    ("Cabin air purification suite", "climate", 8_500, "air,purification,allergy,city", "Multi-stage cabin filtration."),
    # Sustainability
    ("Regenerative drive briefing", "sustainability", 0, "regenerative,electric,briefing,efficiency", "Structured handover on regen and range."),
    ("Responsible material provenance pack", "sustainability", 5_000, "provenance,responsible,sustainable,traceability", "Bound record of material origins."),
    ("Carbon-accounted build report", "sustainability", 6_500, "carbon,footprint,accounting,report", "Per-commission build accounting."),
    # Personalisation
    ("Gallery commission by a named artist", "personalisation", 95_000, "art,gallery,collector,curator,artist", "Original artwork in the fascia."),
    ("Hand-painted monogram and door crests", "personalisation", 14_000, "monogram,initials,crest,heraldry", "Hand-applied monogram."),
    ("Ceremonial coachline in hand-painted gold", "personalisation", 12_000, "coachline,ceremonial,wedding,gold", "Gold freehand coachline."),
    ("Contrast stitching matched to coachline", "personalisation", 6_000, "stitching,contrast,coachline,detail", "Stitch matched to exterior line."),
    ("Embroidered headrests", "personalisation", 5_500, "embroidery,headrest,personal", "Embroidered motif or initials."),
    ("Bespoke treadplate text", "personalisation", 3_000, "treadplate,text,engraving,personal", "Engraved treadplate wording."),
    ("Colour-matched commissioned paint", "personalisation", 48_000, "commissioned,match,sample,unique", "Colour matched to a client sample."),
    ("Bespoke clock face", "personalisation", 9_000, "clock,dial,detail", "Commissioned dashboard clock."),
    # Technology
    ("Night vision and wildlife detection", "technology", 13_000, "night,vision,wildlife,rural", "Thermal night-vision display."),
    ("Head-up display", "technology", 7_000, "head-up,hud,display", "Full-colour head-up display."),
    ("Advanced driver assistance suite", "technology", 11_000, "assistance,adas,safety,motorway", "Lane and adaptive cruise suite."),
    ("Self-levelling wheel centres", "technology", 4_500, "wheel,centres,detail,standing", "Always-upright wheel badges."),
    ("Panoramic glass roof", "technology", 16_000, "panoramic,glass,roof,light", "Full-length glazed roof."),
    ("Rear-seat massage and recline", "rear", 14_000, "massage,recline,comfort,relaxation", "Rear comfort seating suite."),
    ("Acoustic double glazing", "technology", 9_500, "acoustic,quiet,silence,noise", "Laminated acoustic glazing."),
    ("Silent-cabin acoustic package", "technology", 15_000, "silent,quiet,hush,serene", "Additional cabin damping."),
    ("Regenerative braking calibration", "technology", 6_000, "regen,braking,electric,efficiency", "Tuned regenerative response."),
    ("Wireless rear device charging", "technology", 2_500, "charging,wireless,devices", "Rear wireless charging."),
)

# (model, region, status, lead_min_months, lead_max_months)
AVAILABILITY: tuple[tuple[str, str, str, int, int], ...] = (
    ("Phantom", "EU", "limited", 9, 14), ("Ghost", "EU", "available", 6, 9),
    ("Cullinan", "EU", "available", 6, 9), ("Spectre", "EU", "available", 6, 9),
    ("Phantom", "UK", "limited", 9, 14), ("Ghost", "UK", "available", 6, 9),
    ("Cullinan", "UK", "limited", 9, 14), ("Spectre", "UK", "available", 6, 9),
    ("Phantom", "US", "limited", 9, 14), ("Ghost", "US", "available", 6, 9),
    ("Cullinan", "US", "available", 6, 9), ("Spectre", "US", "limited", 9, 14),
    ("Phantom", "GCC", "available", 6, 9), ("Ghost", "GCC", "available", 6, 9),
    ("Cullinan", "GCC", "available", 6, 9), ("Spectre", "GCC", "limited", 9, 14),
)

# (region, uplift_factor, note)
REGIONS: tuple[tuple[str, float, str], ...] = (
    ("EU", 1.00, "Pricing baseline and broadest allocation."),
    ("UK", 1.00, "Narrow roads and urban parking favour Ghost."),
    ("US", 1.03, "Long distances; Spectre limited by charging network."),
    ("GCC", 1.03, "Heat and sand dominate; satin finishes preferred."),
)

# (rule, severity)
CONSTRAINTS: tuple[tuple[str, str], ...] = (
    ("Technical carbon-fibre twill should not be paired with a ceremonial white exterior.", "warn"),
    ("Hotspur Red cabin should not be paired with Magma Red paint; keep one expressive.", "warn"),
    ("23-inch wheels degrade rear-compartment ride and should not be offered on chauffeur briefs.", "warn"),
    ("A vegan commission must use no leather at any touchpoint, including the wheel.", "block"),
    ("Gallery commissions are scheduled by the artist and cannot carry a fixed delivery date.", "warn"),
)
