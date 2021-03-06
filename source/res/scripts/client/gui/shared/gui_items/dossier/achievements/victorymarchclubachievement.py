# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/VictoryMarchClubAchievement.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from abstract import SeriesAchievement
from abstract.mixins import Deprecated, NoProgressBar

class VictoryMarchClubAchievement(Deprecated, NoProgressBar, SeriesAchievement):

    def __init__(self, dossier, value=None):
        super(VictoryMarchClubAchievement, self).__init__('victoryMarch', _AB.SINGLE_7X7, dossier, value)

    def _getCounterRecordNames(self):
        return ((_AB.RATED_7X7, 'victoryMarchSeries'), (_AB.RATED_7X7, 'maxVictoryMarchSeries'))
