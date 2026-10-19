def image_request_files(uploaded_file):
    """Build a multipart payload containing exactly one uploaded image."""
    return {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type,
        )
    }


def leaf_request_files(uploaded_file):
    """Build the leaf-only prediction payload."""
    return image_request_files(uploaded_file)