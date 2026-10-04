"""
Static seed catalog for physical-RWA candidate pool replenishment.

Named platforms only (not bare categories). Used when the live
discovery pool runs low. Each entry must have an official URL seed.
Ticker symbols are never used as identity.
"""

from __future__ import annotations

from typing import Any

# Categories used for diversity ranking.
PHYSICAL_RWA_CATEGORIES = (
    "real_estate",
    "farmland",
    "solar",
    "energy",
    "battery",
    "mining",
    "agriculture",
    "data_center",
    "infrastructure",
    "other_physical_rwa",
)

# Already live on Tokn — never rediscover as new candidates.
LIVE_PLATFORM_SLUGS = frozenset(
    {
        "glow",
        "glow-farm-1",
        "realt",
        "elmnts",
        "elmnts-chevron-mineral-rights-fund-public-marketing",
    }
)

# Curated named physical-RWA / tokenized-physical-asset seeds.
# These are starting points for investigation — not approvals.
SEED_CATALOG: list[dict[str, Any]] = [
    {
        "slug": "agro-digital-token",
        "display_name": "Agro Digital Token",
        "category": "farmland",
        "seeds": [
            "https://www.myagro.io/",
            "https://www.myagro.io/#tokenomics",
            "https://www.myagro.io/#rwa",
        ],
        "notes": "Named plantation / farmland RWA token (AGRO)",
        "aliases": ["myagro", "agro"],
        "discovery_source": "seed_catalog",
    },
    {
        "slug": "lofty",
        "display_name": "Lofty",
        "category": "real_estate",
        "seeds": [
            "https://www.lofty.ai/",
            "https://www.lofty.ai/marketplace",
            "https://docs.lofty.ai/",
        ],
        "notes": "Fractional real-estate property tokens",
        "aliases": ["lofty.ai", "lofty ai"],
        "discovery_source": "seed_catalog",
    },
    {
        "slug": "landshare",
        "display_name": "Landshare",
        "category": "farmland",
        "seeds": [
            "https://landshare.io/",
            "https://docs.landshare.io/",
            "https://landshare.io/rwa/",
        ],
        "notes": "Tokenized real-world farmland / property yield product",
        "aliases": ["land share"],
        "discovery_source": "seed_catalog",
    },
    {
        "slug": "blocksquare",
        "display_name": "Blocksquare",
        "category": "real_estate",
        "seeds": [
            "https://blocksquare.io/",
            "https://docs.blocksquare.io/",
            "https://blocksquare.io/tokenize/",
        ],
        "notes": "Real-estate tokenization protocol / property exposure",
        "aliases": ["bst"],
        "discovery_source": "seed_catalog",
    },
    {
        "slug": "realio",
        "display_name": "Realio Network",
        "category": "real_estate",
        "seeds": [
            "https://realio.network/",
            "https://docs.realio.network/",
            "https://realio.network/ecosystem",
        ],
        "notes": "Real-world asset issuance network focused on real estate / alternatives",
        "aliases": ["realio-network", "rio"],
        "discovery_source": "seed_catalog",
    },
    {
        "slug": "tangible",
        "display_name": "Tangible",
        "category": "other_physical_rwa",
        "seeds": [
            "https://www.tangible.store/",
            "https://docs.tangible.store/",
            "https://www.tangible.store/marketplace",
        ],
        "notes": "Tokenized physical luxury / real-world asset marketplace",
        "aliases": ["tnbl"],
        "discovery_source": "seed_catalog",
    },
    {
        "slug": "energy-web",
        "display_name": "Energy Web",
        "category": "energy",
        "seeds": [
            "https://www.energyweb.org/",
            "https://docs.energyweb.org/",
            "https://www.energyweb.org/technology",
        ],
        "notes": "Energy infrastructure decentralization — may be utility/DePIN not asset claim; investigate carefully",
        "aliases": ["ewt", "energyweb"],
        "discovery_source": "seed_catalog",
    },
    {
        "slug": "toucan-protocol",
        "display_name": "Toucan Protocol",
        "category": "other_physical_rwa",
        "seeds": [
            "https://toucan.earth/",
            "https://docs.toucan.earth/",
            "https://toucan.earth/carbon-bridge",
        ],
        "notes": "On-chain carbon credit / environmental asset bridging — physical-world credit exposure",
        "aliases": ["toucan", "tco2"],
        "discovery_source": "seed_catalog",
    },
    {
        "slug": "mineralized",
        "display_name": "Mineralized",
        "category": "mining",
        "seeds": [
            "https://mineralized.io/",
            "https://mineralized.io/#how-it-works",
        ],
        "notes": "Mining / mineral-rights adjacent tokenization project",
        "aliases": [],
        "discovery_source": "seed_catalog",
    },
    {
        "slug": "digishares",
        "display_name": "DigiShares",
        "category": "real_estate",
        "seeds": [
            "https://www.digishares.io/",
            "https://www.digishares.io/platform",
        ],
        "notes": "Real-estate / alternative-asset tokenization platform",
        "aliases": [],
        "discovery_source": "seed_catalog",
    },
    {
        "slug": "parcl",
        "display_name": "Parcl",
        "category": "real_estate",
        "seeds": [
            "https://www.parcl.co/",
            "https://docs.parcl.co/",
            "https://app.parcl.co/",
        ],
        "notes": "Real-estate price exposure / property market synthetic — verify physical-asset claim carefully",
        "aliases": ["prcl"],
        "discovery_source": "seed_catalog",
    },
    {
        "slug": "realt-platform",
        "display_name": "RealT (platform discovery skip)",
        "category": "real_estate",
        "seeds": ["https://realt.co/"],
        "notes": "Already live as Tokn adapter platform — catalog sentinel for dedupe",
        "aliases": ["realt", "real token"],
        "discovery_source": "seed_catalog",
        "skip": True,
    },
    {
        "slug": "glow-protocol",
        "display_name": "Glow (platform discovery skip)",
        "category": "solar",
        "seeds": ["https://www.glow.org/"],
        "notes": "Already live as Tokn adapter platform — catalog sentinel for dedupe",
        "aliases": ["glow", "glw"],
        "discovery_source": "seed_catalog",
        "skip": True,
    },
]

