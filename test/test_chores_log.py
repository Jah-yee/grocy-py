from datetime import datetime

import pytest

from grocy.data_models.chore import Chore
from grocy.data_models.chore_log import ChoreLog
from grocy.data_models.user import User
from grocy.errors import GrocyError


class TestChoresLog:
    @pytest.mark.vcr
    def test_get_chores_log_valid(self, grocy):
        chores_log = grocy.chores_log.list(get_details=True)

        assert isinstance(chores_log, list)
        assert len(chores_log) == 152
        for chore_log in chores_log:
            assert isinstance(chore_log, ChoreLog)
            assert isinstance(chore_log.id, int)
            assert isinstance(chore_log.chore_id, int)
            assert isinstance(chore_log.tracked_time, datetime)
            assert isinstance(chore_log.done_by, int)
            assert isinstance(chore_log.row_created_timestamp, datetime)
            assert isinstance(chore_log.undone, bool)
            assert isinstance(chore_log.undone_timestamp, (datetime, type(None)))
            assert isinstance(chore_log.skipped, bool)
            assert isinstance(
                chore_log.scheduled_execution_time, (datetime, type(None))
            )
            assert isinstance(chore_log.chore, Chore)
            assert isinstance(chore_log.done_by_user, User)

        chore_log = next(chore_log for chore_log in chores_log if chore_log.id == 6)
        assert chore_log.chore_id == 6
        assert chore_log.done_by == 4
        assert chore_log.done_by_user.id == 4

    @pytest.mark.vcr
    def test_get_chore_log_details(self, grocy):
        chore_log_details = grocy.chores_log.get(3, get_details=True)
        assert isinstance(chore_log_details, ChoreLog)
        assert chore_log_details.id == 3

        assert chore_log_details.chore_id == 3
        assert chore_log_details.chore.id == 3

        assert chore_log_details.done_by == 4
        assert chore_log_details.done_by_user.id == 4

        assert chore_log_details.undone == 0
        assert chore_log_details.undone_timestamp is None
        assert chore_log_details.skipped == 0

    @pytest.mark.vcr
    def test_get_chores_log_filters_valid(self, grocy):
        query_filter = ["undone=1"]
        chores_log = grocy.chores_log.list(get_details=True, query_filters=query_filter)

        for item in chores_log:
            assert item.undone == 1

    @pytest.mark.vcr
    def test_get_chores_log_filters_invalid(self, grocy, invalid_query_filter):
        with pytest.raises(GrocyError) as exc_info:
            grocy.chores_log.list(get_details=True, query_filters=invalid_query_filter)

        error = exc_info.value
        assert error.status_code == 500


def test_get_details_deleted_user_none(mocker):
    """Test that get_details handles deleted users gracefully.
    
    When a chore is done by a deleted user, get_user returns None.
    get_details should set done_by_user to None instead of raising AttributeError.
    Regression test for https://github.com/iamkarlson/grocy-py/issues/22
    """
    from grocy.data_models.chore_log import ChoreLog
    from grocy.data_models.chore import Chore
    from grocy.data_models.user import User
    from datetime import datetime
    
    # Create a ChoreLog with a user that was deleted
    chore_log = ChoreLog(
        id=1,
        chore_id=1,
        tracked_time=datetime.now(),
        done_by=99999,  # deleted user
        row_created_timestamp=datetime.now(),
        undone=False,
        skipped=False,
    )
    
    # Mock api_client
    mock_api = mocker.Mock()
    mock_api.get_userfields.return_value = {}
    
    # Mock get_chore to return a valid chore
    mock_chore = mocker.Mock(spec=Chore)
    mock_api.get_chore.return_value = mock_chore
    
    # Mock get_user to return None (deleted user)
    mock_api.get_user.return_value = None
    
    # This should not raise AttributeError
    chore_log.get_details(mock_api)
    
    # done_by_user should be None
    assert chore_log.done_by_user is None
