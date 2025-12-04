
from typing import Dict

class MBATools:
    def swot(self, topic: str) -> str:
        topic = topic or "the business"
        return (
            f"SWOT analysis for {topic}:\n\n"
            "Strengths:\n- ...\n\nWeaknesses:\n- ...\n\nOpportunities:\n- ...\n\nThreats:\n- ..."
        )

    def pestle(self, topic: str) -> str:
        topic = topic or "the business"
        return (
            f"PESTLE analysis for {topic}:\n\nPolitical:\n- ...\n\nEconomic:\n- ...\n\n"
            "Social:\n- ...\n\nTechnological:\n- ...\n\nLegal:\n- ...\n\nEnvironmental:\n- ..."
        )

    def porters(self, topic: str) -> str:
        return (
            "Porter's Five Forces:\n1. Threat of new entrants: ...\n"
            "2. Bargaining power of buyers: ...\n3. Bargaining power of suppliers: ...\n"
            "4. Threat of substitutes: ...\n5. Competitive rivalry: ..."
        )

    def bcg(self, topic: str) -> str:
        return "BCG Matrix explanation and recommended placement of product(s)."

    def ansoff(self, topic: str) -> str:
        return "Ansoff Matrix strategies: Market Penetration, Market Development, Product Development, Diversification."
