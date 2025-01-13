import pytest
from typing import List, Dict
from jstruct import struct, JList, JDict, JStruct, REQUIRED, asdict


class TestClass(object):
    def test_nested_models_serialization(self):
        payload = {
            "scientists": [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "profession": {
                        "title": "Bio Engineer",
                        "roles": {
                            "researcher": {
                                "description": "applies engineering principles of design and analysis to biological systems and biomedical technologies."
                            }
                        },
                    },
                }
            ]
        }

        role_models = RoleModels(
            scientists=[
                Person(
                    first_name="John",
                    last_name="Doe",
                    profession=Profession(
                        title="Bio Engineer",
                        roles={
                            "researcher": Role(
                                description="applies engineering principles of design and analysis to biological systems and biomedical technologies."
                            )
                        },
                    ),
                )
            ]
        )

        assert role_models == RoleModels(**payload)

    def test_nested_models_deserialization(self):
        role_models = RoleModels(
            scientists=[
                Person(
                    first_name="Jane",
                    last_name="Doe",
                    profession=Profession(
                        title="Astronaut",
                        roles={
                            "researcher": Role(
                                description="An astronaut or cosmonaut is a person trained by a human spaceflight program to command, pilot, or serve as a crew member of a spacecraft."
                            )
                        },
                    ),
                )
            ]
        )

        data = {
            "scientists": [
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "profession": {
                        "title": "Astronaut",
                        "roles": {
                            "researcher": {
                                "description": "An astronaut or cosmonaut is a person trained by a human spaceflight program to command, pilot, or serve as a crew member of a spacecraft."
                            }
                        },
                    },
                }
            ]
        }

        assert data == asdict(role_models)

    def test_nested_models_required_validation(self):
        payload = {
            "scientists": [
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "profession": {
                        "title": "Astronaut"
                    },
                }
            ]
        }

        with pytest.raises(TypeError):
            RoleModels(**payload)


"""
    Test Models
"""


@struct
class Role:
    description: str


@struct
class Profession:
    title: str
    roles: Dict[str, Role] = JDict[str, Role, REQUIRED]


@struct
class Person:
    first_name: str
    last_name: str
    profession: Profession = JStruct[Profession]


@struct
class RoleModels:
    scientists: List[Person] = JList[Person]
