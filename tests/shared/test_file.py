from src.shared.file import (
    check_file,
    check_folder,
    is_json,
    read_json,
    remove_file,
    remove_folder,
    save_json,
)


def test_is_json():
    """Check if the target is json based on the file extension in the path."""
    assert is_json("test.json")
    assert not is_json("test.txt")


TEST_FOLDER_PATH = "output/file_test"


class TestSaveReadJsonRemoveCheckFile:
    def test_save_json(self):
        """Should save data to file and readable by read_json."""
        file_path = f"{TEST_FOLDER_PATH}/1.json"
        data = {"test": "yes"}
        save_json(file_path, data)
        assert read_json(file_path) == data
        assert check_file(file_path)
        remove_file(file_path)
        assert not check_file(file_path)

    def test_sort_keys(self):
        """Should save data to file and readable by read_json."""
        file_path = f"{TEST_FOLDER_PATH}/2.json"
        data = {"2": "bar", "1": "foo"}
        assert next(iter(data)) == "2"
        save_json(file_path, data, sort_keys=True)
        result = read_json(file_path)
        assert next(iter(result)) == "1"

        remove_file(file_path)


def test_remove_folder():
    """Should remove a folder."""
    assert check_folder(TEST_FOLDER_PATH)
    remove_folder(TEST_FOLDER_PATH)
    assert not check_folder(TEST_FOLDER_PATH)
