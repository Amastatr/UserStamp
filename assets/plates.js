/* The Plates: the image record of the Haus, entries as data, not markup.
   Add a plate by adding an object; index.html teases from this list and
   plates.html renders all of it. Captions are carried verbatim from the
   v19 exhibition and the Biographage record; write new ones in the house
   register and mark the section COPY:DRAFT until confirmed.
   Fields: src, alt, label (mono, short), text (the reader's prose),
   line (prog | cast | bench | archive), pos (optional object-position). */
window.PLATES = [

  /* ── The Progression ─────────────────────────────────────── */
  {
    src: "assets/images/gun-show-red-rifle.jpg",
    alt: "A boy at a Texas gun show holds a long-barrelled rifle above his shoulder",
    label: "I · The culture",
    text: "A Texas gun show, a red rifle longer than the boy. The Valley's first language was weapons; every household knew the vocabulary. The interest was real and the inheritance was real and both predate any later position taken against either.",
    line: "prog"
  },
  {
    src: "assets/images/backyard-target-mcallen.jpg",
    alt: "A boy in a striped shirt, sighting a pistol at a target board in a backyard",
    label: "II · The hand learns",
    text: "Backyard. Striped shirt. A target nailed to a fence in McAllen. Before any argument about force, force was a thing the body practiced.",
    line: "prog"
  },
  {
    src: "assets/images/father-green-ram-papeleria.jpg",
    alt: "A man stands beside a deep-green Dodge Ram pickup in front of a two-story Mexican papelería",
    label: "III · The inheritance",
    text: "Dad, his green Ram 1500, the papelería at the corner. He died when I was twenty. The engineering came first; the loss sealed it. The armor-only commitment was sealed with grief, not pivot.",
    line: "prog"
  },
  {
    src: "assets/images/first-metals-m2-and-6061.jpg",
    alt: "Two rectangular metal plates marked out with cut lines on a cutting mat: a hardened M2 steel plate and a 6061 aluminum plate",
    label: "IV · The first metals",
    text: "West Campus apartment, Austin. Plate left: 0.05 inch hardened M2 tool steel, $120 from McMaster-Carr, Northern European origin. Plate right: 6 by 12 inch 6061 aerospace-grade aluminum. Out of frame: a child's first prototype was napkins and cream-colored duct tape. Begin with what is on the desk.",
    line: "prog"
  },
  {
    src: "assets/images/the-becoming-face-shield.jpg",
    alt: "A young man in a mirror selfie wearing a blue face shield, yellow welding apron, and welding gauntlets",
    label: "V · The becoming",
    text: "Austin apartment bathroom, face shield down, leather apron, welder's gauntlets. The plate is 1075 blue-tempered spring steel. The work is now armor: multi-hit ballistic panels engineered against the failure modes that ceramic-only competitors share. The body of the boy who held the rifle and the body of the man who builds the panel are the same body. The form has changed; the inheritance is still moving.",
    line: "prog",
    pos: "center 30%"
  },

  /* ── The First Castings ──────────────────────────────────── */
  {
    src: "assets/images/casting-mix-by-hand.jpg",
    alt: "Grey wet concrete worked with a trowel in a red mixing tub",
    label: "The mix, worked by hand",
    text: "Concrete and mortar, mixed by hand and by drill, before the enterprise had a name. Garage bench, Rio Grande Valley, roughly eight years ago.",
    line: "cast"
  },
  {
    src: "assets/images/casting-rebar-bucket.jpg",
    alt: "Concrete in a blue bucket with rebar and a threaded rod standing vertically as reinforcement",
    label: "Reinforced with rebar",
    text: "Poured into buckets and reinforced with rebar and threaded rod: the first reinforcement schemes, learned by casting them.",
    line: "cast"
  },
  {
    src: "assets/images/casting-demolded.jpg",
    alt: "A demolded cylindrical concrete specimen resting on a concrete floor",
    label: "Demolded specimen",
    text: "Demolded and read like a record: how the body had set, where the aggregate sat, what the cure had done.",
    line: "cast"
  },
  {
    src: "assets/images/casting-drilled.jpg",
    alt: "A drill resting on a cured concrete disc with test holes bored into it",
    label: "Drilled to read the set",
    text: "Drilled to read how the body had set: test holes as the first instrumentation the bench owned.",
    line: "cast"
  },
  {
    src: "assets/images/casting-broken.jpg",
    alt: "Cured concrete broken into chunks on a garage floor",
    label: "Broken to find the failure",
    text: "Broken apart to find where it failed. The instinct was protective from the start: a body built to take the hit, not to deal one. Years later, ImpactStop.",
    line: "cast"
  },
  {
    src: "assets/images/shot-article-impact-face.jpg",
    alt: "The impact face of a tape-wrapped cast article, densely cratered with metal fragments seated in the craters",
    label: "Impact face",
    text: "The last article is the one that matters. A cast core wrapped in tape, shot many times across a single face. The front holds the craters and the embedded fragments.",
    line: "cast"
  },
  {
    src: "assets/images/shot-article-reverse.jpg",
    alt: "The reverse face of the same article, the tape wrap largely intact with only a few shallow marks",
    label: "Reverse · nothing came through",
    text: "The reverse of the same article is nearly whole, and nothing came through. The casting frames are from the time; the shot article survives.",
    line: "cast"
  },

  /* ── The Bench ───────────────────────────────────────────── */
  {
    src: "assets/images/tool-steel-heat-bloom.jpg",
    alt: "A tool-steel plate marked out on a cutting mat, an oval heat-bloom across its face from tempering",
    label: "Tool steel, tempered",
    text: "Tool steel, tempered and marked out. The bloom is the heat record.",
    line: "bench"
  },
  {
    src: "assets/images/sodium-silicate-water-glass.jpg",
    alt: "Sodium silicate water glass",
    label: "Binder · sodium silicate",
    text: "Water glass: the mineral matrix. Sold as a carton and concrete sealer; here it is the structural glass, curing by drying and carbonation rather than by a chemical resin.",
    line: "bench"
  },
  {
    src: "assets/images/cab-o-sil-fumed-silica.jpg",
    alt: "CAB-O-SIL fumed silica",
    label: "Rheology · fumed silica",
    text: "CAB-O-SIL. A few percent thickens the mix and stops it draining out of vertical and radial sections before it sets. The label calls it gap and radial fill; the property is the same.",
    line: "bench"
  },
  {
    src: "assets/images/fibreglast-544-kevlar-pulp.jpg",
    alt: "FibreGlast 544 Kevlar pulp",
    label: "Toughening · aramid pulp",
    text: "FibreGlast 544 Kevlar pulp: short aramid fibers added for abrasion resistance and to reinforce high-impact areas, holding a cracked region together rather than letting it open.",
    line: "bench"
  },

  /* ── The Archive ─────────────────────────────────────────── */
  {
    src: "assets/images/graf-spee-bound-volume.jpg",
    alt: "A bound volume of the Illustrated London News, open to a January 1940 page showing the Admiral Graf Spee burning off Montevideo",
    label: "The Graf Spee · January 1940",
    text: "The Illustrated London News, January 1940: the Graf Spee in smoke off Montevideo, found in a bound volume at the Perry-Castañeda. The Historiotempo keeps the coordinate: the event, the place, the date, and the day the record of it was found.",
    line: "archive"
  },
  {
    src: "assets/images/author-as-a-boy-gun-show.jpg",
    alt: "The author as a boy at a gun show, holding a rifle",
    label: "The author as a boy",
    text: "The author as a boy, at a gun show. Two photographs a generation apart begin the inheritance record; this is the first.",
    line: "archive"
  },
  {
    src: "assets/images/father-seated-1990s.jpg",
    alt: "His father seated at a table, patterned shirt and jeans, a 1990s print",
    label: "His father, seated · the 1990s",
    text: "His father, seated. The 1990s. Rafael Mendoza Ramírez Valencia, 1963 to 2025, Biographage No. 001: the registers begin with a person.",
    line: "archive",
    pos: "center 20%"
  },
  {
    src: "assets/images/father-grandfather-suburban-fig06.jpg",
    alt: "Two men beside a dark Suburban, the father at the front fender in a white short-sleeve shirt, the grandfather at his side",
    label: "Father and grandfather · Fig. 06",
    text: "Two men beside a dark Suburban on the GMT400 platform, the long two-door body filling the frame. The father stands at the front fender in a white short-sleeve shirt; the grandfather, Adán Mendoza Ramírez, at his side. A paved drive under the tires, trees and open sky behind. McAllen, the mid-1990s.",
    line: "archive"
  },
  {
    src: "assets/images/father-grandfather-suburban-fig07.jpg",
    alt: "The same scene from the other side in low winter sun, the father leaning on the front fender, the grandfather in blue at the front of the truck",
    label: "The other side · Fig. 07",
    text: "The same scene from the other side, in low winter sun. The father leans back against the front fender, a mustache, a watch on his left wrist, one hand on the hood, the amber markers lit beside him. The grandfather stands at the front of the truck in blue. Single-story houses and bare trees behind.",
    line: "archive"
  },
  {
    src: "assets/images/great-grandfather-rafael-mendoza-portrait.jpg",
    alt: "A studio portrait in muted color: a young man in a wide-brimmed pale sombrero and open-collar white shirt, looking level into the camera",
    label: "Rafael Mendoza · Biographage No. 003",
    text: "A studio portrait, muted color. A young man in a wide-brimmed pale sombrero and an open-collar white shirt, dark hair and a mustache, looking level into the camera against a mottled backdrop. The great-grandfather, first of the line's four Rafaels in the record.",
    line: "archive"
  }
];
