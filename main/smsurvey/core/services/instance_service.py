import time
import pytz

from datetime import datetime, timedelta

from smsurvey.config import logger
from smsurvey.core.model.status import Status
from smsurvey.core.model.model import Model
from smsurvey.core.model.query.where import Where
from smsurvey.core.model.query.inner_join import InnerJoin
from smsurvey.core.services.participant_service import ParticipantService
from smsurvey.core.services.plugin_service import PluginService
from smsurvey.core.services.state_service import StateService
from smsurvey.core.services.survey_service import SurveyService


class InstanceService:
    @staticmethod
    def get_instance(instance_id):
        instances = Model.repository.instances
        return instances.select(Where(instances.id, Where.EQUAL, instance_id))

    @staticmethod
    def create_instances(survey_id):
        # Get survey
        surveys = Model.repository.surveys
        survey = surveys.select(Where(surveys.id, Where.E, survey_id))

        # Get all participants in enrollment
        participants = Model.repository.participants
        participant_list = participants.select(Where(participants.enrollment_id, Where.E, survey.enrollment_id),
                                               force_list=True)

        instances = Model.repository.instances
        returnable = []
        for participant in participant_list:
            instance = instances.create()
            instance.survey_id = survey_id
            instance.participant_id = participant.id
            instance.created = datetime.now(tz=pytz.utc)
            returnable.append(instance.save())

        return returnable

    @staticmethod
    def delete_instances(to_delete):
        instances = Model.repository.instances

        instance_ids = [instance.id for instance in to_delete]

        instances.delete(Where(instances.id, Where.IN, instance_ids))

    @staticmethod
    def get_by_owner(owner_id, survey_id=None, status=None):
        instances = Model.repository.instances
        surveys = Model.repository.surveys

        if survey_id is None:
            instance_list = instances.select(InnerJoin(instances, surveys, instances.survey_id, InnerJoin.EQUAL,
                                                       surveys.id), Where(surveys.owner_id, Where.EQUAL, owner_id),
                                             force_list=True)
        else:
            instance_list = instances.select(InnerJoin(instances, surveys, instances.survey_id, InnerJoin.EQUAL,
                                                       surveys.id), Where(surveys.owner_id, Where.EQUAL, owner_id)
                                             .AND(surveys.id, Where.EQUAL, survey_id), force_list=True)

        if status is None:
            return instance_list
        else:
            final_list = []

            for instance in instance_list:
                state = StateService.get_next_state_in_instance(instance, status)

                if state is not None and status.value == state.status:
                    final_list.append(instance)

            return final_list

    @staticmethod
    def get_survey_id(instance_id):
        instance = InstanceService.get_instance(instance_id)

        if instance is not None:
            return instance.survey_id

        return None

    @staticmethod
    def get_current_instances():
        instances = Model.repository.instances
        return instances.select(force_list=True)

    @staticmethod
    def start_instance(instance):
        instance_id = instance.id
        print("Starting instance " + str(instance_id))

        survey = SurveyService.get_survey(instance.survey_id)
        timeout_minutes = survey.timeout
        timeout_timestamp = datetime.now(tz=pytz.utc) + timedelta(minutes=timeout_minutes)

        StateService.create_state(instance_id, 1, Status.CREATED_START, timeout_timestamp, 0)

        participants = ParticipantService.get_participants_in_enrollment(survey.enrollment_id)

        plugin_ids = set()

        for participant in participants:
            plugin_ids.add(participant.plugin_id)

        for plugin_id in plugin_ids:
            PluginService.poke(plugin_id, survey.id)

    @staticmethod
    def send_message_for_instance(instance, message):
        survey = SurveyService.get_survey(instance.survey_id)
        participants = ParticipantService.get_participants_in_enrollment(survey.enrollment_id)

        for participant in participants:
            PluginService.send_message(participant.plugin_id, instance.id, message)

    @staticmethod
    def run_loop():
        logger.info("Starting instance service loop")

        next_warning = {}

        while True:
            logger.info("Running instance service loop")
            instances = InstanceService.get_current_instances()

            if instances is not None:
                logger.info("%d instances existing", len(instances))

                not_started = []
                in_progress = []
                finished = []

                for instance in instances:
                    latest = StateService.get_next_state_in_instance(instance)

                    if latest is None:
                        not_started.append(instance)
                    else:
                        in_progress.append(instance)

                now = datetime.now(tz=pytz.utc)

                for instance in in_progress:
                    unfinished = StateService.get_unfinished_states(instance)

                    if unfinished is None or len(unfinished) is 0:
                        finished.append(instance)
                    elif unfinished[0].timeout.replace(tzinfo=pytz.utc) < now:
                        InstanceService.send_message_for_instance(instance,
                                                                  "Survey has expired")
                        finished.append(instance)
                    else:
                        if instance.id not in next_warning:
                            next_warning[instance.id] = now + timedelta(minutes=5)
                        else:
                            if now > next_warning[instance.id]:
                                expires = StateService.get_next_state_in_instance(instance).timeout\
                                    .replace(tzinfo=pytz.utc)
                                now_ts = time.mktime(now.timetuple())
                                expires_ts = time.mktime(expires.timetuple())
                                delta = str(int((expires_ts - now_ts) / 60))
                                message = "Warning - survey expires in " + delta + " minutes"
                                InstanceService.send_message_for_instance(instance, message)
                                next_warning[instance.id] = now + timedelta(minutes=5)


                logger.info("%d instances not started, %d instances in progress, %d instances awaiting purge",
                            len(not_started), len(in_progress), len(finished))

                if len(finished) > 0:
                    logger.info("Purging instances: %s", str(finished))

                    InstanceService.delete_instances(finished)
                    StateService.delete_states_for_instances(finished)

                    if instance.id in next_warning:
                        del next_warning[instance.id]

                if len(not_started) > 0:
                    logger.info("Starting instances: %s", str(not_started))

                    for instance in not_started:
                        InstanceService.start_instance(instance)
            else:
                logger.info("No instances exist")

            time.sleep(30)