# Generic DePIN / network-utility names that must not be preferred as physical RWA.
GENERIC_DEPIN_BLOCKLIST = frozenset(
    {
        "helium",
        "render",
        "filecoin",
        "bittensor",
        "akash",
        "io-net",
        "ionet",
        "nosana",
        "grass",
        "hivemapper",
        "dimo",
        "wifi-map",
        "wifi",
        "theta",
        "livepeer",
        "arweave",
        "storj",
        "aethir",
        "spacecoin",
    }
)

PHYSICAL_MARKERS = (
    "real estate",
    "real-estate",
    "rental",
    "property",
    "farmland",
    "farm land",
    "agriculture",
    "agricultural",
    "solar farm",
    "solar panel",
    "renewable",
    "battery storage",
    "energy storage",
    "mining",
    "mining royalty",
    "net smelter",
    "mineral",
    "mineral rights",
    "commodity",
    "carbon credit",
    "carbon",
    "tokenized real",
    "fractional ownership",
    "physical asset",
    "real-world asset",
    "real world asset",
    "rwa",
    "data center",
    "datacenter",
    "infrastructure financing",
    "lease",
    "plantation",
    "luxury",
)

GENERIC_DEPIN_MARKERS = (
    "run a node",
    "run the node",
    "operate a node",
    "node operator",
    "provide compute",
    "gpu host",
    "host a miner",
    "contribute hardware",
    "mine helium",
    "hotspot",
    "bandwidth sharing",
    "storage provider",
    "filecoin miner",
    "render node",
    "depin network token",
)

OWNERSHIP_EXPOSURE_MARKERS = (
    "ownership",
    "fractional",
    "royalty",
    "revenue share",
    "rent",
    "yield from",
    "backed by",
    "claim on",
    "economic exposure",
    "financing",
    "dividend",
    "distribution",
    "nsr",
    "cash flow",
    "cashflow",
)
