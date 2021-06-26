#!/usr/bin/env python
"""Implement the Rock class and other core rocks functionality."""
from datetime import datetime
from typing import List, Optional, Union

import numpy as np
import pandas as pd
import pydantic
import rich
from tqdm import tqdm

import rocks


# ------
# Validators
def ensure_list(value):
    """Ensure that parameters are always a list.
    Some parameters are a dict if it's a single reference and a list otherwise.

    Further replaces all None values by empty dictionaries.
    """
    if isinstance(value, dict):
        value = [value]

    for i, v in enumerate(value):
        if v is None:
            value[i] = {}
    return value


# ------
# ssoCard as pydantic model

# The lowest level in the ssoCard tree is the Parameter
class Error(pydantic.BaseModel):
    min_: Optional[float] = pydantic.Field(np.nan, alias="min")
    max_: Optional[float] = pydantic.Field(np.nan, alias="max")


class Parameter(pydantic.BaseModel):
    error: Error = Error(**{})
    value: Union[int, float, None] = None


# Other common branches are method and bibref
class Method(pydantic.BaseModel):
    doi: Optional[str] = ""
    name: Optional[str] = ""
    year: Optional[int] = None
    title: Optional[str] = ""
    bibcode: Optional[str] = ""
    shortbib: Optional[str] = ""


class Bibref(pydantic.BaseModel):
    doi: Optional[str] = ""
    year: Optional[int] = None
    title: Optional[str] = ""
    bibcode: Optional[str] = ""
    shortbib: Optional[str] = ""


