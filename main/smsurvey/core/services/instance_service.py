import time
import pytz

from datetime import datetime

from smsurvey.core.model.status import Status
from smsurvey.core.model.model import Model
from smsurvey.core.model.query.where import Where
from smsurvey.core.model.query.inner_join import InnerJoin
from smsurvey.core.services.enrollment_service import EnrollmentService
from smsurvey.core.services.participant_service import ParticipantService
from smsurvey.core.services.plugin_service import PluginService
from smsurvey.core.services.protocol_service import ProtocolService
from smsurvey.core.services.state_service import StateService
from smsurvey.core.services.survey_service import SurveyService


class InstanceService:
    @staticmethod
    def get_instance(instance_id):
        instances = Model.repository.instances
        return instances.select(Where(instances.id, Where.EQUAL, instance_id))

    @staticmethod
    def create_instance(survey_id):
        instances = Model.repository.instances
        instance = instances.create()

        instance.survey_id = survey_id
        instance.created = datetime.now(tz=pytz.utc)
        return instance.save()

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
            instance_list = instances.select(InnerJoin(surveys, instances.survey_id, InnerJoin.EQUAL, surveys.id),
                             Where(surveys.owner_id, Where.EQUAL, owner_id))
        else:
            instance_list = instances.select(InnerJoin(surveys, instances.survey_id, InnerJoin.EQUAL, surveys.id),
                             Where(surveys.owner_id, Where.EQUAL, owner_id).AND(surveys.id, Where.EQUAL, survey_id))

        if status is None:
            return instance_list
        else:
            final_list = []
            for instance in instance_list:
                state = StateService.get_next_state_in_instance(instance.id, status)

                if state is not None and status == state.status:
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

        result = instances.select()

        if result is None:
            return None

        if isinstance(result, list):
            return result

        return [result]

    @staticmethod
    def start_instance(instance):
        instance_id = instance.id
        print("Starting instance " + str(instance_id))

        survey = SurveyService.get_survey(instance.survey_id)
        first_question = ProtocolService.get_protocol(survey.protocol_id)

        StateService.create_state(instance_id, first_question.id, Status.CREATED_START, 0)

        participants = ParticipantService.get_participants_in_enrollment(survey.enrollment_id)

        plugin_ids = set()

        for participant in participants:
            plugin_ids.add(participant.plugin_id)

        for plugin_id in plugin_ids:
            PluginService.poke(plugin_id, survey.id)

    @staticmethod
    def run_loop():
        print("Starting instance service loop")
        while True:
            print("Running instance service loop")
            instances = InstanceService.get_current_instances()

            if instances is not None:

                not_started = []
                in_progress = []
                finished = []

                for instance in instances:
                    latest = StateService.get_next_state_in_instance(instance)

                    if latest is None:
                        not_started.append(instance)
                    else:
                        in_progress.append(instance)

                for instance in in_progress:
                    unfinished = StateService.get_unfinished_states(instance)

                    if unfinished is None or len(unfinished) is 0:
                        finished.append(instance)

                if len(finished) > 0:
                    print("Instances that have finished: " + str(finished))

                    InstanceService.delete_instances(finished)
                    StateService.delete_states_for_instances(finished)

                if len(not_started) > 0:
                    print("Starting " + str(len(not_started)) + " instances")

                    for instance in not_started:
                        InstanceService.start_instance(instance)

            time.sleep(60)
