class BaseCommand:

    def __eq__(self, other):
        return isinstance(self, other)

    def tell(self, message):
        self.table.tell(message, self.player)

    def say(self, message):
        self.table.say(message)

    def fail(self, message):
        self.tell(message)
        self.should_advance = False

    def succeed(self, message):
        self.say(message)
        self.should_advance = True
