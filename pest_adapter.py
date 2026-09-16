#!/usr/bin/env python3
"""
Pest Detection Adapter — Agricultural Insect & Mite Surveillance Module
========================================================================
Analyzes leaf imagery and crop symptomology to identify:
1. Pests: Spider Mites, Aphids, Whiteflies, Thrips, Leaf Miners, Caterpillars,
   Helopeltis (Tea Mosquito Bug), Mealybugs, and Stem Borers.
2. Infestation Risk & Severity Scoring (0-100%).
3. Integrated Pest Management (IPM): Biological bio-controls (predators, parasitoids),
   targeted organic sprays, and chemical control recommendations.
"""

from __future__ import annotations
import json
import os
from typing import Any
import numpy as np
from PIL import Image

PEST_DATABASE: dict[str, dict[str, Any]] = {
    "spider_mites": {
        "pest_name": "Two-Spotted Spider Mite",
        "scientific_name": "Tetranychus urticae",
        "category": "Acarina / Sap-Sucking Mite",
        "damage_pattern": "Fine chlorotic stippling (yellow pinhead speckles) and delicate silken webbing on abaxial leaf surfaces.",
        "affected_parts": "Underside of mature & young leaves, apical buds",
        "biological_control": "Introduce predatory mites (Phytoseiulus persimilis or Neoseiulus californicus) @ 2-5/sq.m. Spray cold-pressed Neem oil (5ml/L + soap emulsion).",
        "chemical_control": "Apply Spiromesifen 22.9% SC @ 1ml/L or Propargite 57% EC @ 2ml/L. Alternate with Fenpyroximate 5% EC @ 1ml/L to avoid resistance.",
        "cultural_management": "Overhead misting to elevate relative humidity (>65%); remove dry weeds around field perimeters to eliminate wild alternate hosts.",
    },
    "aphids": {
        "pest_name": "Aphids / Plant Lice",
        "scientific_name": "Aphis gossypii / Myzus persicae",
        "category": "Hemiptera / Phloem-Feeder",
        "damage_pattern": "Downward curling and crinkling of young foliage, sticky honeydew excretion, and secondary black sooty mold fungus.",
        "affected_parts": "Tender shoot tips, ventral vein ridges, flower buds",
        "biological_control": "Release green lacewing larvae (Chrysoperla carnea) or seven-spotted ladybird beetles (Coccinella septempunctata). Spray entomopathogenic fungus Verticillium lecanii @ 5g/L.",
        "chemical_control": "Foliar spray of Imidacloprid 17.8% SL @ 0.5ml/L or Acetamiprid 20% SP @ 0.3g/L or Thiamethoxam 25% WG @ 0.25g/L.",
        "cultural_management": "Set up bright yellow sticky traps (15-20 traps/acre); avoid excessive nitrogenous top-dressing which stimulates succulent aphid-attracting shoots.",
    },
    "whiteflies": {
        "pest_name": "Silverleaf Whitefly",
        "scientific_name": "Bemisia tabaci",
        "category": "Aleyrodidae / Vector Insect",
        "damage_pattern": "Chlorotic mottling, premature leaf senescence, sooty mold covering photosynthetic laminae, and potential geminivirus transmission.",
        "affected_parts": "Mid-canopy leaf undersides, apical shoots",
        "biological_control": "Deploy parasitoid wasps (Encarsia formosa or Eretmocerus eremicus). Apply entomopathogen Beauveria bassiana @ 5g/L during overcast hours.",
        "chemical_control": "Apply Diafenthiuron 50% WP @ 1g/L or Pyriproxyfen 10% EC @ 1.5ml/L (insect growth regulator) or Spirotetramat 15.3% OD @ 1ml/L.",
        "cultural_management": "Install UV-reflective silver plastic mulches to disorient flying adults; maintain 30 yellow sticky traps/acre.",
    },
    "thrips": {
        "pest_name": "Foliar Thrips",
        "scientific_name": "Thrips tabaci / Scirtothrips dorsalis",
        "category": "Thysanoptera / Rasping-Sucking",
        "damage_pattern": "Silvery or bronze sheen on leaf undersides with tiny black fecal flecks; upward boat-shaped leaf margin curling and stunted terminal buds.",
        "affected_parts": "Tender shoot tips, axillary nodes, floral parts",
        "biological_control": "Release pirate bugs (Orius insidiosus) and predatory mites (Amblyseius swirskii). Spray Pongamia / Karanja oil @ 5ml/L.",
        "chemical_control": "Spray Fipronil 5% SC @ 1.5ml/L or Spinetoram 11.7% SC @ 0.8ml/L or Spinosad 45% SC @ 0.3ml/L.",
        "cultural_management": "Install blue sticky traps (highly preferred by thrips over yellow); maintain clean sprinkler irrigation to dislodge nymphs.",
    },
    "leaf_miners": {
        "pest_name": "Serpentine Leaf Miner",
        "scientific_name": "Liriomyza trifolii",
        "category": "Agromyzidae / Larval Borer",
        "damage_pattern": "Prominent, winding serpentine whitish-translucent mines/tunnels gouged across the mesophyll layer, diminishing photosynthetic area.",
        "affected_parts": "Leaf blade mesophyll, lower and middle canopy leaves",
        "biological_control": "Conserve native parasitic eulophid wasps (Diglyphus isaea). Spray Neem seed kernel extract (NSKE 5%) to repel ovipositing females.",
        "chemical_control": "Apply Cyromazine 75% WP @ 0.3g/L or Abamectin 1.9% EC @ 0.75ml/L (translaminar action reaches internal larvae).",
        "cultural_management": "Hand-pinch and collect heavily mined lower leaves in solarized bags before pupae drop to soil; install yellow sticky cards for adult flies.",
    },
    "caterpillar_armyworm": {
        "pest_name": "Armyworm / Foliar Caterpillar",
        "scientific_name": "Spodoptera frugiperda / Spodoptera litura",
        "category": "Lepidoptera / Chewing Pest",
        "damage_pattern": "Irregular jagged margin defoliation, windowed leaf cuticle (skeletonized patches), and visible dark cylindrical frass granules.",
        "affected_parts": "Leaf blades, petioles, growing shoot crowns",
        "biological_control": "Foliar spray of Bacillus thuringiensis kurstaki (Bt) @ 2g/L or Spodoptera NPV (Nuclear Polyhedrosis Virus) @ 250 LE/acre during evening hours.",
        "chemical_control": "Apply Chlorantraniliprole 18.5% SC @ 0.4ml/L or Emamectin Benzoate 5% SG @ 0.4g/L or Flubendiamide 39.35% SC @ 0.25ml/L.",
        "cultural_management": "Install pheromone traps (4-5 traps/acre) for flight monitoring; collect and destroy clustered egg masses covered with buff-colored hairs.",
    },
    "helopeltis": {
        "pest_name": "Tea Mosquito Bug / Mirid Bug",
        "scientific_name": "Helopeltis theivora",
        "category": "Miridae / Sap-Puncturing Bug",
        "damage_pattern": "Circular water-soaked brown puncture spots on young leaves and shoots, turning necrotic black with shot-hole appearance; dieback of buds.",
        "affected_parts": "Young succulent leaves, tender shoots, pluckable flush",
        "biological_control": "Spray entomopathogenic formulation Beauveria bassiana 1x10^8 CFU/g @ 5g/L. Encourage weaver ants (Oecophylla smaragdina) in perennial crops.",
        "chemical_control": "Spray Thiamethoxam 25% WG @ 0.2g/L or Quinalphos 25% EC @ 2ml/L or Clothianidin 50% WDG @ 0.15g/L during early morning or dusk.",
        "cultural_management": "Remove broad-leaved weed hosts like Mikania micrantha; execute light pruning to improve aeration and light penetration in dense canopies.",
    },
    "mealybugs": {
        "pest_name": "Striped Mealybug",
        "scientific_name": "Ferrisia virgata / Phenacoccus solenopsis",
        "category": "Pseudococcidae / Scale Insect",
        "damage_pattern": "Cottony, waxy white flocculent colonies encrusting leaf veins and axils, causing crinkling, chlorosis, and sooty mold development.",
        "affected_parts": "Leaf axils, underside of main veins, apical growing shoots",
        "biological_control": "Release mealybug destroyer beetles (Cryptolaemus montrouzieri) @ 5-10 adults per infested plant.",
        "chemical_control": "Spray Buprofezin 25% SC @ 1.5ml/L or Spirotetramat 15.3% OD @ 1ml/L mixed with non-ionic surfactant/sticker (0.5ml/L) to penetrate waxy cuticle.",
        "cultural_management": "Band tree trunks/stems with grease or sticky barriers to prevent attendant ants from transporting and protecting mealybugs.",
    },
}


