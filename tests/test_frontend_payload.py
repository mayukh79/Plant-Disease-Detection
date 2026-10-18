from types import SimpleNamespace

from src.utils.uploads import (
    image_request_files,
    leaf_request_files,
)


def test_image_payload_contains_only_one_image():
    image = SimpleNamespace(
        name="plant-part.jpg",
        type="image/jpeg",
        getvalue=lambda: b"plant-part-image",
    )

    files = image_request_files(image)

    assert files == {
        "file": ("plant-part.jpg", b"plant-part-image", "image/jpeg")
    }


def test_leaf_prediction_payload_contains_only_leaf():
    leaf = SimpleNamespace(
        name="leaf.jpg",
        type="image/jpeg",
        getvalue=lambda: b"leaf-image",
    )

    assert leaf_request_files(leaf) == {
        "file": ("leaf.jpg", b"leaf-image", "image/jpeg")
    }
