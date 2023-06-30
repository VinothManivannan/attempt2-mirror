"""Pan-Tahini Dataclass Schema
"""
from marshmallow import Schema as AbstractSchema
from marshmallow import post_dump

# pylint: disable=unused-argument

class Schema(AbstractSchema):
    """This function defines rules for serialisation/deserialisation for
    LegacyRegmap dataclasses using marshmallow.
    """

    class Meta:
        """Options object for a Schema
        """
        ordered = True

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        """Post-dump processing function used to remove None values

        Args:
            data (Data object): Data object resulting from the serialisation

        Returns:
            Data object: Processed data object without None
        """
        return {
            key: value for key, value in data.items()
            if value is not None
        }

# pylint: enable=unused-argument