class PestDetectionAdapter:
    """
    Intelligent agronomic adapter for visual and algorithmic pest assessment.
    Combines computer vision heuristics (texture, stippling, edge jaggedness,
    color speckling) with Gemini multi-modal inference and crop-specific rules.
    """

    @classmethod
    def analyze(
        cls,
        image: Image.Image,
        disease_hint: str = "",
        plant_hint: str = "",
        custom_query: str = "",
    ) -> dict[str, Any]:
        """
        Runs multi-stage pest detection.
        Returns detailed pest identification, risk rating, and integrated management.
        """
        # 1. Computer Vision Heuristics
        cv_signals = cls._extract_cv_signals(image)

        # 2. Disease and Crop Correlation
        inferred_pest_key, base_conf = cls._correlate_disease_and_signals(
            disease_hint, plant_hint, cv_signals
        )

        # 3. Optional Gemini AI Multi-Modal Enrichment
        gemini_result = cls._try_gemini_pest_vision(image, disease_hint, plant_hint)
        if gemini_result and gemini_result.get("pest_detected") is not None:
            return gemini_result

        # 4. Deterministic Agronomic Output Construction
        if inferred_pest_key and inferred_pest_key in PEST_DATABASE:
            pest_data = PEST_DATABASE[inferred_pest_key]
            infestation_score = min(
                95.0,
                max(
                    20.0,
                    round(base_conf * 0.7 + cv_signals["anomaly_score"] * 0.3, 1),
                ),
            )
            risk_level = "Severe" if infestation_score >= 75 else "High" if infestation_score >= 50 else "Moderate" if infestation_score >= 30 else "Low"

            return {
                "pest_detected": True,
                "pest_name": pest_data["pest_name"],
                "scientific_name": pest_data["scientific_name"],
                "category": pest_data["category"],
                "risk_level": risk_level,
                "infestation_score": infestation_score,
                "damage_pattern": pest_data["damage_pattern"],
                "affected_parts": pest_data["affected_parts"],
                "biological_control": pest_data["biological_control"],
                "chemical_control": pest_data["chemical_control"],
                "cultural_management": pest_data["cultural_management"],
                "cv_signals": {
                    "stippling_index": round(cv_signals["stippling_ratio"], 2),
                    "edge_erosion": round(cv_signals["edge_erosion"], 2),
                    "dark_fleck_density": round(cv_signals["dark_fleck_density"], 2),
                },
            }

        # Clean/No obvious pest infestation
        return {
            "pest_detected": False,
            "pest_name": "No Destructive Pests Detected",
            "scientific_name": "Beneficial / Clean Canopy",
            "category": "Intact Foliage",
            "risk_level": "Low",
            "infestation_score": 8.5,
            "damage_pattern": "No chewing damage, galleries, waxy colonies, or sap-feeder stippling observed.",
            "affected_parts": "None",
            "biological_control": "Conserve resident predatory fauna (spiders, ladybird beetles, lacewings) by avoiding broad-spectrum synthetic pyrethroids.",
            "chemical_control": "No insecticide or acaricide application required at current scout threshold.",
            "cultural_management": "Maintain routine crop monitoring and clean border strips.",
            "cv_signals": {
                "stippling_index": round(cv_signals["stippling_ratio"], 2),
                "edge_erosion": round(cv_signals["edge_erosion"], 2),
                "dark_fleck_density": round(cv_signals["dark_fleck_density"], 2),
            },
        }

    @classmethod
    def _extract_cv_signals(cls, image: Image.Image) -> dict[str, float]:
        """Extracts low-level agricultural leaf signals from RGB array."""
        try:
            img_rgb = image.convert("RGB").resize((256, 256))
            arr = np.asarray(img_rgb, dtype=np.float32)

            r = arr[:, :, 0]
            g = arr[:, :, 1]
            b = arr[:, :, 2]

            # Stippling: high frequency pale yellow/white dots
            is_stipple = (r > 160) & (g > 160) & (b < 130)
            stippling_ratio = float(np.mean(is_stipple)) * 100.0

            # Dark flecks / puncture spots: very dark necrotic pinpoints
            is_dark_fleck = (r < 65) & (g < 65) & (b < 65)
            dark_fleck_density = float(np.mean(is_dark_fleck)) * 100.0

            # Edge erosion: color gradient standard deviation along outer perimeter
            perimeter = np.concatenate([arr[0, :, :], arr[-1, :, :], arr[:, 0, :], arr[:, -1, :]])
            edge_erosion = float(np.std(perimeter)) / 2.55

            anomaly_score = float(min(100.0, stippling_ratio * 4.0 + dark_fleck_density * 5.0 + (edge_erosion * 0.3)))

            return {
                "stippling_ratio": stippling_ratio,
                "dark_fleck_density": dark_fleck_density,
                "edge_erosion": edge_erosion,
                "anomaly_score": anomaly_score,
            }
        except Exception:
            return {
                "stippling_ratio": 2.0,
                "dark_fleck_density": 1.5,
                "edge_erosion": 15.0,
                "anomaly_score": 18.0,
            }

    @classmethod
    def _correlate_disease_and_signals(
        cls, disease_hint: str, plant_hint: str, signals: dict[str, float]
    ) -> tuple[str | None, float]:
        """Maps diagnosed plant/disease context and vision metrics to likely pest."""
        d_lower = (disease_hint or "").lower()
        p_lower = (plant_hint or "").lower()

        # Direct disease-pest vector associations
        if "helopeltis" in d_lower or "tea mosquito" in d_lower:
            return "helopeltis", 92.0
        if "algal" in d_lower:
            return "spider_mites", 65.0
        if "leaf spot" in d_lower or "spot" in d_lower:
            if signals["dark_fleck_density"] > 2.5:
                return "thrips", 68.0
        if "mosaic" in d_lower:
            return "whiteflies", 85.0

        # Heuristic detection based on CV signals
        if signals["stippling_ratio"] > 4.5:
            return "spider_mites", 78.0
        if signals["dark_fleck_density"] > 3.8:
            return "helopeltis" if "tea" in p_lower else "thrips", 72.0
        if signals["edge_erosion"] > 35.0:
            return "caterpillar_armyworm", 64.0

        # If high general anomaly score
        if signals["anomaly_score"] > 32.0:
            return "leaf_miners", 58.0

        return None, 15.0

    @classmethod
    def _try_gemini_pest_vision(
        cls, image: Image.Image, disease_hint: str, plant_hint: str
    ) -> dict[str, Any] | None:
        """Optional Gemini Multi-Modal Vision call when API key is available."""
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            return None

        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = (
                f"You are an agricultural entomology expert analyzing a leaf image.\n"
                f"Diagnosed Context: Crop: {plant_hint or 'Plant'}, Disease Hint: {disease_hint or 'None'}.\n"
                f"Carefully examine the leaf image for any insect, mite, or larval pest infestation (e.g. Spider Mites, "
                f"Aphids, Whiteflies, Thrips, Leaf Miners, Caterpillars/Armyworms, Helopeltis, Mealybugs).\n"
                f"Respond ONLY with a valid JSON object strictly matching this schema:\n"
                f"{{\n"
                f'  "pest_detected": true/false,\n'
                f'  "pest_name": "Common Name (e.g. Silverleaf Whitefly)",\n'
                f'  "scientific_name": "Scientific name",\n'
                f'  "category": "Family / Feeding Type",\n'
                f'  "risk_level": "Low" | "Moderate" | "High" | "Severe",\n'
                f'  "infestation_score": 0 to 100,\n'
                f'  "damage_pattern": "Precise visual damage description",\n'
                f'  "affected_parts": "Parts of leaf or shoot affected",\n'
                f'  "biological_control": "Beneficial bio-control and organic sprays",\n'
                f'  "chemical_control": "Approved targeted chemical sprays with dosage",\n'
                f'  "cultural_management": "Field sanitation and cultural prevention"\n'
                f"}}"
            )

            # Resize image to save bandwidth and stay well within rate limits
            thumb = image.convert("RGB")
            thumb.thumbnail((512, 512))

            resp = model.generate_content([prompt, thumb])
            raw_text = resp.text.strip()
            # Clean markdown codeblocks
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
            parsed = json.loads(raw_text.strip())
            return parsed
        except Exception:
            return None
