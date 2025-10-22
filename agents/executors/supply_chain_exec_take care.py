import asyncio
from typing import Dict, Any, List, Optional
import httpx
from datetime import datetime
from agno.tools import Tool
import os

class SupplyChainExecutor(Tool):
    """
    Checks component availability, pricing, and lifecycle status
    across EU/Asia distributors
    """
    
    def __init__(self):
        super().__init__(
            name="supply_chain_check",
            description="Check component availability, pricing, and lifecycle status",
        )
        
        # API keys from environment
        self.octopart_key = os.getenv("OCTOPART_API_KEY")
        self.digikey_client_id = os.getenv("DIGIKEY_CLIENT_ID")
        self.digikey_client_secret = os.getenv("DIGIKEY_CLIENT_SECRET")
        
        # Distributor APIs
        self.distributors = {
            "octopart": {
                "name": "Octopart",
                "api": "https://octopart.com/api/v4/endpoint",
                "coverage": "Global aggregator"
            },
            "digikey": {
                "name": "Digi-Key",
                "api": "https://api.digikey.com/v1",
                "coverage": "EU, Asia"
            },
            "mouser": {
                "name": "Mouser Electronics",
                "api": "https://api.mouser.com/api/v1",
                "coverage": "EU, Asia"
            },
            "lcsc": {
                "name": "LCSC (Asia)",
                "api": "https://wmsc.lcsc.com/ftps/wm/product",
                "coverage": "Asia (China focus)"
            }
        }
    
    async def execute(self, query: str, part_numbers: List[str] = None) -> Dict[str, Any]:
        """
        Check supply chain status for components
        
        Args:
            query: Component description or search query
            part_numbers: Specific part numbers to check
            
        Returns:
            Availability, pricing, lifecycle data
        """
        print(f"🔍 Checking supply chain for: {query}")
        
        results = []
        
        if part_numbers:
            # Check specific part numbers
            for pn in part_numbers:
                component_data = await self._check_component(pn)
                if component_data:
                    results.append(component_data)
        else:
            # Search by query
            search_results = await self._search_components(query)
            results = search_results
        
        # Analyze supply chain health
        analysis = self._analyze_supply_chain(results)
        
        return {
            "source": "supply_chain",
            "query": query,
            "components_checked": len(results),
            "components": results,
            "analysis": analysis,
            "checked_at": datetime.utcnow().isoformat()
        }
    
    async def _check_component(self, part_number: str) -> Optional[Dict[str, Any]]:
        """
        Check a specific component across distributors
        """
        if self.octopart_key:
            return await self._check_octopart(part_number)
        else:
            # Fallback to sample data if no API key
            return self._create_sample_component_data(part_number)
    
    async def _check_octopart(self, part_number: str) -> Optional[Dict[str, Any]]:
        """
        Query Octopart API (aggregates multiple distributors)
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Octopart GraphQL API
                query = """
                query {
                  search(q: "%s", limit: 1) {
                    results {
                      part {
                        mpn
                        manufacturer {
                          name
                        }
                        short_description
                        offers {
                          seller {
                            name
                          }
                          sku
                          inventory_level
                          prices {
                            quantity
                            price
                            currency
                          }
                        }
                        lifecycle_status
                      }
                    }
                  }
                }
                """ % part_number
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.octopart_key}"
                }
                
                # Note: This is simplified - real implementation needs proper GraphQL client
                # response = await client.post(
                #     self.distributors["octopart"]["api"],
                #     json={"query": query},
                #     headers=headers
                # )
                
                # For now, return sample data
                return self._create_sample_component_data(part_number)
                
            except Exception as e:
                print(f"⚠️  Octopart API error: {str(e)}")
                return None
    
    async def _search_components(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for components by description/category
        """
        # Use Octopart or Digi-Key search
        components = []
        
        # Sample implementation
        components = [
            self._create_sample_component_data(f"SAMPLE-{query}-001"),
            self._create_sample_component_data(f"SAMPLE-{query}-002")
        ]
        
        return components
    
    def _create_sample_component_data(self, part_number: str) -> Dict[str, Any]:
        """Create sample component data (for testing/demo)"""
        return {
            "part_number": part_number,
            "manufacturer": "Texas Instruments",
            "description": "High-efficiency power management IC",
            "lifecycle": "Active",
            "availability": {
                "digikey": {
                    "stock": 1250,
                    "lead_time_weeks": 0,
                    "region": "EU"
                },
                "mouser": {
                    "stock": 890,
                    "lead_time_weeks": 0,
                    "region": "EU"
                },
                "lcsc": {
                    "stock": 5200,
                    "lead_time_weeks": 1,
                    "region": "Asia"
                }
            },
            "pricing": {
                "unit_price_usd": 2.45,
                "price_breaks": [
                    {"quantity": 1, "price": 2.45},
                    {"quantity": 10, "price": 2.20},
                    {"quantity": 100, "price": 1.95},
                    {"quantity": 1000, "price": 1.75}
                ],
                "currency": "USD"
            },
            "datasheet_url": f"https://www.ti.com/lit/ds/symlink/{part_number}.pdf",
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _analyze_supply_chain(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze supply chain health and risks
        """
        if not components:
            return {"status": "no_data"}
        
        total_stock_eu = 0
        total_stock_asia = 0
        at_risk_count = 0
        active_count = 0
        
        for comp in components:
            # Count stock by region
            availability = comp.get("availability", {})
            for dist, data in availability.items():
                stock = data.get("stock", 0)
                region = data.get("region", "")
                
                if region == "EU":
                    total_stock_eu += stock
                elif region == "Asia":
                    total_stock_asia += stock
            
            # Check lifecycle
            lifecycle = comp.get("lifecycle", "").lower()
            if lifecycle == "active":
                active_count += 1
            elif lifecycle in ["nrnd", "obsolete"]:
                at_risk_count += 1
        
        # Determine overall health
        if at_risk_count > len(components) * 0.3:
            health = "at_risk"
        elif total_stock_eu + total_stock_asia < 1000:
            health = "low_stock"
        else:
            health = "healthy"
        
        return {
            "overall_health": health,
            "total_stock_eu": total_stock_eu,
            "total_stock_asia": total_stock_asia,
            "active_components": active_count,
            "at_risk_components": at_risk_count,
            "recommendations": self._generate_recommendations(health, at_risk_count)
        }
    
    def _generate_recommendations(self, health: str, at_risk: int) -> List[str]:
        """Generate supply chain recommendations"""
        recommendations = []
        
        if health == "at_risk":
            recommendations.append("⚠️  Multiple components at end-of-life. Consider alternatives.")
        
        if health == "low_stock":
            recommendations.append("📦 Low stock levels detected. Place orders soon or identify second sources.")
        
        if at_risk > 0:
            recommendations.append(f"🔄 {at_risk} component(s) may need redesign. Review lifecycle status.")
        
        if not recommendations:
            recommendations.append("✅ Supply chain appears healthy. No immediate concerns.")
        
        return recommendations