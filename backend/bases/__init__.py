# import all models from all modules/packages here
from users.models import User
from competitions.models import (
    Competition, CompetitionActivity, CompetitionCustomEvent,
    CompetitionInfoTab, CompetitionRound, CompetitionOrganizer,
    CompetitionRegistration, CompetitionVenue, TimeLimitCumulativeRound
)
from results.models import Result, ResultAttempt, ResultUser