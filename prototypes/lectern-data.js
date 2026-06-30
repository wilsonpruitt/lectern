/* Real Proper 23 (28) Year A data — output of the existing Lectern generators
   (sermon_connect.py, hymns/tag_connect.py, call_to_worship.py). This object is
   also a sketch of the per-occasion data contract the static shell would consume. */
window.LECTERN = {
  occasion: {
    id: "proper-23-28-a",
    name: "Proper 23 (28)",
    year: "A",
    season: "Season after Pentecost",
    exampleDate: "Oct 12",
    note: "The complementary track converges on one image — the banquet: the feast on the mountain (Isa 25), the table prepared (Ps 23), the wedding hall thrown open to the streets (Matt 22).",
  },

  tracks: {
    complementary: {
      label: "Complementary",
      readings: [
        { role: "First",   ref: "Isaiah 25:1–9" },
        { role: "Psalm",   ref: "Psalm 23" },
        { role: "Epistle", ref: "Philippians 4:1–9" },
        { role: "Gospel",  ref: "Matthew 22:1–14" },
      ],
      sermons: [
        { title: "On the Wedding Garment", author: "John Wesley", text: "Matthew 22:12",
          tags: ["garment-and-robe", "table-and-feast"], score: 3.0,
          note: "Wesley's own sermon on this Sunday's Gospel." },
        { title: "Sermon 101 — The Duty of Constant Communion", author: "John Wesley", text: "Luke 22:19",
          tags: ["kingdom-of-god", "table-and-feast", "table-communion"], score: 3.0 },
        { title: "CW Sermon III", author: "Charles Wesley", text: "Luke 16:10",
          tags: ["comfort-and-consolation", "grace", "kingdom-of-god", "praise-and-exultation"], score: 3.2 },
        { title: "Justification by Faith", author: "John Wesley", text: "Romans 4:5",
          tags: ["grace", "joy", "kingdom-of-god"], score: 2.6 },
      ],
      hymns: [
        { hymnal: "UMH", number: 138, title: "The Lord's My Shepherd, I'll Not Want",
          tags: ["shepherd", "table-and-feast", "water", "valley-and-shadow", "trust"], score: 8.6 },
        { hymnal: "UMH", number: 136, title: "The King of Love My Shepherd Is",
          tags: ["shepherd", "table-and-feast", "water", "grace", "comfort-and-consolation"], score: 7.7 },
        { hymnal: "TFWS", number: 2126, title: "All Who Hunger Gather Gladly",
          tags: ["table-and-feast", "water", "hospitality-of-god", "grace", "joy"], score: 7.2 },
        { hymnal: "UMH", number: 339, title: "Come, Sinners, to the Gospel Feast",
          tags: ["table-and-feast", "hospitality-of-god", "grace", "kingdom-of-god"], score: 6.1 },
        { hymnal: "UMH", number: 614, title: "For the Bread Which You Have Broken",
          tags: ["table-and-feast", "bread", "thanksgiving"], score: 4.6 },
      ],
    },
    semicontinuous: {
      label: "Semicontinuous",
      readings: [
        { role: "First",   ref: "Exodus 32:1–14" },
        { role: "Psalm",   ref: "Psalm 106:1–6, 19–23" },
        { role: "Epistle", ref: "Philippians 4:1–9" },
        { role: "Gospel",  ref: "Matthew 22:1–14" },
      ],
      sermons: [
        { title: "Justification by Faith", author: "John Wesley", text: "Romans 4:5",
          tags: ["fear-and-trembling", "grace", "penitence", "repentance", "kingdom-of-god"], score: 4.8 },
        { title: "The Wilderness State", author: "John Wesley", text: "John 16:22",
          tags: ["grace", "joy", "penitence", "repentance", "wilderness"], score: 4.7 },
        { title: "The Lord Our Righteousness", author: "John Wesley", text: "Jeremiah 23:6",
          tags: ["fear-and-trembling", "grace", "penitence", "repentance"], score: 3.8 },
        { title: "The Spirit of Bondage and of Adoption", author: "John Wesley", text: "Romans 8:15",
          tags: ["grace", "kingdom-of-god", "penitence", "repentance"], score: 3.6 },
      ],
      hymns: [
        { hymnal: "UMH", number: 269, title: "Lord, Who Throughout These Forty Days",
          tags: ["penitence", "wilderness", "temptation-and-testing"], score: 3.6 },
        { hymnal: "UMH", number: 339, title: "Come, Sinners, to the Gospel Feast",
          tags: ["table-and-feast", "hospitality-of-god", "grace", "kingdom-of-god"], score: 3.1 },
      ],
    },
  },

  // Call to Worship — complementary track (the banquet). Antiphonal: leader / CONGREGATION.
  calls: {
    track: "complementary",
    registers: [
      { key: "A", label: "Spare", desc: "house voice · 4–8 lines",
        lines: [
          ["Come to the table the Lord has spread.", "The feast is ready, and the doors are open."],
          ["We came hungry, and grief came with us.", "God will swallow up death and wipe every tear away."],
          ["The invitation has gone out into the streets.", "We heard it, and we have come."],
          ["Come, let us worship the God who sets the table.", "We come to the feast. Amen."],
        ] },
      { key: "B", label: "Immersive", desc: "sensory anchor · building refrain",
        lines: [
          ["Can you smell it? The bread is warm, the cup is poured, the table runs longer than your eyes can follow.", "There is a place for you at this table."],
          ["Come in from the road and the long week — come hungry, come grieving, come just as you are.", "There is a place for you at this table."],
          ["For God is spreading a feast on the mountain, swallowing up death, wiping the tears from every face.", "There is a place for you at this table."],
          ["So pull up a chair, friends. The host has been waiting for you.", "There is a place for you at this table. Thanks be to God!"],
        ] },
      { key: "C", label: "Hybrid", desc: "economy + one refrain",
        lines: [
          ["Smell the bread; the table is set.", "There is room for you here."],
          ["We come in from the road, hungry and grieving.", "There is room for you here."],
          ["God spreads the feast and wipes away every tear.", "There is room for you here."],
          ["Come, let us worship the God who keeps our place.", "We come to the table. Thanks be to God."],
        ] },
    ],
  },
};
