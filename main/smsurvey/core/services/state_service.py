from smsurvey.core.model.model import Model
from smsurvey.core.model.query.where import Where


class StateService:

    @staticmethod
    def get_state(state_id):
        states = Model.repository.states
        return states.select(Where(states.id, Where.EQUAL, state_id))

    @staticmethod
    def create_state(instance_id, question_id, status, priority):
        states = Model.repository.states
        state = states.create()

        state.instance_id = instance_id
        state.question_id = question_id
        state.status = status.value
        state.priority = priority

        return state.save()

    @staticmethod
    def update_state(state):
        state.save()

    @staticmethod
    def delete_state(state):
        if StateService.get_state(state.id) is not None:
            states = Model.repository.states
            states.delete(Where(states.id, Where.EQUAL, state.id))

    @staticmethod
    def delete_states_for_instances(instances):
        states = Model.repository.states

        instance_ids = [instance.id for instance in instances]

        states.delete(Where(states.instance_id, Where.IN, instance_ids))

    @staticmethod
    def get_next_state_in_instance(instance, status=None):
        instance_id = instance.id
        states = Model.repository.states

        where = Where(states.instance_id, Where.EQUAL, instance_id)

        if status is not None:
            where = where.AND(states.status, Where.EQUAL, status.value)

        state_list = states.select(where)

        if state_list is not None:
            if isinstance(state_list, list):
                lowest_state = state_list[0]
            else:
                lowest_state = state_list
        else:
            return None

        for state in state_list:
            if state.priority < lowest_state.priority:
                lowest_state = state

        return lowest_state

    @staticmethod
    def get_state_by_instance_and_question(instance_id, question_id):
        states = Model.repository.states
        return states.select(Where(states.instance_id, Where.EQUAL, instance_id)
                             .AND(states.question_id, Where.EQUAL, question_id))

    @staticmethod
    def get_unfinished_states(instance):
        instance_id = instance.id
        states = Model.repository.states

        result = states.select(Where(states.instance_id, Where.EQUAL, instance_id)
                             .AND(states.status, Where.LESS_THAN, 500))

        if result is None:
            return None

        if isinstance(result, list):
            return result

        return [result]
