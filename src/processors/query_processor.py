import logging
from typing import Dict, Any, List, Optional
import os
from openai import AsyncOpenAI
import json
import re

logger = logging.getLogger(__name__)

class QueryProcessor:
    """
    AI-driven query understanding and parameter extraction
    
    Capabilities:
    - Intent classification (component search, research overview, TRL query, etc.)
    - Entity extraction (components, technologies, specs)
    - Domain detection (embedded, power, EMC/EMI, etc.)
    - Regional preference extraction
    - Query expansion and refinement
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        
        # EE domain knowledge
        self.domains = {
            "embedded_systems": ["mcu", "microcontroller", "embedded", "rtos", "firmware", "arm", "cortex"],
            "power_management": ["pmic", "power", "converter", "regulator", "buck", "boost", "ldo", "gan", "sic"],
            "emc_emi": ["emc", "emi", "filter", "shielding", "noise", "interference", "compliance"],
            "analog": ["adc", "dac", "opamp", "analog", "amplifier", "sensor"],
            "rf_wireless": ["rf", "wireless", "ble", "lora", "wifi", "5g", "antenna", "zigbee"]
        }
        
        self.intents = [
            "component_search",      # "Find GaN power ICs"
            "research_overview",     # "What's new in SiC technology?"
            "trl_query",            # "What's the maturity of edge AI?"
            "supply_chain_check",   # "Is TPS54620 available?"
            "comparison",           # "Compare GaN vs SiC"
            "design_guidance"       # "How to design a buck converter?"
        ]
        
        logger.info("QueryProcessor initialized")
    
    async def process(self, query: str, context: str = "") -> Dict[str, Any]:
        """
        Process and understand query
        
        Args:
            query: User's natural language query
            context: Optional context from previous interactions
            
        Returns:
            Structured query understanding with:
            - intent: Primary intent
            - entities: Extracted entities (components, technologies)
            - domains: Relevant EE domains
            - parameters: Search parameters
            - routing: Provider routing decisions
        """
        try:
            logger.info(f"Processing query: {query}")
            
            # Quick pattern-based processing for simple queries
            if self._is_simple_query(query):
                return self._process_simple_query(query)
            
            # AI-powered processing for complex queries
            understanding = await self._ai_understand_query(query, context)
            
            # Enhance with domain knowledge
            understanding = self._enhance_with_domain_knowledge(understanding, query)
            
            # Generate routing decisions
            understanding["routing"] = self._generate_routing(understanding)
            
            logger.info(f"Query understood: intent={understanding['intent']}, domains={understanding['domains']}")
            
            return understanding
        
        except Exception as e:
            logger.error(f"Query processing error: {str(e)}")
            return self._create_fallback_understanding(query)
    
    def _is_simple_query(self, query: str) -> bool:
        """Check if query is simple enough for pattern matching"""
        query_lower = query.lower()
        
        # Simple patterns
        simple_patterns = [
            r"^find .+ for .+$",
            r"^search .+$",
            r"^what is .+\?$",
            r"^show me .+$"
        ]
        
        return any(re.match(pattern, query_lower) for pattern in simple_patterns)
    
    def _process_simple_query(self, query: str) -> Dict[str, Any]:
        """Process simple queries with pattern matching"""
        query_lower = query.lower()
        
        # Detect intent from keywords
        intent = "research_overview"  # Default
        
        if any(word in query_lower for word in ["find", "search", "show"]):
            intent = "component_search"
        elif any(word in query_lower for word in ["available", "stock", "price"]):
            intent = "supply_chain_check"
        elif any(word in query_lower for word in ["maturity", "trl", "ready"]):
            intent = "trl_query"
        
        # Extract entities
        entities = self._extract_entities_pattern(query)
        
        # Detect domains
        domains = self._detect_domains(query_lower)
        
        return {
            "intent": intent,
            "entities": entities,
            "domains": domains,
            "parameters": {
                "query": query,
                "max_results": 20
            },
            "confidence": 0.7,
            "method": "pattern_matching"
        }
    
    async def _ai_understand_query(self, query: str, context: str) -> Dict[str, Any]:
        """Use AI to understand complex queries"""
        
        system_prompt = f"""You are an expert EE research assistant. Analyze the user's query and extract:

1. Primary intent (one of: {', '.join(self.intents)})
2. Entities (components, technologies, part numbers, specifications)
3. Relevant EE domains (from: embedded_systems, power_management, emc_emi, analog, rf_wireless)
4. Key parameters (voltage ranges, current, power, frequency, etc.)
5. Regional preferences (EU, Asia, US, or none)

