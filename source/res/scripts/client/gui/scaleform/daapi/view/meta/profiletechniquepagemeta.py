# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileTechniquePageMeta.py
from gui.Scaleform.daapi.view.lobby.profile.ProfileTechnique import ProfileTechnique

class ProfileTechniquePageMeta(ProfileTechnique):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends ProfileTechnique
    null
    """

    def setIsInHangarSelected(self, value):
        """
        :param value:
        :return :
        """
        self._printOverrideError('setIsInHangarSelected')

    def as_setSelectedVehicleIntCDS(self, index):
        """
        :param index:
        :return :
        """
        return self.flashObject.as_setSelectedVehicleIntCD(index) if self._isDAAPIInited() else None
