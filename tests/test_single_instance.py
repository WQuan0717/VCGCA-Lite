import uuid

from src.utils.single_instance import SingleInstanceChecker


def test_mutex_is_released_and_can_be_acquired_again():
    name = "VCGCA-test-" + uuid.uuid4().hex
    first = SingleInstanceChecker(name)
    second = SingleInstanceChecker(name)
    third = SingleInstanceChecker(name)
    try:
        assert first.is_already_running() is False
        assert second.is_already_running() is True
        first.release()
        assert third.is_already_running() is False
    finally:
        first.release()
        second.release()
        third.release()
