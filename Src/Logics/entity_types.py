from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_model import recipe_model


entity_types = {
    "ranges": range_model,
    "groups": group_model,
    "warehouses": warehouse_model,
    "nomenclatures": nomenclature_model,
    "recipes": recipe_model,
}


def entity_links(entity) -> list[tuple]:
    """Поля, ссылающиеся на другие сущности."""
    if isinstance(entity, range_model):
        return [(entity, "base_range")]
    if isinstance(entity, nomenclature_model):
        return [(entity, "group"), (entity, "range")]
    if isinstance(entity, recipe_model):
        links = [(entity, "output_range"), (entity, "target_nomenclature")]
        for row in entity.rows:
            links.extend((row, field) for field in ("nomenclature", "range", "sub_recipe"))
        return links
    return []
