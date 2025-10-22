from typing import Dict, Any, List

def filter_by_region(
    component_data: Dict[str, Any],
    target_regions: List[str]
) -> Dict[str, Any]:
    """
    Filter component data by target regions
    
    Args:
        component_data: Component information
        target_regions: List of target regions (e.g., ["EU", "Asia"])
        
    Returns:
        Filtered component data with regional info
    """
    result = component_data.copy()
    result["target_regions"] = target_regions
    result["regions"] = []
    
    # Check manufacturer region
    manufacturer = component_data.get("manufacturer", "").lower()
    mfr_region = _get_manufacturer_region(manufacturer)
    if mfr_region:
        result["manufacturer_region"] = mfr_region
        if mfr_region in target_regions:
            result["regions"].append(mfr_region)
    
    # Check supply chain availability by region
    sc_data = component_data.get("supply_chain", {})
    for distributor, data in sc_data.items():
        dist_region = data.get("region", "")
        if dist_region in target_regions and dist_region not in result["regions"]:
            result["regions"].append(dist_region)
    
    # Check if component meets regional requirements
    result["meets_regional_requirements"] = len(result["regions"]) > 0
    
    return result

def _get_manufacturer_region(manufacturer: str) -> str:
    """Map manufacturer to primary region"""
    eu_manufacturers = [
        "infineon", "stmicroelectronics", "st", "nxp", "philips"
    ]
    
    asia_manufacturers = [
        "renesas", "rohm", "toshiba", "panasonic", "sony",
        "samsung", "hynix", "mediatek", "hisilicon"
    ]
    
    us_manufacturers = [
        "texas instruments", "ti", "analog devices", "adi",
        "microchip", "on semiconductor", "maxim", "intel"
    ]
    
    mfr_lower = manufacturer.lower()
    
    if any(m in mfr_lower for m in eu_manufacturers):
        return "EU"
    elif any(m in mfr_lower for m in asia_manufacturers):
        return "Asia"
    elif any(m in mfr_lower for m in us_manufacturers):
        return "US"
    
    return "Unknown"

def get_regional_distributors(region: str) -> List[str]:
    """Get list of distributors for a region"""
    distributors = {
        "EU": ["Digi-Key", "Mouser", "Farnell", "RS Components"],
        "Asia": ["LCSC", "Digi-Key", "Mouser", "Arrow Asia"],
        "US": ["Digi-Key", "Mouser", "Arrow", "Avnet"]
    }
    
    return distributors.get(region, [])

def check_regional_compliance(component: Dict[str, Any], region: str) -> Dict[str, Any]:
    """Check if component meets regional compliance requirements"""
    compliance = {
        "region": region,
        "compliant": True,
        "requirements": [],
        "status": {}
    }
    
    if region == "EU":
        compliance["requirements"] = ["CE", "RoHS", "REACH"]
        # Check if component mentions compliance
        # (In production, check against actual databases)
        compliance["status"]["CE"] = "Unknown"
        compliance["status"]["RoHS"] = "Unknown"
        compliance["status"]["REACH"] = "Unknown"
    
    elif region == "Asia":
        compliance["requirements"] = ["CCC (China)", "PSE (Japan)", "KC (Korea)"]
        compliance["status"]["CCC"] = "Unknown"
        compliance["status"]["PSE"] = "Unknown"
        compliance["status"]["KC"] = "Unknown"
    
    return compliance