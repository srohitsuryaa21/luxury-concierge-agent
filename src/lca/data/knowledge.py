"""Retrievable product knowledge, stored as rows rather than documents.

This is the only knowledge source in the system. Each row is one focused
passage, which is deliberate: whole-document embeddings average several topics
into a single vector and retrieve poorly, so the unit of storage is the unit we
want retrieval to return.

(title, category, content, keywords)
"""

from __future__ import annotations

KNOWLEDGE: tuple[tuple[str, str, str, str], ...] = (
    # -- Model positioning -------------------------------------------------
    (
        "Phantom positioning", "positioning",
        (
            "Phantom is the ceremonial flagship, for clients who value presence, privacy and a "
            "chauffeur-led experience. It is strongest for formal events, legacy clients and "
            "highly bespoke commissions, and carries the widest bespoke envelope in the range. "
            "It is the default recommendation when a brief is elegant but unspecific."
        ),
        "phantom,flagship,ceremonial,formal,presence,chauffeur,legacy,bespoke",
    ),
    (
        "Ghost positioning", "positioning",
        (
            "Ghost is the discreet driver's saloon, for entrepreneurs and executives who want "
            "luxury without theatrical presence. It is the correct answer when a client says "
            "they will drive themselves, or asks for something understated, low-key or not too "
            "flashy. Narrow roads and tight urban parking make it the strongest UK default."
        ),
        "ghost,discreet,driver,understated,executive,entrepreneur,urban,saloon",
    ),
    (
        "Cullinan positioning", "positioning",
        (
            "Cullinan is the all-terrain luxury SUV for families, estates, mountain routes and "
            "regional travel. It suits safari, adventure and outdoor briefs, and any commission "
            "mentioning children, luggage volume or an elevated seating position. Practicality "
            "beats presence in every trade-off for this client."
        ),
        "cullinan,suv,family,estate,mountain,terrain,safari,children,luggage,adventure",
    ),
    (
        "Spectre positioning", "positioning",
        (
            "Spectre is the electric grand tourer for clients wanting quiet, modern, sustainable "
            "luxury with effortless power delivery. It is the strongest answer for zero-emission, "
            "city-centre and sustainability-led briefs. Confirm the client's home charging "
            "arrangement before recommending it."
        ),
        "spectre,electric,ev,quiet,sustainable,zero-emission,grand tourer,charging,city",
    ),
    (
        "Choosing between models", "positioning",
        (
            "When two models could fit, resolve on usage rather than taste. A client who is "
            "driven should be offered Phantom or Ghost. A client who drives should be offered "
            "Ghost or Cullinan. Presence ranks Phantom, Cullinan, Spectre, Ghost. Practicality "
            "ranks Cullinan, Phantom, Ghost, Spectre. A model named in the brief always "
            "overrides inference."
        ),
        "choosing,comparison,presence,practicality,usage,trade-off,named model",
    ),
    # -- Materials ---------------------------------------------------------
    (
        "Choosing a leather direction", "materials",
        (
            "Choose the leather first: it governs how bright or enveloping the cabin reads. "
            "Grace White is the formal, bright, ceremonial default. Ardent Tan gives warmth and "
            "craft character for warm, brown, cognac and chestnut briefs. Black Grace is the "
            "formal chauffeur standard and hides wear in high-use rear compartments."
        ),
        "leather,cabin,grace white,ardent tan,black grace,warm,formal,brightness",
    ),
    (
        "Vegan and sustainable cabins", "materials",
        (
            "Scivaro Grey technical textile with responsibly sourced leather accents is the "
            "sustainable cabin direction and the only correct answer for vegan, cruelty-free or "
            "plant-based requests. For a strictly vegan commission, specify textile throughout "
            "with no leather anywhere, including the steering wheel, gear selector and grab "
            "handles. Pair it with sustainably harvested bamboo veneer."
        ),
        "vegan,sustainable,cruelty-free,plant-based,scivaro,textile,bamboo,animal welfare",
    ),
    (
        "Expressive and rare cabin colours", "materials",
        (
            "Hotspur Red suits crimson, scarlet and burgundy briefs; use it as a full cabin only "
            "for confident clients, otherwise propose it as piping. Forest Green is a rare "
            "commission that works against Emerald Aurora or Oyster Pearl. Navy Blue is the "
            "discreet alternative to black. Duotone cabins suit clients who want visible "
            "bespoke work."
        ),
        "hotspur,red,forest green,navy,duotone,expressive,rare,piping,distinctive",
    ),
    (
        "Calm and low-glare cabins", "materials",
        (
            "Anthracite Slate is the calm, low-glare option for charcoal and grey briefs and the "
            "strongest choice for long-distance touring. Seashell Cream suits ivory and soft "
            "ceremonial cabins where Grace White reads too clinical. Pale Obeche veneer lifts "
            "darker leathers considerably."
        ),
        "anthracite,slate,charcoal,grey,touring,glare,seashell,cream,obeche,calm",
    ),
    (
        "Veneer selection", "materials",
        (
            "Open-pore Circassian walnut supports warm heritage cabins and partners Ardent Tan. "
            "Piano Black suits modern, formal and electric configurations and is the default. "
            "Technical carbon-fibre twill suits performance and driver-focused briefs. Burr Oak "
            "is the heritage and traditional choice for legacy clients. Canadel panelling is the "
            "apex handcrafted option."
        ),
        "veneer,walnut,piano black,carbon,burr oak,canadel,heritage,performance,timber",
    ),
    (
        "Cabin coherence", "materials",
        (
            "Warm leather with a cool veneer reads as a mistake to most clients. Keep the cabin "
            "either warm throughout or cool throughout unless the client has explicitly asked "
            "for contrast. Stitch colour and coachline should tell one story."
        ),
        "coherence,warm,cool,contrast,stitch,coachline,mistake,pairing",
    ),
    # -- Paint -------------------------------------------------------------
    (
        "House palette finishes", "paint",
        (
            "Commissioned Midnight Sapphire is the house default for understated formal briefs. "
            "Black Diamond over Anthracite is the strongest formal chauffeur finish. Arctic "
            "White with a hand-painted coachline suits ceremonial, bridal and wedding usage. "
            "Bespoke Emerald Aurora fits nature, estate and forest briefs."
        ),
        "paint,midnight sapphire,black diamond,arctic white,emerald aurora,default,formal",
    ),
    (
        "Expressive commissioned colours", "paint",
        (
            "Burgundy Nocturne suits oxblood and claret briefs, deep enough to read formal in "
            "low light. Magma Red is the most expressive finish offered; pair it with a "
            "restrained cabin. Amethyst Twilight shifts between violet and charcoal with the "
            "light and suits collectors who ask for something unrepeatable."
        ),
        "burgundy,oxblood,claret,magma,red,amethyst,violet,collector,unrepeatable,expressive",
    ),
    (
        "Two-tone and regional finishes", "paint",
        (
            "Salamanca Blue over Andalusian White is the marine and nautical two-tone for "
            "coastal clients. English White over Silver Sand is the most discreet two-tone. "
            "Desert Gold satin is the regional signature for GCC and desert briefs: satin is "
            "markedly better than gloss at hiding fine sand abrasion. Two-tone finishes require "
            "an additional paint and cure cycle."
        ),
        "two-tone,salamanca,silver sand,desert gold,satin,gcc,sand,abrasion,coastal,nautical",
    ),
    (
        "Coachlines", "paint",
        (
            "Coachlines should match a cabin stitch colour when the client wants a coherent "
            "visual story. Conservative clients receive tonal coachlines; expressive clients can "
            "receive higher-contrast hand-painted lines. A hand-painted coachline is applied in "
            "a single pass by one specialist and cannot be corrected, which adds real lead time."
        ),
        "coachline,hand-painted,tonal,contrast,specialist,lead time,single pass",
    ),
    # -- Availability and timeline ----------------------------------------
    (
        "Lead time bands", "timeline",
        (
            "Lead times are directional. Available allocations usually take 6 to 9 months. "
            "Limited allocations usually take 9 to 14 months. Always quote the lower bound when "
            "testing a client's timeline. A brief asking for delivery inside the lower bound "
            "must be flagged as at risk during discovery, never after."
        ),
        "lead time,months,available,limited,allocation,timeline,at risk,discovery",
    ),
    (
        "What extends a lead time", "timeline",
        (
            "Hand-painted coachlines, gallery commissions, monograms and colour-matched bespoke "
            "paint each add specialist time that cannot be parallelised. Two-tone finishes add a "
            "full extra paint and cure cycle. Client-supplied materials must clear provenance "
            "checks before entering the build schedule."
        ),
        "extends,delay,specialist,gallery,monogram,colour match,provenance,schedule",
    ),
    (
        "Compressing a timeline", "timeline",
        (
            "Accepting a house palette finish rather than a commissioned colour is the single "
            "largest saving. Accepting an existing allocation rather than a new build slot is "
            "the second. Neither should be presented to the client as a downgrade."
        ),
        "compress,faster,house palette,allocation,build slot,saving,urgent",
    ),
    (
        "Commission stages", "process",
        (
            "A commission moves through discovery, specification, confirmation, build and "
            "handover. Lead time is measured from confirmation, when the deposit is taken and "
            "the build slot is allocated, not from first contact. Clients routinely "
            "misunderstand this, so state it explicitly in every proposal."
        ),
        "stages,discovery,specification,confirmation,build,handover,deposit,measured from",
    ),
    # -- Regional ----------------------------------------------------------
    (
        "GCC considerations", "regional",
        (
            "Heat is the dominant constraint. Recommend heat-reflective glazing, satin rather "
            "than gloss finishes, and lighter cabin colours that stay comfortable after standing "
            "in direct sun. Sand-sealed underbody protection suits any client mentioning desert "
            "or dune driving. Ceremonial and family commissions are both strong in Dubai, Riyadh "
            "and Doha. Regional pricing carries a modest uplift."
        ),
        "gcc,dubai,riyadh,doha,heat,sun,sand,desert,dune,arid,glazing,uplift,emirates",
    ),
    (
        "United States considerations", "regional",
        (
            "Distances are long and highways dominate, so prioritise touring comfort, rear "
            "refrigeration and extended luggage over off-road capability. Spectre allocation is "
            "limited pending charging network expansion, so confirm home charging first. "
            "Regional pricing carries a modest uplift. Schedule servicing by distance, not "
            "calendar."
        ),
        "us,usa,america,new york,california,highway,touring,distance,charging,uplift",
    ),
    (
        "United Kingdom considerations", "regional",
        (
            "Roads are narrow and urban parking is tight, making Ghost the strongest default and "
            "Cullinan a considered rather than automatic choice. Weather favours darker and "
            "two-tone finishes that hide road film. Cold-climate packs are worth proposing more "
            "often than clients expect."
        ),
        "uk,britain,london,narrow,parking,weather,road film,cold,ghost",
    ),
    (
        "European Union considerations", "regional",
        (
            "The broadest allocation of any region and the pricing baseline. City-centre "
            "emission zones make Spectre unusually compelling for urban clients. Alpine and ski "
            "clients should be shown Cullinan with the cold-climate pack and all-terrain tyres."
        ),
        "eu,europe,baseline,emission zone,urban,alpine,ski,snow,winter,allocation",
    ),
    (
        "Inferring a region", "regional",
        (
            "Never infer a region from a client's nationality. Infer it from where the car will "
            "be delivered and driven, and if the brief does not say, ask. Region changes "
            "availability, price and which options are genuinely useful rather than decorative."
        ),
        "region,infer,nationality,delivery,driven,ask,assumption",
    ),
    # -- Wheels ------------------------------------------------------------
    (
        "Wheel selection", "wheels",
        (
            "The 22-inch part-polished forged wheel is the house default. The 21-inch disc wheel "
            "is the chauffeur and ceremonial choice: the taller sidewall improves "
            "rear-compartment ride, which is all that matters when the client is a passenger. "
            "The 23-inch forged alloy suits driver-focused briefs at a real cost in low-speed "
            "compliance. The 23-inch aero wheel is the Spectre partner and contributes to range."
        ),
        "wheels,22-inch,21-inch,23-inch,forged,disc,aero,ride,sidewall,compliance",
    ),
    (
        "Wheels and terrain", "wheels",
        (
            "The 22-inch all-terrain forged wheel with protective finish is for mountain, estate, "
            "safari and off-road use; the protective finish resists kerb and gravel damage that "
            "would ruin a polished rim. Terrain outranks performance: a client who mentions both "
            "wants a wheel that survives gravel, not one that sharpens turn-in."
        ),
        "all-terrain,gravel,kerb,mountain,estate,safari,off-road,snow,protective,terrain",
    ),
    (
        "Wheel guidance", "wheels",
        (
            "Match the wheel to how the car is used, not how the client wants it to look. A "
            "client who asks for the largest wheel and is chauffeured daily will be unhappy "
            "within a month. Wheel finish should echo the brightwork, not the paint. Wheel "
            "changes after the build slot is confirmed do not affect lead time."
        ),
        "guidance,usage,largest,chauffeured,brightwork,finish,defer,change",
    ),
    # -- Options and technology -------------------------------------------
    (
        "Signature options", "options",
        (
            "The starlight headliner is the most requested feature in the range; the bespoke "
            "constellation variant renders a sky for a date chosen by the client and is the "
            "strongest emotional anchor in any proposal. Three signature options is the house "
            "standard - more reads as indecisive, not generous."
        ),
        "starlight,headliner,constellation,signature,three,emotional,anchor,requested",
    ),
    (
        "Audio and cabin technology", "options",
        (
            "Bespoke audio tuning is calibrated to the finished cabin because materials change "
            "the acoustic profile. The 18-speaker calibration suits any client mentioning music "
            "or concerts. Acoustic double glazing and the silent-cabin package suit clients who "
            "ask for quiet. Night vision suits rural and wildlife exposure."
        ),
        "audio,speakers,music,concert,acoustic,glazing,silent,quiet,night vision,rural",
    ),
    (
        "Chauffeur and rear-compartment options", "options",
        (
            "Privacy suite, champagne cooler and rear picnic tables form the chauffeur set. "
            "Laminated privacy glazing, rear business console and secure document safe suit a "
            "principal who works in the car and takes confidential calls. Rear-seat massage and "
            "recline suit long journeys in the back."
        ),
        "chauffeur,privacy,champagne,picnic,business,console,safe,confidential,massage,rear",
    ),
    (
        "Family and estate options", "options",
        (
            "Rear child-seat provisioning, cabin partition storage and rear entertainment "
            "tablets answer family briefs directly. All-terrain tyres, elevated ride height and "
            "the boot-mounted viewing suite form the estate set. The cabin pet suite and fitted "
            "golf-bag housing are small, specific and disproportionately well received when the "
            "client has mentioned the interest."
        ),
        "family,child,tablets,storage,estate,viewing,pet,dog,golf,tyres,ride height",
    ),
    (
        "Climate options", "options",
        (
            "Heat-reflective glazing and sand-sealed underbody protection form the GCC set. The "
            "cold-climate pack forms the alpine and winter set. Cabin air purification suits "
            "urban clients and allergy sensitivity."
        ),
        "climate,heat,glazing,sand,underbody,cold,alpine,winter,purification,allergy,urban",
    ),
    (
        "Apex personalisation", "options",
        (
            "A gallery commission by a named artist is the apex personalisation; the artist sets "
            "the schedule, not the factory, so never quote it against a fixed delivery date. "
            "Hand-painted monograms and door crests suit clients mentioning initials or "
            "heraldry. Propose one apex personalisation, not several - a commission carrying a "
            "gallery piece, a monogram, a bespoke colour and a constellation reads as unfocused."
        ),
        "gallery,artist,apex,monogram,crest,heraldry,initials,unrepeatable,collector,unfocused",
    ),
    (
        "Low-cost personalisation", "options",
        (
            "Stitch colour, piping, treadplate text and embroidered headrests are low-cost, "
            "high-impact, and can be decided late without affecting the build schedule. Offer "
            "them to any client who wants the car to feel personal but has a tight timeline."
        ),
        "stitch,piping,treadplate,embroidery,headrest,late,cheap,tight timeline,personal",
    ),
    # -- Sustainability ----------------------------------------------------
    (
        "Provenance records", "sustainability",
        (
            "The responsible material provenance pack documents the origin of every material in "
            "the commission - hides, textiles, timber and metals - issued as a bound record. "
            "Collectors increasingly request it regardless of whether sustainability motivated "
            "the purchase. Client-supplied materials must clear provenance checks before "
            "entering the build schedule."
        ),
        "provenance,origin,record,traceability,hides,timber,collector,bound,checks",
    ),
    (
        "Sustainability claims", "sustainability",
        (
            "Do not describe the range as carbon neutral. Do not describe leather as sustainable. "
            "Describe it as responsibly sourced and be prepared to show the provenance record. "
            "Sustainability-led clients ask harder questions than any other segment; answer with "
            "specifics or not at all. A client who catches an overstatement will not trust the "
            "rest of the proposal."
        ),
        "claims,carbon neutral,greenwashing,overstatement,exaggerating,credentials,honesty,trust",
    ),
    (
        "Regenerative drive briefing", "sustainability",
        (
            "A structured handover covering regenerative braking behaviour, charging strategy, "
            "range planning and battery care. Offer it with every Spectre commission and with "
            "any brief mentioning efficiency."
        ),
        "regenerative,braking,charging,range,battery,handover,briefing,efficiency,spectre",
    ),
    # -- Pricing -----------------------------------------------------------
    (
        "How the estimate is built", "pricing",
        (
            "Every figure produced during discovery is a directional estimate for sales "
            "discovery, not a binding quote, and must be labelled as such. The model sets the "
            "base; paint, leather, veneer, wheels and each option add their catalogue price; "
            "region applies an uplift for GCC and US commissions over the EU and UK baseline."
        ),
        "estimate,directional,quote,base,catalogue,uplift,region,binding,itemised",
    ),
    (
        "When the estimate exceeds the budget", "pricing",
        (
            "Do not silently reduce the specification to fit. Surface the gap and open a "
            "trim-level conversation. The levers, in the order they cost the client least "
            "emotionally: move from a commissioned colour to a house palette finish; reduce to "
            "the two signature options that matter most; move from an apex personalisation to "
            "cabin personalisation; change model tier only as a last resort."
        ),
        "over budget,exceeds,gap,trim,levers,reduce,house palette,last resort,downgrade",
    ),
    (
        "When the budget comfortably fits", "pricing",
        (
            "Do not pad the specification to consume the difference. Propose the correct "
            "commission and note the headroom. Clients who feel upsold do not return, and the "
            "headroom is better spent later on personalisation they choose themselves."
        ),
        "fits,headroom,padding,upsell,restraint,return,within budget",
    ),
    (
        "Currency", "pricing",
        (
            "Estimates are produced in EUR. A budget stated in another currency is currently "
            "read as its EUR figure, so confirm the currency explicitly with the client before "
            "treating a budget test as authoritative."
        ),
        "currency,eur,dollars,pounds,conversion,fx,confirm",
    ),
    # -- Constraints and conduct ------------------------------------------
    (
        "Combinations to avoid", "constraints",
        (
            "Do not pair technical carbon-fibre veneer with a ceremonial white exterior. Do not "
            "offer Hotspur Red as a full cabin alongside Magma Red paint - keep one of the two "
            "expressive. Do not propose 23-inch wheels for a chauffeur brief. Do not offer a "
            "vegan cabin with natural-grain leather accents."
        ),
        "avoid,clash,incompatible,carbon,ceremonial,red,23-inch,chauffeur,vegan,accents",
    ),
    (
        "Combinations that succeed", "constraints",
        (
            "Ardent Tan with Circassian walnut and a tonal coachline for warm heritage briefs. "
            "Scivaro Grey with bamboo veneer and aero wheels for sustainability briefs. Black "
            "Grace with Piano Black and 21-inch disc wheels for formal chauffeur work. "
            "Anthracite Slate with Pale Obeche for long-distance touring where glare matters."
        ),
        "succeed,pairing,combination,heritage,sustainability,chauffeur,touring,recommended",
    ),
    (
        "Escalation and honesty", "constraints",
        (
            "Where the estimate exceeds a stated budget, surface the gap rather than quietly "
            "reducing the specification. Where a timeline is at risk, say so in the same breath "
            "as the recommendation. A client who learns about a delay late will not commission "
            "again, and one whose risk was flagged honestly during discovery is markedly more "
            "likely to return."
        ),
        "escalation,honesty,surface,flag,risk,delay,late,trust,repeat,return",
    ),
    (
        "Client archetypes", "archetypes",
        (
            "The ceremonial client has an immovable event date, so test feasibility before any "
            "specification work. The chauffeur-led principal values privacy and never wants "
            "large wheels. The owner-driver wants capability without theatre. The family "
            "principal trades presence for practicality. The collector buys rarity and story, "
            "and lead time is not a constraint for them."
        ),
        "archetype,ceremonial,principal,owner-driver,family,collector,rarity,story,feasibility",
    ),
    (
        "Proposal documentation", "process",
        (
            "Every proposal should carry the configuration, the estimate with its confidence "
            "qualifier, the availability status with lead time, and the knowledge sources used. "
            "A proposal a client cannot audit is a proposal they will not sign."
        ),
        "proposal,documentation,audit,sources,confidence,qualifier,sign,transparency",
    ),
    (
        "Care of bespoke finishes", "aftercare",
        (
            "Satin finishes such as Desert Gold must never be machine polished. Hand-painted "
            "coachlines should be washed by hand along the line, not across it. Open-pore and "
            "bamboo veneers respond badly to solvent cleaners. Technical textiles resist stains "
            "better than leather but tolerate heat worse, so avoid steam cleaning entirely."
        ),
        "care,aftercare,satin,polish,coachline,wash,solvent,veneer,textile,steam,cleaning",
    ),
    (
        "Retained client relationship", "aftercare",
        (
            "Record the specification, the provenance pack and the personalisation story against "
            "the client, not the car. Clients commission repeatedly, and the second commission "
            "always references the first."
        ),
        "relationship,record,repeat,second commission,history,client file,story",
    ),
)
