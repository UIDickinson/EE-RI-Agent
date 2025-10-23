from typing import Dict, Any, List, Optional
import logging
from .base_provider import BaseProvider
import os

logger = logging.getLogger(__name__)

class NexarProvider(BaseProvider):
    """
    Supply chain provider using Nexar API
    
    Provides:
    - Component availability
    - Pricing information
    - Distributor stock levels
    - Lifecycle status
    """
    
    def __init__(self):
        super().__init__("NexarProvider")
        
        self.client_id = os.getenv("NEXAR_CLIENT_ID")
        self.client_secret = os.getenv("NEXAR_CLIENT_SECRET")
        
        self.token_url = "https://identity.nexar.com/connect/token"
        self.api_url = "https://api.nexar.com/graphql"
        
        self.access_token = None
        self.use_mock = not (self.client_id and self.client_secret)
        
        if self.use_mock:
            logger.warning("Nexar credentials not found - using mock data")
    
    async def fetch(
        self,
        part_numbers: List[str] = None,
        query: str = None
    ) -> Dict[str, Any]:
        """
        Fetch supply chain information
        
        Args:
            part_numbers: List of part numbers to check
            query: Search query
        """
        try:
            if self.use_mock:
                components = self._create_mock_supply_data(part_numbers or [query])
            else:
                components = await self._fetch_nexar_data(part_numbers or [query])
            
            # Analyze supply chain health
            analysis = self._analyze_supply_chain(components)
            
            return self._create_response(
                success=True,
                data={
                    "components": components,
                    "count": len(components),
                    "analysis": analysis,
                    "mock_data": self.use_mock
                },
                metadata={
                    "part_numbers": part_numbers,
                    "query": query
                }
            )
        
        except Exception as e:
            logger.error(f"Supply chain fetch error: {str(e)}")
            return self._create_response(
                success=False,
                error=str(e)
            )
    
    async def _get_token(self) -> Optional[str]:
        """Get OAuth2 access token from Nexar"""
        if self.access_token:
            return self.access_token
        
        try:
            response = await self._make_request(
                self.token_url,
                method="POST",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "supply.domain"
                }
            )
            
            data = response.json()
            self.access_token = data.get("access_token")
            return self.access_token
        
        except Exception as e:
            logger.error(f"Nexar auth error: {str(e)}")
            return None
    
    async def _fetch_nexar_data(self, part_numbers: List[str]) -> List[Dict[str, Any]]:
        """Fetch data from Nexar API"""
        token = await self._get_token()
        if not token:
            return self._create_mock_supply_data(part_numbers)
        
        # Nexar GraphQL query
        query = """
        query SearchParts($q: String!) {
          supSearchMpn(q: $q, limit: 10) {
            results {
              part {
                mpn
                manufacturer { name }
                shortDescription
                sellers {
                  company { name }
                  offers {
                    inventoryLevel
                    prices {
                      quantity
                      price
                      currency
                    }
                  }
                }
              }
            }
          }
        }
        """
        
        components = []
        for pn in part_numbers:
            try:
                response = await self._make_request(
                    self.api_url,
                    method="POST",
                    json={
                        "query": query,
                        "variables": {"q": pn}
                    },
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                data = response.json()
                parsed = self._parse_nexar_response(data, pn)
                if parsed:
                    components.append(parsed)
            
            except Exception as e:
                logger.error(f"Error fetching {pn}: {str(e)}")
        
        return components
    
    def _parse_nexar_response(self, data: Dict[str, Any], part_number: str) -> Optional[Dict[str, Any]]:
        """Parse Nexar GraphQL response"""
        try:
            results = data.get("data", {}).get("supSearchMpn", {}).get("results", [])
            
            if not results:
                return None
            
            part = results[0].get("part", {})
            
            # Parse availability
            availability = {}
            for seller in part.get("sellers", []):
                seller_name = seller.get("company", {}).get("name", "Unknown")
                offers = seller.get("offers", [])
                
                if offers:
                    availability[seller_name] = {
                        "stock": offers[0].get("inventoryLevel", 0),
                        "lead_time_weeks": 0,
                        "region": self._guess_region(seller_name)
                    }
            
            # Parse pricing
            pricing = {"unit_price_usd": 0, "price_breaks": []}
            if part.get("sellers") and part["sellers"][0].get("offers"):
                prices = part["sellers"][0]["offers"][0].get("prices", [])
                if prices:
                    pricing["unit_price_usd"] = prices[0].get("price", 0)
                    pricing["price_breaks"] = [
                        {"quantity": p.get("quantity"), "price": p.get("price")}
                        for p in prices
                    ]
            
            return {
                "part_number": part.get("mpn", part_number),
                "manufacturer": part.get("manufacturer", {}).get("name", "Unknown"),
                "description": part.get("shortDescription", ""),
                "lifecycle": "Active",
                "availability": availability,
                "pricing": pricing
            }
        
        except Exception as e:
            logger.error(f"Parse error: {str(e)}")
            return None
    
    def _guess_region(self, seller: str) -> str:
        """Guess region from seller name"""
        seller_lower = seller.lower()
        
        if "digi-key" in seller_lower or "mouser" in seller_lower:
            return "EU"
        elif "lcsc" in seller_lower:
            return "Asia"
        else:
            return "Global"
    
    def _create_mock_supply_data(self, identifiers: List[str]) -> List[Dict[str, Any]]:
        """Create mock supply chain data"""
        components = []
        
        for i, identifier in enumerate(identifiers[:10]):
            component = {
                "part_number": identifier if identifier.isupper() else f"MOCK{1000+i}",
                "manufacturer": ["Texas Instruments", "Infineon", "Rohm"][i % 3],
                "description": f"Mock component for {identifier}",
                "lifecycle": "Active",
                "availability": {
                    "Digi-Key": {"stock": 1250 + i*100, "lead_time_weeks": 0, "region": "EU"},
                    "Mouser": {"stock": 890 + i*80, "lead_time_weeks": 0, "region": "EU"},
                    "LCSC": {"stock": 5200 + i*200, "lead_time_weeks": 1, "region": "Asia"}
                },
                "pricing": {
                    "unit_price_usd": 2.45 + i*0.5,
                    "price_breaks": [
                        {"quantity": 1, "price": 2.45 + i*0.5},
                        {"quantity": 10, "price": 2.20 + i*0.4},
                        {"quantity": 100, "price": 1.95 + i*0.3}
                    ]
                }
            }
            components.append(component)
        
        return components
    
    def _analyze_supply_chain(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze supply chain health"""
        if not components:
            return {"status": "no_data"}
        
        total_stock = 0
        eu_stock = 0
        asia_stock = 0
        active_count = 0
        
        for comp in components:
            availability = comp.get("availability", {})
            for dist, data in availability.items():
                stock = data.get("stock", 0)
                total_stock += stock
                
                region = data.get("region", "")
                if region == "EU":
                    eu_stock += stock
                elif region == "Asia":
                    asia_stock += stock
            
            if comp.get("lifecycle") == "Active":
                active_count += 1
        
        health = "healthy" if total_stock > 1000 else "low_stock"
        
        return {
            "overall_health": health,
            "total_stock": total_stock,
            "eu_stock": eu_stock,
            "asia_stock": asia_stock,
            "active_components": active_count,
            "at_risk_components": len(components) - active_count,
            "recommendations": self._generate_recommendations(health)
        }
    
    def _generate_recommendations(self, health: str) -> List[str]:
        """Generate recommendations"""
        if health == "low_stock":
            return [
                "⚠️  Low stock levels detected",
                "Consider placing orders soon",
                "Identify second sources"
            ]
        else:
            return ["✅ Supply chain appears healthy"]
    
    def validate_response(self, response: Any) -> bool:
        """Validate supply chain response"""
        if not isinstance(response, dict):
            return False
        return "components" in response.get("data", {})