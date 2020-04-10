from mock import MagicMock, patch

class TriggerMock:
    def __init__(self, nick='ldlework', owner=True):
        self.nick = nick
        self.account = nick
        self.owner = owner


class DbMock:
    def __init__(self, memory=None, plugin_db=None, chan_db=None, nick_db=None):
        self.plugin_db = plugin_db or dict()
        self.chan_db = chan_db or dict()
        self.nick_db = nick_db or dict()

    def get_plugin_value(self, plugin, key, default=None):
        plugin_db = self.plugin_db.get(plugin, dict())
        return plugin_db.get(key, default)

    def set_plugin_value(self, plugin, key, value):
        plugin_db = self.plugin_db.get(plugin, dict())
        plugin_db[key] = value
        self.plugin_db[plugin] = plugin_db

    def delete_plugin_value(self, plugin, key):
        plugin_db = self.plugin_db.get(plugin)

        if plugin_db and key in plugin_db:
            del plugin_db[key]

    def get_channel_value(self, chan, key, default=None):
        chan_db = self.chan_db.get(chan, dict())
        return chan_db.get(key, default)

    def set_channel_value(self, chan, key, value):
        chan_db = self.chan_db.get(chan, dict())
        chan_db[key] = value
        self.chan_db[chan] = chan_db

    def delete_channel_value(self, chan, key):
        chan_db = self.chan_db.get(chan)

        if chan_db and key in chan_db:
            del chan_db[key]

    def get_nick_value(self, nick, key, default=None):
        nick_db = self.nick_db.get(nick, dict())
        return nick_db.get(key, default)

    def set_nick_value(self, nick, key, value):
        nick_db = self.nick_db.get(nick, dict())
        nick_db[key] = value
        self.nick_db[nick] = nick_db

    def delete_nick_value(self, nick, key):
        nick_db = self.nick_db.get(nick)

        if nick_db and key in nick_db:
            del nick_db[key]

class SopelMock:
    def __init__(self, memory=None, **kwargs):
        self.memory = memory or dict()
        self.say = MagicMock()
        self.db = DbMock(**kwargs)
