import time

from smsurvey.core.model.status import Status
from smsurvey.core.model.model import Model
from smsurvey.core.model.query.where import Where
from smsurvey.core.model.query.inner_join import InnerJoin

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
        return instance.save()

    @staticmethod
    def delete_instances(instance_ids):
        instances = Model.repository.instances
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
    def get_current_instance_ids():
        instances = Model.repository.instances
        return instances.select()

    @staticmethod
    def start_instance(instance_id):
        print("Starting instance " + str(instance_id))

        instance = InstanceService.get_instance(instance_id)
        survey = SurveyService.get_survey(instance.survey_id)
        first_question = ProtocolService.get_protocol(survey.survey_id)

        StateService.create_state(instance_id, first_question, Status.CREATED_START, 0)

        participant = ParticipantService.get_participant(survey.participant_id)
        PluginService.poke(participant.plugin_id, survey.survey_id)

    @staticmethod
    def run_loop():
        print("Starting instance service loop")
        while True:
            print("Running instance service loop")
            instance_ids = InstanceService.get_current_instance_ids()

            not_started = []
            in_progress = []
            finished = []

            for instance_id in instance_ids:
                latest = StateService.get_next_state_in_instance(instance_id)

                if latest is None:
                    not_started.append(instance_id)
                else:
                    in_progress.append(instance_id)

            for instance_id in in_progress:
                unfinished = StateService.get_unfinished_states(instance_id)

                if len(unfinished) is 0:
                    finished.append(instance_id)

            if len(finished) > 0:
                print("Instances that have finished: " + str(finished))

                InstanceService.delete_instances(finished)
                StateService.delete_states_for_instances(finished)

            if len(not_started) > 0:
                print("Instances that have not started: " + str(not_started))

                for instance_id in not_started:
                    InstanceService.start_instance(instance_id)

            time.sleep(60)
