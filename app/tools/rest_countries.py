import httpx
from urllib.parse import quote

from app.models.schema import NormalizedCountryData

async def fetch_country_by_name(country_name:str)->list[NormalizedCountryData]:
      url = f"https://restcountries.com/v3.1/name/{quote(country_name)}" 

      async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
      
      if response.status_code == 404:
        return []


      response.raise_for_status()
      data = response.json()
      
      countries = [] 
      for item in data:
        country = NormalizedCountryData(
            common_name=item.get("name", {}).get("common", ""),
            official_name=item.get("name", {}).get("official"),
            capital=item.get("capital"),
            population=item.get("population"),
            currencies=[
                currency.get("name")
                for currency in item.get("currencies", {}).values()
                if currency.get("name")
            ]
            or None,
            languages=list(item.get("languages", {}).values()) or None,
            region=item.get("region"),
            subregion=item.get("subregion"),
        )
        countries.append(country)

      return countries

    


      
     
    
