import asyncio
from typing import Dict, Any, List, Optional
from agno.tools import Tool
import httpx

from tools.datasheet_parser import parse_datasheet
from tools.regional_filter import filter_by_region

class ComponentExecutor(Tool):
    """
    Comprehensive component information executor
    Aggregates data from multiple sources into unified component profile
    """
    
    def __init__(self):
        super().__init__(
            name="component_info",
            description="Get comprehensive component information including specs, apps, alternatives",
        )
        
        # Component databases
        self.databases = {
            "ti": "https://www.ti.com/product",
            "infineon": "https://www.infineon.com/cms/en/product",
            "st": "https://www.st.com/en/products",
            "renesas": "https://www.renesas.com/products",
            "rohm": "https://www.rohm.com/products"
        }
    
    async def execute(
        self,
        part_number: str = None,
        category: str = None,
        specifications: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive component information
        
        Args:
            part_number: Specific part number (e.g., "TPS54620")
            category: Component category (e.g., "Buck Converter")
            specifications: Required specs (e.g., {"vin_max": 60, "iout_max": 6})
            
        Returns:
            Complete component profile with alternatives
        """
        if part_number:
            return await self._get_component_by_part_number(part_number)
        elif category and specifications:
            return await self._search_by_specs(category, specifications)
        else:
            return {"error": "Must provide either part_number or (category + specifications)"}
    
    async def _get_component_by_part_number(self, part_number: str) -> Dict[str, Any]:
        """
        Get detailed info for specific part number
        """
        print(f"🔍 Fetching component info for: {part_number}")
        
        # Parse datasheet
        datasheet_data = await self._fetch_and_parse_datasheet(part_number)
        
        # Get application notes
        app_notes = await self._fetch_application_notes(part_number)
        
        # Find alternatives
        alternatives = await self._find_alternatives(datasheet_data)
        
        # Check regional availability
        regional_data = filter_by_region(datasheet_data, ["EU", "Asia"])
        
        return {
            "part_number": part_number,
            "manufacturer": datasheet_data.get("manufacturer", "Unknown"),
            "category": datasheet_data.get("category"),
            "specifications": datasheet_data.get("specs", {}),
            "features": datasheet_data.get("features", []),
            "applications": datasheet_data.get("typical_applications", []),
            "package_types": datasheet_data.get("packages", []),
            "datasheet_url": datasheet_data.get("datasheet_url"),
            "application_notes": app_notes,
            "alternatives": alternatives,
            "regional_availability": regional_data.get("regions", []),
            "design_resources": {
                "reference_designs": datasheet_data.get("reference_designs", []),
                "spice_models": datasheet_data.get("spice_model_url"),
                "eval_boards": datasheet_data.get("eval_boards", [])
            }
        }
    
    async def _fetch_and_parse_datasheet(self, part_number: str) -> Dict[str, Any]:
        """
        Fetch and parse component datasheet
        """
        # Try to find datasheet URL
        datasheet_url = await self._find_datasheet_url(part_number)
        
        if datasheet_url:
            # Parse datasheet using tool
            parsed = await parse_datasheet(datasheet_url)
            return parsed
        else:
            # Return sample data if datasheet not found
            return self._create_sample_component_profile(part_number)
    
    async def _find_datasheet_url(self, part_number: str) -> Optional[str]:
        """
        Search for datasheet URL across manufacturer sites
        """
        # Try common patterns
        manufacturers = ["ti", "infineon", "st", "renesas", "rohm"]
        
        for mfr in manufacturers:
            # Construct likely URL
            if mfr == "ti":
                url = f"https://www.ti.com/lit/ds/symlink/{part_number.lower()}.pdf"
            elif mfr == "infineon":
                url = f"https://www.infineon.com/dgdl/Infineon-{part_number}-DataSheet-v01_00-EN.pdf"
            # Add more patterns...
            
            # Check if URL exists
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.head(url, timeout=5.0)
                    if response.status_code == 200:
                        return url
                except:
                    continue
        
        return None
    
    async def _fetch_application_notes(self, part_number: str) -> List[Dict[str, Any]]:
        """
        Fetch related application notes
        """
        # Search manufacturer sites for app notes
        # This would require web scraping or API access
        
        # Sample data
        return [
            {
                "title": f"Design Guide for {part_number}",
                "document_number": "SLUA123",
                "url": f"https://www.ti.com/lit/an/slua123/slua123.pdf"
            }
        ]
    
    async def _find_alternatives(self, component_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find alternative components with similar specs
        """
        # Use specifications to find alternatives
        # In production, query component databases
        
        category = component_data.get("category", "")
        
        # Sample alternatives
        alternatives = [
            {
                "part_number": "ALTERNATIVE-001",
                "manufacturer": "Infineon",
                "similarity_score": 0.95,
                "key_differences": ["Higher efficiency", "Smaller package"]
            },
            {
                "part_number": "ALTERNATIVE-002",
                "manufacturer": "STMicroelectronics",
                "similarity_score": 0.88,
                "key_differences": ["Lower cost", "Wider input voltage range"]
            }
        ]
        
        return alternatives
    
    async def _search_by_specs(
        self,
        category: str,
        specifications: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Search for components matching specifications
        """
        print(f"🔍 Searching {category} with specs: {specifications}")
        
        # Query parametric search engines
        # This would interface with distributor parametric search
        
        matching_components = [
            self._create_sample_component_profile("MATCH-001"),
            self._create_sample_component_profile("MATCH-002")
        ]
        
        return {
            "category": category,
            "search_criteria": specifications,
            "matches_found": len(matching_components),
            "components": matching_components
        }
    
    def _create_sample_component_profile(self, part_number: str) -> Dict[str, Any]:
        """Create sample component profile for testing"""
        return {
            "part_number": part_number,
            "manufacturer": "Texas Instruments",
            "category": "Buck Converter",
            "specs": {
                "vin_min": 4.5,
                "vin_max": 60,
                "vout_min": 0.8,
                "vout_max": 58,
                "iout_max": 6.0,
                "efficiency": 95,
                "fsw_khz": 500,
                "package": "VQFN-20"
            },
            "features": [
                "High efficiency at light load",
                "Wide input voltage range",
                "Integrated MOSFETs",
                "Adjustable switching frequency"
            ],
            "typical_applications": [
                "Industrial power supplies",
                "Automotive electronics",
                "Telecom equipment"
            ],
            "packages": ["VQFN-20", "HTSSOP-20"],
            "datasheet_url": f"https://www.ti.com/lit/ds/symlink/{part_number}.pdf",
            "reference_designs": [
                "48V to 12V, 6A Reference Design"
            ],
            "spice_model_url": f"https://www.ti.com/lit/zip/{part_number}",
            "eval_boards": [
                f"{part_number}EVM"
            ]
        }