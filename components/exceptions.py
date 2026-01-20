class ActionNotFoundException(Exception):

    def __init__(self, action, *args):
        self.action = action
        super().__init__(*args)

    def __str__(self) -> str:
        return f'{self.action.title()} not Found.'


class CommonException(Exception):
    pass
