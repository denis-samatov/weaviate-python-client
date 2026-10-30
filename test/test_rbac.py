from weaviate.classes.rbac import Actions, Permissions
from weaviate.rbac.models import Role


def test_permissions_roles_only_manage_false() -> None:
    permissions = Permissions.roles(read=False, role="*")
    assert len(permissions) == 0


def test_permissions_roles_only_manage_true() -> None:
    permissions = Permissions.roles(read=True, role="*")
    assert len(permissions) == 1
    assert len(permissions[0].actions) == 1


def test_permissions_roles() -> None:
    permissions = Permissions.roles(read=True, create=False, role="*")
    assert len(permissions) == 1
    assert len(permissions[0].actions) == 1


def test_permissions_backup_read() -> None:
    permissions = Permissions.backup(collection="books", read=True)
    assert [p._to_weaviate() for p in permissions] == [
        [{"action": "read_backups", "backups": {"collection": "Books"}}]
    ]


def test_role_parses_read_backups() -> None:
    role = Role._from_weaviate_role(
        {
            "name": "r",
            "permissions": [{"action": "read_backups", "backups": {"collection": "Books"}}],
        }
    )
    assert role.backups_permissions[0].actions == {Actions.Backups.READ}


def test_backup_defaults_and_manage_preserve_least_privilege() -> None:
    assert Permissions.backup(collection="Books") == []
    permission = Permissions.backup(collection="Books", manage=True)[0]
    assert permission.actions == {Actions.Backups.MANAGE}
    assert Actions.Backups.READ not in permission.actions


def test_backup_collection_sequence_and_combined_actions_round_trip() -> None:
    permissions = Permissions.backup(collection=["Books", "Articles"], read=True, manage=True)
    assert len(permissions) == 2
    assert {permission.collection for permission in permissions} == {"Books", "Articles"}
    for permission in permissions:
        assert permission.actions == {Actions.Backups.READ, Actions.Backups.MANAGE}
        assert {entry["action"] for entry in permission._to_weaviate()} == {
            "read_backups",
            "manage_backups",
        }