Respond ONLY with valid JSON in this format:
{{
  "intent": "component_search",
  "entities": {{
    "components": ["list of components"],
    "technologies": ["list of technologies"],
    "part_numbers": ["list of part numbers"],
    "specifications": {{"key": "value"}}
  }},
  "domains": ["list of domains"],
  "parameters": {{
    "voltage_range": "value",
    "current_max": "value",
    "other_params": "value"
  }},
  "regional_preference": "EU/Asia/US/none",
  "confidence": 0.95
}}"""

        user_prompt = f"Query: {query}"
        if context:
            user_prompt += f"\n\nContext: {context}"
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            understanding = json.loads(response.choices[0].message.content)
            understanding["method"] = "ai_processing"
            
            return understanding
        
        except Exception as e:
            logger.error(f"AI processing error: {str(e)}")
            return self._create_fallback_understanding(query)
    
    def _enhance_with_domain_knowledge(
        self,
        understanding: Dict[str, Any],
        query: str
    ) -> Dict[str, Any]:
        """Enhance AI understanding with domain-specific knowledge"""
        
        query_lower = query.lower()
        
        # Add missing domains based on keywords
        detected_domains = set(understanding.get("domains", []))
        for domain, keywords in self.domains.items():
            if any(kw in query_lower for kw in keywords):
                detected_domains.add(domain)
        
        understanding["domains"] = list(detected_domains)
        
        # Extract part numbers if missed
        part_numbers = understanding.get("entities", {}).get("part_numbers", [])
        additional_pns = self._extract_part_numbers(query)
        part_numbers.extend([pn for pn in additional_pns if pn not in part_numbers])
        
        if "entities" not in understanding:
            understanding["entities"] = {}
        understanding["entities"]["part_numbers"] = part_numbers
        
        # Add default parameters if missing
        if "parameters" not in understanding:
            understanding["parameters"] = {}
        
        understanding["parameters"]["query"] = query
        understanding["parameters"].setdefault("max_results", 20)
        understanding["parameters"].setdefault("regions", ["EU", "Asia"])
        
        return understanding
    
    def _generate_routing(self, understanding: Dict[str, Any]) -> Dict[str, bool]:
        """
        Generate provider routing decisions
        
        Returns which providers should be called
        """
        intent = understanding.get("intent", "research_overview")
        entities = understanding.get("entities", {})
        
        routing = {
            "paper_provider": False,
            "patent_provider": False,
            "component_provider": False,
            "nexar_provider": False,
            "trl_provider": False
        }
        
        # Route based on intent
        if intent == "component_search":
            routing["component_provider"] = True
            routing["nexar_provider"] = True
            routing["patent_provider"] = True  # Related patents
        
        elif intent == "research_overview":
            routing["paper_provider"] = True
            routing["patent_provider"] = True
            routing["trl_provider"] = True
        
        elif intent == "trl_query":
            routing["paper_provider"] = True
            routing["patent_provider"] = True
            routing["component_provider"] = True
            routing["trl_provider"] = True
        
        elif intent == "supply_chain_check":
            routing["nexar_provider"] = True
            routing["component_provider"] = True
        
        elif intent == "comparison":
            routing["paper_provider"] = True
            routing["component_provider"] = True
            routing["trl_provider"] = True
        
        else:  # Default: comprehensive search
            routing = {k: True for k in routing.keys()}
        
        # Always enable TRL if papers or patents are fetched
        if routing["paper_provider"] or routing["patent_provider"]:
            routing["trl_provider"] = True
        
        return routing
    
    def _detect_domains(self, query: str) -> List[str]:
        """Detect EE domains from query"""
        detected = []
        
        for domain, keywords in self.domains.items():
            if any(kw in query for kw in keywords):
                detected.append(domain)
        
        return detected if detected else ["general"]
    
    def _extract_entities_pattern(self, query: str) -> Dict[str, List[str]]:
        """Extract entities using patterns"""
        entities = {
            "components": [],
            "technologies": [],
            "part_numbers": []
        }
        
        # Extract part numbers
        entities["part_numbers"] = self._extract_part_numbers(query)
        
        # Extract technologies
        tech_keywords = ["gan", "sic", "silicon carbide", "gallium nitride", "cmos", "bicmos"]
        for tech in tech_keywords:
            if tech in query.lower():
                entities["technologies"].append(tech.upper())
        
        return entities
    
    def _extract_part_numbers(self, query: str) -> List[str]:
        """Extract part numbers from query"""
        # Common part number patterns
        patterns = [
            r'\b[A-Z]{2,}[\d]{3,}[A-Z]*\b',  # TPS54620, LM317
            r'\b[A-Z]\d{4,}\b',               # L7805
        ]
        
        part_numbers = []
        for pattern in patterns:
            matches = re.findall(pattern, query.upper())
            part_numbers.extend(matches)
        
        return list(set(part_numbers))
    
    def _create_fallback_understanding(self, query: str) -> Dict[str, Any]:
        """Create fallback understanding when processing fails"""
        return {
            "intent": "research_overview",
            "entities": {
                "components": [],
                "technologies": [],
                "part_numbers": self._extract_part_numbers(query)
            },
            "domains": self._detect_domains(query.lower()),
            "parameters": {
                "query": query,
                "max_results": 20,
                "regions": ["EU", "Asia"]
            },
            "routing": {
                "paper_provider": True,
                "patent_provider": True,
                "component_provider": True,
                "nexar_provider": False,
                "trl_provider": True
            },
            "confidence": 0.4,
            "method": "fallback"
        }
    
    def expand_query(self, query: str, domains: List[str]) -> List[str]:
        """
        Generate query variations for better search coverage
        
        Returns list of expanded queries
        """
        expansions = [query]
        
        # Add domain-specific terms
        for domain in domains:
            if domain == "power_management":
                expansions.append(f"{query} power supply")
                expansions.append(f"{query} voltage regulator")
            elif domain == "embedded_systems":
                expansions.append(f"{query} microcontroller")
                expansions.append(f"{query} embedded")
        
        return expansions[:3]  # Limit to 3 variations