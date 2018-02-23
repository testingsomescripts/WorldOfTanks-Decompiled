# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportUnitView.py
from UnitBase import UNIT_OP
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.lobby.rally import vo_converters, rally_dps
from gui.Scaleform.daapi.view.meta.CyberSportUnitMeta import CyberSportUnitMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.prb_control import settings
from gui.prb_control.prb_helpers import UnitListener
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared import events, EVENT_BUS_SCOPE, g_itemsCache

class CyberSportUnitView(CyberSportUnitMeta, UnitListener):

    def __init__(self):
        super(CyberSportUnitView, self).__init__()

    def getCoolDownRequests(self):
        requests = super(CyberSportUnitView, self).getCoolDownRequests()
        requests.append(REQUEST_TYPE.CLOSE_SLOT)
        return requests

    def onUnitStateChanged(self, unitState, timeLeft):
        functional = self.unitFunctional
        pInfo = functional.getPlayerInfo()
        rosterSettings = functional.getRosterSettings()
        isCreator = pInfo.isCreator()
        if unitState.isLockedStateChanged():
            vehGetter = pInfo.getVehiclesToSlot
            slotGetter = functional.getSlotState
            slotLabels = map(lambda idx: vo_converters.makeSlotLabel(unitState, slotGetter(idx), isCreator, len(vehGetter(idx))), rosterSettings.getAllSlotsRange())
            self.as_lockUnitS(unitState.isLocked(), slotLabels)
        if isCreator and unitState.isOpenedStateChanged():
            self.as_setOpenedS(unitState.isOpened(), vo_converters.makeUnitStateLabel(unitState))
        self._setActionButtonState()

    def onUnitSettingChanged(self, opCode, value):
        if opCode == UNIT_OP.SET_COMMENT:
            self.as_setCommentS(self.unitFunctional.getCensoredComment())
        elif opCode in [UNIT_OP.CLOSE_SLOT, UNIT_OP.OPEN_SLOT]:
            functional = self.unitFunctional
            unitStats = functional.getStats()
            unitState = functional.getState()
            slotState = functional.getSlotState(value)
            pInfo = functional.getPlayerInfo()
            canAssign, vehicles = pInfo.canAssignToSlot(value)
            vehCount = len(vehicles)
            slotLabel = vo_converters.makeSlotLabel(unitState, slotState, pInfo.isCreator(), vehCount)
            if opCode == UNIT_OP.CLOSE_SLOT:
                self.as_closeSlotS(value, settings.UNIT_CLOSED_SLOT_COST, slotLabel)
            else:
                self.as_openSlotS(value, canAssign, slotLabel, vehCount)
            hasError, label = vo_converters.makeTotalLevelLabel(unitStats)
            self.as_setTotalLabelS(hasError, label, unitStats.curTotalLevel)
            self._setActionButtonState()

    def onUnitVehicleChanged(self, dbID, vInfo):
        functional = self.unitFunctional
        pInfo = functional.getPlayerInfo(dbID=dbID)
        if pInfo.isInSlot:
            slotIdx = pInfo.slotIdx
            if not vInfo.isEmpty():
                vehicleVO = makeVehicleVO(g_itemsCache.items.getItemByCD(vInfo.vehTypeCD))
                slotCost = vInfo.vehLevel
            else:
                slotState = functional.getSlotState(slotIdx)
                vehicleVO = None
                if slotState.isClosed:
                    slotCost = settings.UNIT_CLOSED_SLOT_COST
                else:
                    slotCost = 0
            self.as_setMemberVehicleS(slotIdx, slotCost, vehicleVO)
            unitStats = functional.getStats()
            hasError, label = vo_converters.makeTotalLevelLabel(unitStats)
            self.as_setTotalLabelS(hasError, label, unitStats.curTotalLevel)
        if pInfo.isCreator() or pInfo.isCurrentPlayer():
            self._setActionButtonState()
        return

    def onUnitMembersListChanged(self):
        functional = self.unitFunctional
        if self._candidatesDP:
            self._candidatesDP.rebuild(functional.getCandidates())
        self._updateMembersData()
        self._setActionButtonState()
        unitStats = functional.getStats()
        hasError, label = vo_converters.makeTotalLevelLabel(unitStats)
        self.as_setTotalLabelS(hasError, label, unitStats.curTotalLevel)

    def toggleFreezeRequest(self):
        self.requestToLock(not self.unitFunctional.getState().isLocked())

    def toggleStatusRequest(self):
        self.requestToOpen(not self.unitFunctional.getState().isOpened())

    def showSettingsRoster(self, slots):
        container = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        window = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY})
        if window is not None:
            window.updateSlots(slots)
        else:
            maxLevel = self.unitFunctional.getRosterSettings().getMaxLevel()
            self.fireEvent(events.ShowViewEvent(events.ShowWindowEvent.SHOW_ROSTER_SLOT_SETTINGS_WINDOW, ctx={'settings': slots,
             'section': 'cs_unit_view_settings',
             'maxLevel': maxLevel}), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def cancelRosterSlotsSettings(self):
        self._destroyRelatedView(ViewTypes.TOP_WINDOW, CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY)

    def resultRosterSlotsSettings(self, value):
        self.requestToUpdateRoster(value)
        self._destroyRelatedView(ViewTypes.TOP_WINDOW, CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY)

    def lockSlotRequest(self, slotIndex):
        self.requestToCloseSlot(slotIndex)

    def _updateRallyData(self):
        functional = self.unitFunctional
        data = vo_converters.makeUnitVO(functional, unitIdx=functional.getUnitIdx(), app=self.app)
        self.as_updateRallyS(data)

    def _setActionButtonState(self):
        self.as_setActionButtonStateS(vo_converters.makeUnitActionButtonVO(self.unitFunctional))

    def _getVehicleSelectorDescription(self):
        return CYBERSPORT.WINDOW_VEHICLESELECTOR_INFO_UNIT

    def _populate(self):
        super(CyberSportUnitView, self)._populate()
        self.addListener(events.CSRosterSlotSettingsWindow.APPLY_SLOT_SETTINGS, self.__applyRosterSettings)
        self._updateVehiclesLabel('I', 'VIII')

    def _dispose(self):
        self._destroyRelatedView(ViewTypes.TOP_WINDOW, CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY)
        self.removeListener(events.CSRosterSlotSettingsWindow.APPLY_SLOT_SETTINGS, self.__applyRosterSettings)
        super(CyberSportUnitView, self)._dispose()

    def __applyRosterSettings(self, event):
        self.as_updateSlotSettingsS(event.ctx)

    def initCandidatesDP(self):
        self._candidatesDP = rally_dps.CandidatesDataProvider()
        self._candidatesDP.init(self.as_getCandidatesDPS(), self.unitFunctional.getCandidates())

    def rebuildCandidatesDP(self):
        self._candidatesDP.rebuild(self.unitFunctional.getCandidates())