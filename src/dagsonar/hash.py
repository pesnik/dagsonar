import hashlib
import json


def compute_hash(reference) -> str:
    """Compute a SHA-256 hash of a given object."""
    reference_dict = reference.__dict__.copy()
    reference_dict.pop("hash", None)
    json_str = json.dumps(reference_dict, default=str, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()
