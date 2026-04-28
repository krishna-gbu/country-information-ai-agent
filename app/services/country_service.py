from app.models.schema import NormalizedCountryData
from app.tools.rest_countries import fetch_country_by_name


class CountryService:
    async def lookup_by_name(self, country_name:str)->list[NormalizedCountryData]:
        return await fetch_country_by_name(country_name)
