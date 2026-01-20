import enum


class ViewActionScope(enum.Enum):
    """
    Enum class for view action scopes.
    """
    FORM = "form"
    TABLE = "table"
    BASKET = "basket"


class UpdateAction(enum.Enum):
    """
    Enum class for column update action.
    """
    UPDATE_CELL = "update-cell"
    UPDATE_ROW = "update-row"
    UPDATE_BASKET = "update-basket"
    DELETE_ROW = "delete"
    ADD_ROW = "add"

    @property
    def is_cell(self):
        return self.value == UpdateAction.UPDATE_CELL.value

    @property
    def is_row(self):
        return self.value == UpdateAction.UPDATE_ROW.value

    @property
    def is_basket(self):
        return self.value == UpdateAction.UPDATE_BASKET.value

    @property
    def is_delete(self):
        return self.value == UpdateAction.DELETE_ROW.value

    @property
    def is_add(self):
        return self.value == UpdateAction.ADD_ROW.value
