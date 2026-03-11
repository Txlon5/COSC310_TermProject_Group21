from app.repositories.menu_repository import get_all_restaurants, get_all_menus


def test_repository_get_all_restaurants():
    restaurants = get_all_restaurants()
    assert isinstance(restaurants, list)
    assert len(restaurants) >= 1


def test_repository_get_all_menus():
    menus = get_all_menus()
    assert isinstance(menus, list)
    assert len(menus) >= 1