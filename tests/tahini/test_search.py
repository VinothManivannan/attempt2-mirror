"""
Tests for the search function
"""
import unittest
from tahini.cmap_schema import ArrayIndex as CmapArrayIndex
from tahini.cmap_schema import CType as CmapCtype
from tahini.cmap_schema import Register as CmapRegister
from tahini.cmap_schema import RegisterOrStruct as CmapRegisterOrStruct
from tahini.cmap_schema import Regmap as CmapRegmap
from tahini.cmap_schema import Struct as CmapStruct
from tahini.cmap_schema import Type as CmapType
from tahini.search import search


class TestSearch(unittest.TestCase):
    """Tests for the search function
    """
    _CMAP_REGMAP = CmapRegmap(
        children=[
            CmapRegisterOrStruct(
                name="alpha",
                type=CmapType.REGISTER,
                addr=256,
                size=2,
                register=CmapRegister(
                    ctype=CmapCtype.UINT16
                )
            ),
            CmapRegisterOrStruct(
                name="beta",
                type=CmapType.STRUCT,
                addr=512,
                size=26,
                struct=CmapStruct(
                    children=[
                        CmapRegisterOrStruct(
                            name="gamma",
                            type=CmapType.REGISTER,
                            addr=512,
                            size=2,
                            register=CmapRegister(
                                ctype=CmapCtype.UINT16
                            )
                        ),
                        CmapRegisterOrStruct(
                            name="delta",
                            type=CmapType.STRUCT,
                            addr=514,
                            size=24,
                            struct=CmapStruct(
                                children=[
                                    CmapRegisterOrStruct(
                                        name="epsilon_d",
                                        type=CmapType.REGISTER,
                                        addr=514,
                                        size=2,
                                        register=CmapRegister(
                                            ctype=CmapCtype.UINT16
                                        ),
                                        repeat_for=[CmapArrayIndex(
                                            count=3,
                                            aliases=["x", "y", "z"],
                                            offset=2
                                        )]
                                    ),
                                    CmapRegisterOrStruct(
                                        name="zeta_d",
                                        type=CmapType.STRUCT,
                                        addr=520,
                                        size=6,
                                        repeat_for=[CmapArrayIndex(
                                            count=3,
                                            aliases=["rx", "ry", "rz"],
                                            offset=6
                                        )],
                                        struct=CmapStruct(
                                            children=[
                                                CmapRegisterOrStruct(
                                                    name="eta",
                                                    type=CmapType.REGISTER,
                                                    addr=520,
                                                    size=2,
                                                    register=CmapRegister(
                                                        ctype=CmapCtype.UINT16
                                                    ),
                                                    repeat_for=[
                                                        CmapArrayIndex(
                                                            count=3,
                                                            aliases=["rx", "ry", "rz"],
                                                            offset=6
                                                        )
                                                    ]
                                                ),
                                                CmapRegisterOrStruct(
                                                    name="theta",
                                                    type=CmapType.REGISTER,
                                                    addr=522,
                                                    size=2,
                                                    register=CmapRegister(
                                                        ctype=CmapCtype.UINT16
                                                    ),
                                                    repeat_for=[
                                                        CmapArrayIndex(
                                                            count=3,
                                                            aliases=["rx", "ry", "rz"],
                                                            offset=6
                                                        ),
                                                        CmapArrayIndex(
                                                            count=2,
                                                            offset=2
                                                        )
                                                    ]
                                                )
                                            ]
                                        )
                                    )
                                ]
                            )
                        )
                    ]
                )
            )
        ]
    )

    def test_search_register_simple(self):
        """Check that we can find a register in the most simple case
        """
        expected_result = TestSearch._CMAP_REGMAP.children[0]

        match = search(name="alpha", cmap_type=CmapType.REGISTER, node=TestSearch._CMAP_REGMAP)

        self.assertIsNotNone(match)
        self.assertEqual(expected_result, match.result)
        self.assertEqual(256, match.address)

    def test_search_register_not_present(self):
        """Check that if we search for a register which is not present, we don't get any
        match.
        """

        match = search(name="zeta", cmap_type=CmapType.REGISTER, node=TestSearch._CMAP_REGMAP)

        self.assertIsNone(match)

    def test_search_register_does_not_match_struct_with_same_same(self):
        """Check that if we search for a register then structs with the same name do not
        return a match.
        """
        struct_name = "beta"

        self.assertIsNone(search(name=struct_name, cmap_type=CmapType.REGISTER, node=TestSearch._CMAP_REGMAP))
        self.assertIsNotNone(search(name=struct_name, cmap_type=CmapType.STRUCT, node=TestSearch._CMAP_REGMAP))

    def test_search_register_nested(self):
        """Check that we can find a register nested in another struct
        """
        expected_result = TestSearch._CMAP_REGMAP.children[1].struct.children[0]

        match = search(name="gamma", cmap_type=CmapType.REGISTER, node=TestSearch._CMAP_REGMAP)

        self.assertIsNotNone(match)
        self.assertEqual(expected_result, match.result)
        self.assertEqual(512, match.address)

    def test_search_register_in_array_by_index(self):
        """Check that we can find a register in an array using its index
        """
        expected_result = TestSearch._CMAP_REGMAP.children[1].struct.children[1].struct.children[0]

        match = search(name="epsilon_d1", cmap_type=CmapType.REGISTER, node=TestSearch._CMAP_REGMAP)

        self.assertIsNotNone(match)
        self.assertEqual(expected_result, match.result)
        self.assertEqual(516, match.address)

    def test_search_register_in_array_by_alias(self):
        """Check that we can find a register in an array using its alias
        """
        expected_result = TestSearch._CMAP_REGMAP.children[1].struct.children[1].struct.children[0]

        match = search(name="epsilon_dz", cmap_type=CmapType.REGISTER, node=TestSearch._CMAP_REGMAP)

        self.assertIsNotNone(match)
        self.assertEqual(expected_result, match.result)
        self.assertEqual(518, match.address)

    def test_search_register_using_mixed_case_name(self):
        """Check that we can find a register even if the name case does not match
        """
        expected_result = TestSearch._CMAP_REGMAP.children[0]

        match = search(name="aLpHa", cmap_type=CmapType.REGISTER, node=TestSearch._CMAP_REGMAP)

        self.assertIsNotNone(match)
        self.assertEqual(expected_result, match.result)
        self.assertEqual(256, match.address)

    def test_search_register_using_mixed_case_alias(self):
        """Check that we can find a register even if the alias case does not match
        """
        expected_result = TestSearch._CMAP_REGMAP.children[1].struct.children[1].struct.children[0]

        match = search(name="epsilon_dZ", cmap_type=CmapType.REGISTER, node=TestSearch._CMAP_REGMAP)

        self.assertIsNotNone(match)
        self.assertEqual(expected_result, match.result)
        self.assertEqual(518, match.address)

    def test_search_register_from_a_struct(self):
        """Check that we can find a nested register when running a search from a struct
        """
        struct = TestSearch._CMAP_REGMAP.children[1].struct.children[1]
        expected_result = TestSearch._CMAP_REGMAP.children[1].struct.children[1].struct.children[0]

        match = search(name="epsilon_dZ", cmap_type=CmapType.REGISTER, node=struct)

        self.assertIsNotNone(match)
        self.assertEqual(expected_result, match.result)
        self.assertEqual(518, match.address)

    def test_search_register_not_present_from_a_struct(self):
        """Check that we can find a nested register when running a search from a struct
        """
        struct = TestSearch._CMAP_REGMAP.children[1].struct.children[1]

        match = search(name="alpha", cmap_type=CmapType.REGISTER, node=struct)

        self.assertIsNone(match)

    def test_search_struct_simple(self):
        """Check that we can find a struct in the most simple case
        """
        expected_result = TestSearch._CMAP_REGMAP.children[1]

        match = search(name="beta", cmap_type=CmapType.STRUCT, node=TestSearch._CMAP_REGMAP)

        self.assertIsNotNone(match)
        self.assertEqual(expected_result, match.result)
        self.assertEqual(512, match.address)

    def test_search_struct_does_not_match_register_with_same_same(self):
        """Check that if we search for a register then structs with the same name do not
        return a match.
        """
        register_name = "alpha"

        self.assertIsNone(search(name=register_name, cmap_type=CmapType.STRUCT, node=TestSearch._CMAP_REGMAP))
        self.assertIsNotNone(search(name=register_name, cmap_type=CmapType.REGISTER, node=TestSearch._CMAP_REGMAP))

    def test_search_struct_nested(self):
        """Check that we can find a struct nested in another struct
        """
        expected_result = TestSearch._CMAP_REGMAP.children[1].struct.children[1]

        match = search(name="delta", cmap_type=CmapType.STRUCT, node=TestSearch._CMAP_REGMAP)

        self.assertIsNotNone(match)
        self.assertEqual(expected_result, match.result)
        self.assertEqual(514, match.address)

    def test_search_struct_in_array(self):
        """Check that we can find a struct in an array using its index
        """
        expected_result = TestSearch._CMAP_REGMAP.children[1].struct.children[1].struct.children[1]

        match = search(name="zeta_drz", cmap_type=CmapType.STRUCT, node=TestSearch._CMAP_REGMAP)

        self.assertIsNotNone(match)
        self.assertEqual(expected_result, match.result)
        self.assertEqual(532, match.address)

    def test_search_register_in_nested_array(self):
        """Check that we can find a register in an array, part of another array
        """
        expected_result = TestSearch._CMAP_REGMAP.children[1].\
            struct.children[1].struct.children[1].struct.children[1]

        match = search(name="thetarz_1", cmap_type=CmapType.REGISTER, node=TestSearch._CMAP_REGMAP)

        self.assertIsNotNone(match)
        self.assertEqual(expected_result, match.result)
        self.assertEqual(536, match.address)

    def test_search_register_with_invalid_alias(self):
        """Check that we search for a register using an invalid alias, we don't get a match
        """
        match = search(name="thetarz_x", cmap_type=CmapType.REGISTER, node=TestSearch._CMAP_REGMAP)

        self.assertIsNone(match)
