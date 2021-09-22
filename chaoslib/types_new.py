from typing import Any, Dict, List, Literal, NamedTuple, Optional, Pattern, Union

from pydantic import BaseModel as PydanticBaseModel
from pydantic import validator
from pydantic.fields import Field
from pydantic.main import Extra
from pydantic.networks import HttpUrl


class BaseModel(PydanticBaseModel):
    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True


class ControlProvider(BaseModel):
    type: Literal["python"]
    module: str


class Control(BaseModel):
    name: str
    provider: ControlProvider
    scope: Optional[Literal["before", "after"]]
    automatic: Optional[bool] = True


class PythonProvider(BaseModel):
    type: Literal["python"]
    module: str
    func: str
    arguments: Optional[Dict[str, Any]]


class Timeout(NamedTuple):
    connection_timeout: Union[float, int]
    request_timeout: Union[float, int]


class HttpProvider(BaseModel):
    type: Literal["http"]
    url: HttpUrl
    method: Optional[
        Literal["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE"]
    ] = "GET"
    headers: Optional[Dict[str, str]]
    expected_status: Optional[int]
    arguments: Optional[Dict[str, Any]]
    timeout: Optional[Union[Union[float, int], Timeout]]


class ProcessProvider(BaseModel):
    type: Literal["process"]
    path: str
    arguments: Optional[List[str]]
    timeout: Optional[Union[float, int]]


class Probe(BaseModel):
    type: Literal["probe"]
    name: str
    provider: Union[HttpProvider, ProcessProvider, PythonProvider]
    secret: Optional[str]
    configuration: Optional[str]
    background: Optional[bool]
    controls: Optional[List[Control]]
    ref: Optional[str]


class PausesBefore(BaseModel):
    before: int


class PausesAfter(BaseModel):
    after: int


class PausesBoth(PausesAfter, PausesBefore):
    pass


class Action(BaseModel):
    type: Literal["action"]
    name: str
    provider: Union[HttpProvider, ProcessProvider, PythonProvider]
    controls: List[Control]
    secret: Optional[str]
    configuration: Optional[str]
    background: Optional[bool]
    pauses: Optional[Union[PausesAfter, PausesBefore, PausesBoth]]
    ref: Optional[str]


Activity = Union[Probe, Action]


class RegexTolerance(BaseModel):
    type: Literal["regex"]
    pattern: Pattern  # type: ignore[type-arg]
    target: Optional[str]


class JsonPathTolerance(BaseModel):
    type: Literal["jsonpath"]
    path: str
    expect: Optional[int]


class Range(NamedTuple):
    lower_bound: Union[float, int]
    upper_bound: Union[float, int]


class RangeTolerance(BaseModel):
    type: Literal["range"]
    range: Range

    @validator("range")
    def validate_range(cls, val: Range) -> Range:
        if val.lower_bound > val.upper_bound:
            raise ValueError(
                "Range first entry must be lower bound,"
                f" {val.lower_bound} is greater than {val.upper_bound}"
            )
        return val


class SteadyStateHypothesisProbe(Probe):
    tolerance: Union[
        str,
        int,
        bool,
        List[str],
        List[int],
        List[bool],
        Probe,
        RegexTolerance,
        JsonPathTolerance,
        RangeTolerance,
    ]


class SteadyStateHypothesis(BaseModel):
    title: str
    probes: List[SteadyStateHypothesisProbe]
    controls: Optional[List[Control]]


class Extension(BaseModel):
    name: str


class Experiment(BaseModel):
    title: str
    description: str
    method: List[Activity]
    steady_state_hypothesis: Optional[SteadyStateHypothesis] = Field(
        alias="steady-state-hypothesis"
    )
    rollbacks: Optional[List[Action]]
    tags: Optional[List[str]]
    secrets: Optional[Union[Dict[str, str], Dict[str, Dict[str, Any]]]]
    extensions: Optional[List[Extension]]
    contributions: Optional[Dict[str, Union[Literal["high", "medium", "low", "none"]]]]
    controls: Optional[List[Control]]