class OrbitalElements(pydantic.BaseModel):
    ceu: Optional[float] = np.nan
    author: Optional[str] = ""
    bibref: List[Bibref] = [Bibref(**{})]
    err_ceu: MinMax = MinMax(**{})
    ceu_rate: Optional[float] = np.nan
    ref_epoch: Optional[float] = np.nan
    inclination: Optional[float] = np.nan
    mean_motion: Optional[float] = np.nan
    orbital_arc: Optional[int] = None
    eccentricity: Optional[float] = np.nan
    err_ceu_rate: MinMax = MinMax(**{})
    mean_anomaly: Optional[float] = np.nan
    node_longitude: Optional[float] = np.nan
    orbital_period: Optional[float] = np.nan
    semi_major_axis: Optional[float] = np.nan
    err_inclination: MinMax = MinMax(**{})
    err_mean_motion: MinMax = MinMax(**{})
    err_eccentricity: MinMax = MinMax(**{})
    err_mean_anomaly: MinMax = MinMax(**{})
    err_node_longitude: MinMax = MinMax(**{})
    err_orbital_period: MinMax = MinMax(**{})
    err_semi_major_axis: MinMax = MinMax(**{})
    perihelion_argument: Optional[float] = np.nan
    err_perihelion_argument: MinMax = MinMax(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class ProperElements(pydantic.BaseModel):
    bibref: List[Bibref] = [Bibref(**{})]
    proper_g: Optional[float] = np.nan
    proper_s: Optional[float] = np.nan
    err_proper_g: MinMax = MinMax(**{})
    err_proper_s: MinMax = MinMax(**{})
    proper_eccentricity: Optional[float] = np.nan
    proper_inclination: Optional[float] = np.nan
    err_proper_inclination: MinMax = MinMax(**{})
    proper_semi_major_axis: Optional[float] = np.nan
    err_proper_eccentricity: MinMax = MinMax(**{})
    proper_sine_inclination: Optional[float] = np.nan
    err_proper_semi_major_axis: MinMax = MinMax(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class Family(pydantic.BaseModel):
    bibref: List[Bibref] = [Bibref(**{})]
    family_name: Optional[str] = ""
    family_number: Optional[int] = None
    family_status: Optional[str] = ""
    family_membership: Optional[int] = None

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class Yarkovsky(pydantic.BaseModel):
    S: Optional[float] = np.nan
    A2: Optional[float] = np.nan
    snr: Optional[float] = np.nan
    dadt: Optional[float] = np.nan
    bibref: List[Bibref] = [Bibref(**{})]
    err_A2: MinMax = MinMax(**{})
    err_dadt: MinMax = MinMax(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class PairMembers(pydantic.BaseModel):
    sibling_name: Optional[str] = ""
    pair_delta_v: Optional[float] = np.nan
    pair_delta_a: Optional[float] = np.nan
    pair_delta_e: Optional[float] = np.nan
    pair_delta_i: Optional[float] = np.nan
    sibling_number: Optional[int] = None


class Pair(pydantic.BaseModel):
    pair_members: List[PairMembers] = [PairMembers(**{})]
    pair_membership: Optional[int] = None

    _ensure_list: classmethod = pydantic.validator(
        "pair_members", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class DynamicalParameters(pydantic.BaseModel):

    pair: Pair = Pair(**{})
    family: Family = Family(**{})
    yarkovsky: Yarkovsky = Yarkovsky(**{})
    proper_elements: ProperElements = ProperElements(**{})
    orbital_elements: OrbitalElements = OrbitalElements(**{})

    def __str__(self):
        return self.json()

    class Config:
        arbitrary_types_allowed = True


class Taxonomy(pydantic.BaseModel):
    class_: Optional[str] = pydantic.Field("", alias="class")
    scheme: Optional[str] = ""
    bibref: List[Bibref] = [Bibref(**{})]
    method: List[Method] = [Method(**{})]
    waverange: Optional[str] = ""

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class Phase(pydantic.BaseModel):
    """Superclass for all phase function measurements."""

    H: Optional[float] = np.nan
    N: Optional[float] = np.nan
    G1: Optional[float] = np.nan
    G2: Optional[float] = np.nan
    err_H: MinMax = MinMax(**{})
    phase: MinMax = MinMax(**{})
    bibref: List[Bibref] = [Bibref(**{})]
    err_G1: MinMax = MinMax(**{})
    err_G2: MinMax = MinMax(**{})
    name_filter: Optional[str] = ""

    _ensure_list: classmethod = pydantic.validator(
        "bibref", allow_reuse=True, pre=True
    )(ensure_list)

    def __str__(self):
        return self.json()


class PhaseFunction(pydantic.BaseModel):

    # ATLAS
    misc_atlas_cyan: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.cyan")
    misc_atlas_orange: Phase = pydantic.Field(Phase(**{}), alias="Misc/Atlas.orange")


class Spin(pydantic.BaseModel):
    period: Optional[float] = np.nan
    err_period: MinMax = MinMax(**{})
    t0: Optional[float] = np.nan
    RA0: Optional[float] = np.nan
    DEC0: Optional[float] = np.nan
    Wp: Optional[float] = np.nan
    long_: Optional[float] = pydantic.Field(np.nan, alias="long")
    lat: Optional[float] = np.nan
    method: Optional[List[Method]] = [Method(**{})]
    bibref: Optional[List[Bibref]] = [Bibref(**{})]

    def __str__(self):
        return self.json()

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class Diameter(pydantic.BaseModel):
    diameter: Optional[float] = np.nan
    err_diameter: MinMax = MinMax(**{})
    method: List[Method] = []
    bibref: List[Bibref] = []

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class Albedo(pydantic.BaseModel):
    albedo: Optional[float] = np.nan
    bibref: List[Bibref] = []
    method: List[Method] = []
    err_albedo: MinMax = MinMax(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class Mass(pydantic.BaseModel):
    mass: Optional[float] = np.nan
    bibref: List[Bibref] = [Bibref(**{})]
    method: List[Method] = [Method(**{})]
    err_mass: MinMax = MinMax(**{})

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class Color(pydantic.BaseModel):
    """Superclass for all colours."""

    color: Optional[float] = np.nan
    epoch: Optional[float] = np.nan
    from_: Optional[str] = pydantic.Field("", alias="from")
    bibref: Bibref = Bibref(**{})
    observer: Optional[str] = ""
    phot_sys: Optional[str] = ""
    err_color: MinMax = MinMax(**{})
    delta_time: Optional[float] = np.nan
    id_filter_1: Optional[str] = ""
    id_filter_2: Optional[str] = ""


class Colors(pydantic.BaseModel):

    # Atlas
    c_o: List[Color] = [pydantic.Field(Color(**{}), alias="c-o")]

    # 2MASS / VISTA
    J_H: List[Color] = [pydantic.Field(Color(**{}), alias="J-H")]
    J_K: List[Color] = [pydantic.Field(Color(**{}), alias="J-K")]
    H_K: List[Color] = [pydantic.Field(Color(**{}), alias="H-K")]

    # SDSS

    _ensure_list: classmethod = pydantic.validator("*", allow_reuse=True, pre=True)(
        ensure_list
    )


class ThermalProperties(pydantic.BaseModel):
    TI: Optional[float] = np.nan
    dsun: Optional[float] = np.nan
    bibref: List[Bibref] = []
    err_TI: MinMax = MinMax(**{})
    method: List[Method] = []

    _ensure_list: classmethod = pydantic.validator(
        "bibref", "method", allow_reuse=True, pre=True
    )(ensure_list)


class PhysicalParameters(pydantic.BaseModel):
    mass: Mass = Mass(**{})
    spin: List[Spin] = [Spin(**{})]
    phase_function: PhaseFunction = PhaseFunction(**{})
    colors: Colors = Colors(**{})
    albedo: Albedo = Albedo(**{})
    diameter: Diameter = Diameter(**{})
    taxonomy: List[Taxonomy] = [Taxonomy(**{})]
    thermal_properties: ThermalProperties = ThermalProperties(**{})

    def __str__(self):
        return self.json()

    _ensure_list: classmethod = pydantic.validator(
        "spin", "taxonomy", allow_reuse=True, pre=True
    )(ensure_list)

    class Config:
        arbitrary_types_allowed = True


class EqStateVector(pydantic.BaseModel):
    ref_epoch: Optional[float] = np.nan
    px: Optional[float] = np.nan
    py: Optional[float] = np.nan
    pz: Optional[float] = np.nan
    vx: Optional[float] = np.nan
    vy: Optional[float] = np.nan
    vz: Optional[float] = np.nan

    def __str__(self):
        return self.json()


class Parameters(pydantic.BaseModel):

    dynamical: DynamicalParameters = DynamicalParameters(**{})
    physical: PhysicalParameters = PhysicalParameters(**{})
    eq_state_vector: EqStateVector = EqStateVector(**{})

    def __str__(self):
        return self.json()

    class Config:
        arbitrary_types_allowed = True


class Link(pydantic.BaseModel):
    unit: Optional[str] = ""
    self_: Optional[str] = pydantic.Field("", alias="self")
    quaero: Optional[str] = ""
    description: Optional[str] = ""


class Ssocard(pydantic.BaseModel):
    version: Optional[str] = ""
    datetime: datetime = None


class Rock(pydantic.BaseModel):
    """Instantiate a specific asteroid with data from its ssoCard."""

    id_: Optional[str] = pydantic.Field("", alias="id")
    name: Optional[str] = ""
    type_: Optional[str] = pydantic.Field("", alias="type")
    class_: Optional[str] = pydantic.Field("", alias="class")
    number: Optional[int] = np.nan
    parent: Optional[str] = ""
    system: Optional[str] = ""

    link: Link = Link(**{})
    ssocard: Ssocard = Ssocard(**{})
    datacloud: rocks.datacloud.Datacloud = rocks.datacloud.Datacloud(**{})
    parameters: Parameters = Parameters(**{})

    aams: AAMS = AAMS(**{})
    astdys: AstDyS = AstDyS(**{})
    astorb: Astorb = Astorb(**{})
    diamalbedo: Diamalbedo = Diamalbedo(**{})
    diameters: Diameters = Diameters(**{})
    albedos: Albedos = Albedos(**{})
    masses: Masses = Masses(**{})
    mpcatobs: Mpcatobs = Mpcatobs(**{})
    pairs: Pairs = Pairs(**{})
    taxonomies: Taxonomies = Taxonomies(**{})

    def __init__(self, id_, ssocard={}, datacloud=[], skip_id_check=False):
        """Identify a minor body  and retrieve its properties from SsODNet.

        Parameters
        ==========
        id_ : str, int, float
            Identifying asteroid name, designation, or number
        ssocard : dict
            Optional argument providing a dictionary to use as ssoCard.
            Default is empty dictionary, triggering the query of an ssoCard.
        datacloud : list of str
            Optional list of additional catalogues to retrieve from datacloud.
            Default is no additional catalogues.
        skip_id_check : bool
            Optional argument to prevent resolution of ID before getting ssoCard.
            Default is False.

        Returns
        =======
        rocks.core.Rock
            An asteroid class instance, with its properties as attributes.

        Notes
        =====
        If the asteroid could not be identified or the data contains invalid
        types, the number is None and no further attributes but the name are set.

        Example
        =======
        >>> from rocks import Rock
        >>> ceres = Rock('ceres')
        >>> ceres.taxonomy.class_
        'C'
        >>> ceres.taxonomy.shortbib
        'DeMeo+2009'
        >>> ceres.diameter
        848.4
        >>> ceres.diameter.unit
        'km'
        """
        if isinstance(datacloud, str):
            datacloud = [datacloud]

        id_provided = id_

        if not skip_id_check:
            _, _, id_ = rocks.identify(id_, return_id=True)  # type: ignore

        # Get ssoCard and datcloud catalogues
        if not pd.isnull(id_):
            if not ssocard:
                ssocard = rocks.ssodnet.get_ssocard(id_)

            for catalogue in datacloud:
                ssocard = self.__add_datacloud_catalogue(id_, catalogue, ssocard)
        else:
            # Something failed. Instantiate minimal ssoCard for meaningful error output.
            ssocard = {"name": id_provided}

        # Deserialize the asteroid data
        try:
            super().__init__(**ssocard)  # type: ignore
        except pydantic.ValidationError as message:
            self.__parse_error_message(message, id_, ssocard)
            return super().__init__(**{"name": id_provided})

    def __getattr__(self, name):
        """Implement attribute shortcuts: omission of parameters.physical/dynamical.
        Gets called if getattribute fails."""

        if name in self.__aliases["physical"].values():
            return getattr(self.parameters.physical, name)

        if name in self.__aliases["dynamical"].values():
            return getattr(self.parameters.dynamical, name)

        raise AttributeError(f"'Rock' object has no attribute '{name}'")

    def __repr__(self):
        return (
            self.__class__.__qualname__
            + f"(number={self.number!r}, name={self.name!r})"
        )

    def __str__(self):
        return f"({self.number}) {self.name}"

    def __hash__(self):
        return hash(self.id_)

    def __add_datacloud_catalogue(self, id_, catalogue, data):
        """Retrieve datacloud catalogue for asteroid and deserialize."""

        if catalogue not in rocks.properties.PROP_TO_DATACLOUD.keys():
            raise ValueError(
                f"Unknown datacloud catalogue name: '{catalogue}'"
                f"\nChoose from {rocks.properties.PROP_TO_DATACLOUD.keys()}"
            )

        catalogue = rocks.properties.PROP_TO_DATACLOUD[catalogue]

        catalogue_attribute = rocks.properties.DATACLOUD_META[catalogue]["attr_name"]
        cat = rocks.ssodnet.get_datacloud_catalogue(id_, catalogue)

        if cat is None:
            return data

        # turn list of dict (catalogue entries) into dict of list
        cat = {
            key: [c[key] for c in cat]
            if catalogue not in ["aams", "astdys", "astorb", "pairs", "families"]
            else cat[0][key]
            for key in cat[0].keys()
        }  # type: ignore

        if catalogue in ["taxonomy", "masses"]:
            cat["preferred"] = [False] * len(list(cat.values())[0])
        elif catalogue in ["diamalbedo"]:
            cat["preferred_albedo"] = [False] * len(list(cat.values())[0])
            cat["preferred_diameter"] = [False] * len(list(cat.values())[0])

            data["diameters"] = cat
            data["albedos"] = cat

        data[catalogue_attribute] = cat
        return data

    def __parse_error_message(self, message, id_, data):
        """Print informative error message if ssocard data is invalid."""
        print(f"{id_}:")

        # Look up offending value in ssoCard
        for error in message.errors():
            value = data
            for loc in error["loc"]:
                value = value[loc]

            rich.print(
                f"Error: {' -> '.join([str(e) for e in error['loc']])} is invalid: {error['msg']}\n"
                f"Passed value: {value}\n"
            )

    __aliases = {
        "dynamical": {
            "parameters.dynamical.orbital_elements": "orbital_elements",
            "parameters.dynamical.proper_elements": "proper_elements",
            "parameters.dynamical.yarkovsky": "yarkovsky",
            "parameters.dynamical.family": "family",
            "parameters.dynamical.pair": "pair",
        },
        "physical": {
            "parameters.physical.diameter": "diameter",
            "parameters.physical.albedo": "albedo",
            "parameters.physical.colors": "colors",
            "parameters.physical.mass": "mass",
            "parameters.physical.thermal_properties": "thermal_properties",
            "parameters.physical.spin": "spin",
            "parameters.physical.taxonomy": "taxonomy",
            "parameters.physical.phase": "phase",
        },
    }


def rocks_(identifier, datacloud=[], progress=False):
    """Create multiple Rock instances.

    Parameters
    ==========
    identifier : list of str, list of int, list of float, np.array, pd.Series
        An iterable containing minor body identifiers.
    datacloud : list of str
        List of additional catalogues to retrieve from datacloud.
        Default is no additional catalogues.
    progress : bool
        Show progress of instantiation. Default is False.

    Returns
    =======
    list of rocks.core.Rock
        A list of Rock instances
    """
    if isinstance(identifier, pd.Series):
        identifier = identifier.values

    ids = [id_ for _, _, id_ in rocks.identify(identifier, return_id=True, progress=progress)]  # type: ignore

    rocks_ = [
        Rock(id_, skip_id_check=True, datacloud=datacloud)
        for id_ in tqdm(
            ids, desc="Building rocks : ", total=len(ids), disable=~progress
        )
    ]

    return rocks_
