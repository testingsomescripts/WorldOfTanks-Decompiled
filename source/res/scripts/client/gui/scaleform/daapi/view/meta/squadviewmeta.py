# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SquadViewMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyRoomView import BaseRallyRoomView

class SquadViewMeta(BaseRallyRoomView):

    def leaveSquad(self):
        self._printOverrideError('leaveSquad')

    def as_updateBattleTypeInfoS(self, tooltip, isVisible):
        if self._isDAAPIInited():
            return self.flashObject.as_updateBattleTypeInfo(tooltip, isVisible)

    def as_updateBattleTypeS(self, battleTypeName, isFallout, isNew):
        if self._isDAAPIInited():
            return self.flashObject.as_updateBattleType(battleTypeName, isFallout, isNew)

    def as_updateInviteBtnStateS(self, isEnabled):
        if self._isDAAPIInited():
            return self.flashObject.as_updateInviteBtnState(isEnabled)

    def as_setCoolDownForReadyButtonS(self, timer):
        if self._isDAAPIInited():
            return self.flashObject.as_setCoolDownForReadyButton(timer)
