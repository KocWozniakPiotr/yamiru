create_character = 'p00'
nick_change = 'p01'


class PlayerHandler:
    server_response = ''

    def update(self, content):
        command = content[:3]
        parameter = content[3:]

        if command == nick_change:
            self.change_nickname(parameter)
        elif command == create_character:
            self.character_create(parameter)

    def change_nickname(self, msg):
        print(msg)

    def character_create(self, msg):
        self.server_response = msg
