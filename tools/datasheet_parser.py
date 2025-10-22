import io
from typing import Dict, Any, Optional
import PyPDF2
import pdfplumber
import re
import httpx

async def parse_datasheet(pdf_url: str) -> Dict[str, Any]:
    """
    Parse PDF datasheet and extract key information
    
    Args:
        pdf_url: URL to PDF datasheet
        
    Returns:
        Extracted specifications and metadata
    """
    try:
        # Download PDF
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(pdf_url)
            pdf_bytes = response.content
        
        # Parse with pdfplumber (better for tables)
        parsed_data = _parse_with_pdfplumber(pdf_bytes)
        
        # Extract key sections
        parsed_data["datasheet_url"] = pdf_url
        
        return parsed_data
    
    except Exception as e:
        print(f"⚠️  Error parsing datasheet {pdf_url}: {str(e)}")
        return {
            "error": str(e),
            "datasheet_url": pdf_url
        }

def _parse_with_pdfplumber(pdf_bytes: bytes) -> Dict[str, Any]:
    """Parse PDF using pdfplumber for better table extraction"""
    result = {
        "part_number": None,
        "manufacturer": None,
        "category": None,
        "specs": {},
        "features": [],
        "typical_applications": [],
        "packages": [],
        "region": None
    }
    
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            # Get first page text for metadata
            if pdf.pages:
                first_page_text = pdf.pages[0].extract_text()
                
                # Extract part number (usually at top)
                result["part_number"] = _extract_part_number(first_page_text)
                result["manufacturer"] = _extract_manufacturer(first_page_text)
                result["category"] = _extract_category(first_page_text)
                
                # Extract tables (specifications)
                for page in pdf.pages[:5]:  # Check first 5 pages
                    tables = page.extract_tables()
                    for table in tables:
                        specs = _parse_spec_table(table)
                        result["specs"].update(specs)
                
                # Extract features
                all_text = "\n".join(page.extract_text() for page in pdf.pages[:3])
                result["features"] = _extract_features(all_text)
                result["typical_applications"] = _extract_applications(all_text)
                result["packages"] = _extract_packages(all_text)
    
    except Exception as e:
        result["parse_error"] = str(e)
    
    return result

def _extract_part_number(text: str) -> Optional[str]:
    """Extract part number from text"""
    # Common patterns: ALPHANUMERIC, dashes, underscores
    patterns = [
        r'\b([A-Z]{2,}[\d\w\-]{3,15})\b',
        r'\bP/N[:\s]+([A-Z0-9\-]{4,})\b',
        r'\bPart Number[:\s]+([A-Z0-9\-]{4,})\b'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def _extract_manufacturer(text: str) -> Optional[str]:
    """Extract manufacturer name"""
    manufacturers = [
        "Texas Instruments", "TI", "Infineon", "STMicroelectronics", "ST",
        "Renesas", "Rohm", "Analog Devices", "ADI", "Microchip",
        "NXP", "ON Semiconductor", "Maxim"
    ]
    
    text_upper = text.upper()
    for mfr in manufacturers:
        if mfr.upper() in text_upper:
            return mfr
    
    return None

def _extract_category(text: str) -> Optional[str]:
    """Extract component category"""
    categories = {
        "Buck Converter": ["buck converter", "step-down", "buck regulator"],
        "Boost Converter": ["boost converter", "step-up", "boost regulator"],
        "LDO": ["ldo", "low dropout", "linear regulator"],
        "PMIC": ["pmic", "power management"],
        "MCU": ["microcontroller", "mcu"],
        "ADC": ["analog-to-digital", "adc"],
        "DAC": ["digital-to-analog", "dac"],
        "Op-Amp": ["operational amplifier", "op-amp", "opamp"]
    }
    
    text_lower = text.lower()
    for category, keywords in categories.items():
        if any(kw in text_lower for kw in keywords):
            return category
    
    return None

def _parse_spec_table(table: list) -> Dict[str, Any]:
    """Parse specification table"""
    specs = {}
    
    if not table or len(table) < 2:
        return specs
    
    # Assume first row is header
    for row in table[1:]:
        if len(row) >= 2:
            param = str(row[0]).strip() if row[0] else ""
            value = str(row[1]).strip() if row[1] else ""
            
            if param and value:
                # Clean and store
                param_key = param.lower().replace(" ", "_")
                specs[param_key] = value
    
    return specs

def _extract_features(text: str) -> list:
    """Extract features list"""
    features = []
    
    # Look for "Features" section
    features_match = re.search(
        r'Features?[:\n]+((?:[-•]\s*.+\n?)+)',
        text,
        re.IGNORECASE | re.MULTILINE
    )
    
    if features_match:
        features_text = features_match.group(1)
        # Extract bullet points
        bullets = re.findall(r'[-•]\s*(.+)', features_text)
        features = [b.strip() for b in bullets if len(b.strip()) > 10]
    
    return features[:10]  # Limit to top 10

def _extract_applications(text: str) -> list:
    """Extract typical applications"""
    applications = []
    
    app_match = re.search(
        r'(?:Typical\s+)?Applications?[:\n]+((?:[-•]\s*.+\n?)+)',
        text,
        re.IGNORECASE | re.MULTILINE
    )
    
    if app_match:
        app_text = app_match.group(1)
        bullets = re.findall(r'[-•]\s*(.+)', app_text)
        applications = [b.strip() for b in bullets if len(b.strip()) > 5]
    
    return applications[:10]

def _extract_packages(text: str) -> list:
    """Extract package types"""
    package_patterns = [
        r'\b(TSSOP-\d+)\b',
        r'\b(SOIC-\d+)\b',
        r'\b(QFN-\d+)\b',
        r'\b(VQFN-\d+)\b',
        r'\b(DIP-\d+)\b',
        r'\b(HTSSOP-\d+)\b'
    ]
    
    packages = []
    for pattern in package_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        packages.extend(matches)
    
    return list(set(packages))  # Remove duplicates