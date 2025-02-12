# Licensed under a 3-clause BSD style license - see LICENSE.rst

# STDLIB
import copy
from collections import OrderedDict

# THIRD PARTY
import pytest

# LOCAL
import astropy.units as u
from astropy.cosmology import Cosmology, realizations
from astropy.cosmology.core import _COSMOLOGY_CLASSES, Parameter
from astropy.cosmology.io.mapping import from_mapping, to_mapping
from astropy.cosmology.parameters import available
from astropy.table import QTable, vstack


cosmo_instances = [getattr(realizations, name) for name in available]
cosmo_instances.append("TestToFromMapping.setup.<locals>.CosmologyWithKwargs")


###############################################################################


class ToFromMappingTestMixin:
    """
    Tests for a Cosmology[To/From]Format with ``format="mapping"``.
    This class will not be directly called by :mod:`pytest` since its name does
    not begin with ``Test``. To activate the contained tests this class must
    be inherited in a subclass. Subclasses must define a :func:`pytest.fixture`
    ``cosmo`` that returns/yields an instance of a |Cosmology|.
    See ``TestCosmologyToFromFormat`` or ``TestCosmology`` for examples.
    """

    @pytest.fixture
    def to_format(self, cosmo):
        """Convert Cosmology instance using ``.to_format()``."""
        return cosmo.to_format

    @pytest.fixture
    def from_format(self, cosmo):
        """Convert mapping to Cosmology using ``Cosmology.from_format()``."""
        return Cosmology.from_format

    # ==============================================================

    def test_failed_cls_to_mapping(self, cosmo, to_format):
        """Test incorrect argument ``cls`` in ``to_mapping()``."""
        with pytest.raises(TypeError, match="'cls' must be"):
            to_format('mapping', cls=list)

    @pytest.mark.parametrize("map_cls", [dict, OrderedDict])
    def test_to_mapping_cls(self, cosmo, to_format, map_cls):
        """Test argument ``cls`` in ``to_mapping()``."""
        params = to_format('mapping', cls=map_cls)
        assert isinstance(params, map_cls)  # test type

    def test_to_from_mapping_instance(self, cosmo, to_format, from_format):
        """Test cosmology -> Mapping -> cosmology."""
        # ------------
        # To Mapping

        params = to_format('mapping')
        assert isinstance(params, dict)  # test type
        assert params["cosmology"] is cosmo.__class__
        assert params["name"] == cosmo.name

        # ------------
        # From Mapping

        params["mismatching"] = "will error"

        # tests are different if the last argument is a **kwarg
        if tuple(cosmo._init_signature.parameters.values())[-1].kind == 4:
            got = from_format(params, format="mapping")

            assert got.name == cosmo.name
            assert "mismatching" not in got.meta

            return  # don't continue testing

        # read with mismatching parameters errors
        with pytest.raises(TypeError, match="there are unused parameters"):
            from_format(params, format="mapping")

        # unless mismatched are moved to meta
        got = from_format(params, format="mapping", move_to_meta=True)
        assert got == cosmo
        assert got.meta["mismatching"] == "will error"

        # it won't error if everything matches up
        params.pop("mismatching")
        got = from_format(params, format="mapping")
        assert got == cosmo

        # and it will also work if the cosmology is a string
        params["cosmology"] = params["cosmology"].__qualname__
        got = from_format(params, format="mapping")
        assert got == cosmo

        # also it auto-identifies 'format'
        got = from_format(params)
        assert got == cosmo

    def test_fromformat_subclass_partial_info_mapping(self, cosmo):
        """
        Test writing from an instance and reading from that class.
        This works with missing information.
        """
        # test to_format
        m = cosmo.to_format("mapping")
        assert isinstance(m, dict)

        # partial information
        m.pop("cosmology", None)
        m.pop("Tcmb0", None)

        # read with the same class that wrote fills in the missing info with
        # the default value
        got = cosmo.__class__.from_format(m, format="mapping")
        got2 = Cosmology.from_format(m, format="mapping", cosmology=cosmo.__class__)
        got3 = Cosmology.from_format(m, format="mapping", cosmology=cosmo.__class__.__qualname__)

        assert (got == got2) and (got2 == got3)  # internal consistency

        # not equal, because Tcmb0 is changed
        assert got != cosmo
        assert got.Tcmb0 == cosmo.__class__._init_signature.parameters["Tcmb0"].default
        assert got.clone(name=cosmo.name, Tcmb0=cosmo.Tcmb0) == cosmo
        # but the metadata is the same
        assert got.meta == cosmo.meta


class TestToFromMapping(ToFromMappingTestMixin):
    """
    Directly test ``to/from_mapping``.
    These are not public API and are discouraged from use, in favor of
    ``Cosmology.to/from_format(..., format="mapping")``, but should be tested
    regardless b/c 3rd party packages might use these in their Cosmology I/O.
    Also, it's cheap to test.
    """

    @pytest.fixture(scope="class", autouse=True)
    def setup(self):
        """Setup and teardown for tests."""

        class CosmologyWithKwargs(Cosmology):
            Tcmb0 = Parameter(unit=u.K)

            def __init__(self, Tcmb0=0, name="cosmology with kwargs", meta=None, **kwargs):
                super().__init__(name=name, meta=meta)
                self._Tcmb0 = Tcmb0 << u.K

        yield  # run tests

        # pop CosmologyWithKwargs from registered classes
        # but don't error b/c it can fail in parallel
        _COSMOLOGY_CLASSES.pop(CosmologyWithKwargs.__qualname__, None)

    @pytest.fixture(params=cosmo_instances)
    def cosmo(self, request):
        """Cosmology instance."""
        if isinstance(request.param, str):  # CosmologyWithKwargs
            return _COSMOLOGY_CLASSES[request.param](Tcmb0=3)
        return request.param

    @pytest.fixture
    def to_format(self, cosmo):
        """Convert Cosmology to mapping using function ``to_mapping()``."""
        return lambda *args, **kwargs: to_mapping(cosmo, *args, **kwargs)

    @pytest.fixture
    def from_format(self):
        """Convert mapping to Cosmology using function ``from_mapping()``."""
        def use_from_mapping(*args, **kwargs):
            kwargs.pop("format", None)  # specific to Cosmology.from_format
            return from_mapping(*args, **kwargs)

        return use_from_mapping
