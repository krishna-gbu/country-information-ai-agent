from pydantic import BaseModel, Field


class ErrorInfo(BaseModel):
    code: str = Field(...,description="Machine-readable error code")
    message: str = Field(...,description="Human-readable error message")

class AskRequest(BaseModel):
    question:str=Field(
        ...,
        min_length=1,
        max_length=500,
        description="User question about a country"
        )

class AskResponse(BaseModel):
    answer:str = Field(
        ...,
        description="Final response text for the user"
    )
    country: str|None = Field(
        default=None,
        description="Resolved country name"
    )
    requested_fields: list[str] = Field(
        default_factory=list,
        description="Normalized fields requested by the user"
    )
    grounded:bool = Field(
        ...,
        description="whether the answer is grounded in tool data"
    )
    source : str = Field(
        default="restcountries",
        description="Source of the factual data"
    )
    error: ErrorInfo| None = Field(
        default=None,
        description="Structured error details if something goes wrong"
    ) 

class  ExtractedIntent(BaseModel):
     country_name:str|None = Field(
        default=None,
        description="Country name extracted from the user question"
     )
     requested_fields : list[str]= Field(
        default_factory=list,
        description="Normalized fields requested by the user"
     )
     supported:bool= Field(
        ...,
        description="Whether the question is supported by this service"
        )
     reason_if_unsupported: str | None = Field(
        default=None,
        description="Reason why the question is unsupported",
    )

class NormalizedCountryData(BaseModel):
    common_name: str = Field(
        ...,
        description="Common country name",
    )
    official_name: str | None = Field(
        default=None,
        description="Official country name",
    )
    capital: list[str] | None = Field(
        default=None,
        description="Capital city names",
    )
    population: int | None = Field(
        default=None,
        description="Country population",
    )
    currencies: list[str] | None = Field(
        default=None,
        description="Currency names or codes",
    )
    languages: list[str] | None = Field(
        default=None,
        description="Languages spoken in the country",
    )
    region: str | None = Field(
        default=None,
        description="Geographic region",
    )
    subregion: str | None = Field(
        default=None,
        description="Geographic subregion",
    )
