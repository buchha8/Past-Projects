class KeybindManager:
    def __init__(self, app_state_manager):
        self.app_state_manager = app_state_manager

    # -------------------------
    # Internal helpers
    # -------------------------
    def _get_keybinds(self):
        return self.app_state_manager.get_state().get("keybinds", [])

    def _set_keybinds(self, keybinds):
        data = self.app_state_manager.get_state()
        data["keybinds"] = keybinds

    # -------------------------
    # Public API
    # -------------------------
    def add_keybind(self, key, gesture=None, sensitivity=1.0, locked=False):
        keybinds = self._get_keybinds()

        for kb in keybinds:
            if kb["key"] == key:
                raise ValueError(f"Keybind for '{key}' already exists")

        keybinds.append({
            "key": key,
            "gesture": gesture,
            "sensitivity": sensitivity,
            "locked": locked
        })

        self._set_keybinds(keybinds)

    def delete_keybind(self, index):
        keybinds = self._get_keybinds()

        if index < 0 or index >= len(keybinds):
            return

        if keybinds[index].get("locked", False):
            return

        keybinds.pop(index)
        self._set_keybinds(keybinds)

    def update_gesture(self, key, gesture):
        keybinds = self._get_keybinds()

        for kb in keybinds:
            if kb["key"] == key:
                kb["gesture"] = gesture
                break

        self._set_keybinds(keybinds)

    def update_sensitivity(self, key, sensitivity):
        keybinds = self._get_keybinds()

        for kb in keybinds:
            if kb["key"] == key:
                kb["sensitivity"] = float(sensitivity)
                break

        self._set_keybinds(keybinds)

    def get_keybinds(self):
        return self._get_keybinds()

    def get_by_key(self, key):
        for kb in self._get_keybinds():
            if kb["key"] == key:
                return kb
        return None