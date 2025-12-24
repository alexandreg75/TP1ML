from feast import Entity
from feast.value_type import ValueType

user = Entity(
    name="user",
    join_keys=["user_id"],
    value_type=ValueType.STRING,
    description="Entité représentant un utilisateur StreamFlow, identifiée de manière unique par user_id.",
)
