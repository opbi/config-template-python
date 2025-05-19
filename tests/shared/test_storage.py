import pytest

from src.shared import file, storage
from src.shared.storage import with_container_setup_teardown

JSON_DATA = {"beef": 1, "lamb": 1}
JSON_STORAGE_PATH = "tests/shared/storage/test.json"

TEXT_DATA = "Here is the order."
TEXT_STORAGE_PATH = "tests/shared/storage/test.txt"

JSON_UPLOAD_PATH = "tests/__fixtures__/order.json"
JSON_NESTED_STORAGE_PATH = "tests/shared/storage/nested/test.json"

FOLDER_UPLOAD_PATH = "tests/__fixtures__/folder"
FOLDER_NESTED_STORAGE_PATH = "tests/shared/storage/nested_folder/folder"


@pytest.mark.online
def test_with_container_setup_teardown():
    """Should provide container configurable from ENV_VARS."""

    @with_container_setup_teardown
    def check_name(container):
        return container.container_name

    assert check_name() == "config-template-python"
    assert check_name(container_name="custom") == "custom"


@pytest.mark.online
class TestSaveReadCheckRemoveFile:
    def test_save_read_json(self):
        """Should save (overwrite) and read json."""
        storage.save_file(JSON_STORAGE_PATH, {"foo": "bar"}, cache_client=True)
        storage.save_file(JSON_STORAGE_PATH, JSON_DATA, cache_client=True)
        assert storage.check_file(JSON_STORAGE_PATH, cache_client=True)

        content = storage.read_file(JSON_STORAGE_PATH)
        assert content == JSON_DATA

        storage.remove(JSON_STORAGE_PATH, cache_client=True)
        assert not storage.check_file(JSON_STORAGE_PATH)

    def test_save_read_txt(self):
        """Should save (overwrite) and read text."""
        storage.save_file(TEXT_STORAGE_PATH, "random-text", cache_client=True)
        storage.save_file(TEXT_STORAGE_PATH, TEXT_DATA, cache_client=True)

        content = storage.read_file(TEXT_STORAGE_PATH)
        assert content == TEXT_DATA


@pytest.mark.online
class TestUploadFile:
    def test_upload_same_path(self):
        """Should upload to the same file path if storage path not set."""
        storage.upload_file(JSON_UPLOAD_PATH, cache_client=True)
        assert storage.check_file(JSON_UPLOAD_PATH, cache_client=True)

        storage.remove(JSON_UPLOAD_PATH, cache_client=True)

    def test_upload_different_path(self):
        """Should upload file to the set storage path."""
        storage.upload_file(JSON_UPLOAD_PATH, JSON_STORAGE_PATH, cache_client=True)
        assert storage.check_file(JSON_STORAGE_PATH, cache_client=True)

        storage.remove(JSON_STORAGE_PATH, cache_client=True)

    def test_upload_to_nested_path(self):
        """Should created the nested folder and upload the file there."""
        storage.upload_file(JSON_UPLOAD_PATH, JSON_NESTED_STORAGE_PATH, cache_client=True)
        assert storage.check_file(JSON_NESTED_STORAGE_PATH, cache_client=True)

        storage.remove(JSON_NESTED_STORAGE_PATH)


@pytest.mark.online
class TestUploadFolderCheckRemoveFolder:
    def test_upload_same_path(self):
        """Should upload to the same path as local folder path."""
        storage.upload_folder(FOLDER_UPLOAD_PATH, cache_client=True)
        assert storage.check_folder(FOLDER_UPLOAD_PATH, cache_client=True)
        # the files inside the folder should be uploaded
        assert storage.check_file(f"{FOLDER_UPLOAD_PATH}/1.txt", cache_client=True)
        assert storage.check_file(f"{FOLDER_UPLOAD_PATH}/2.txt", cache_client=True)

        storage.remove(FOLDER_UPLOAD_PATH, cache_client=True)
        assert not storage.check_folder(FOLDER_UPLOAD_PATH)

    def test_upload_to_nested_folder(self):
        """Should upload folder to path."""
        storage.upload_folder(FOLDER_UPLOAD_PATH, FOLDER_NESTED_STORAGE_PATH, cache_client=True)
        assert storage.check_folder(FOLDER_NESTED_STORAGE_PATH, cache_client=True)
        assert storage.check_file(f"{FOLDER_NESTED_STORAGE_PATH}/1.txt", cache_client=True)
        assert storage.check_file(f"{FOLDER_NESTED_STORAGE_PATH}/2.txt", cache_client=True)

        storage.remove(FOLDER_NESTED_STORAGE_PATH, cache_client=True)
        assert not storage.check_folder(FOLDER_NESTED_STORAGE_PATH)

    def test_upload_non_exist_folder(self):
        """Should do nothing if folder doesn't exist."""
        non_exist_folder = "tests/__fixtures__/non-exist-folder"
        storage.upload_folder(non_exist_folder, cache_client=True)
        assert not storage.check_folder(non_exist_folder)


@pytest.mark.online
class TestDownload:
    def test_download_file(self):
        """Should download the file."""
        storage.upload_file(JSON_UPLOAD_PATH, JSON_NESTED_STORAGE_PATH, cache_client=True)
        assert storage.check_file(JSON_NESTED_STORAGE_PATH, cache_client=True)

        file_path = f"output/{JSON_NESTED_STORAGE_PATH}"
        storage.download_file(JSON_NESTED_STORAGE_PATH, file_path, cache_client=True)

        data = file.read_json(file_path)
        assert data == JSON_DATA

        file.remove_file(file_path)
        storage.remove(JSON_NESTED_STORAGE_PATH)

    def test_download_folder_to_nested_folder(self):
        """Should download the folder."""
        storage.upload_folder(FOLDER_UPLOAD_PATH, cache_client=True)
        assert storage.check_folder(FOLDER_UPLOAD_PATH, cache_client=True)

        storage.download_folder(FOLDER_UPLOAD_PATH, "output/download_folder_test")
        assert file.check_file("output/download_folder_test/1.txt")
        assert file.check_file("output/download_folder_test/2.txt")
        assert file.check_file("output/download_folder_test/nested_folder/1.json")

        storage.remove(FOLDER_UPLOAD_PATH)
        file.remove_folder("output/download_folder_test")


@pytest.mark.online
class TestEmptyBehaviour:
    def check_file_non_exist_container(self):
        """Should return False if the container is not found."""
        assert not storage.check_file(JSON_STORAGE_PATH, container_name="wrong-container")

    def test_remove_file_and_empty_folder(self):
        """Should remove the folder as well if it becomes empty."""
        storage.upload_file(JSON_NESTED_STORAGE_PATH)
        storage.remove(JSON_NESTED_STORAGE_PATH)
        assert not storage.check_folder("tests/shared/azure/nested/")

    def test_remove_non_exist_folder(self):
        """Should remove folder."""
        storage.remove("unknown_folder/")
