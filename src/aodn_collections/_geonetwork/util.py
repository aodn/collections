"""
Requires group `dev`

`uv sync --group dev`
"""

import owslib.csw


def csw_record_to_json(record):
    return {
        "identifier": record.identifier,
        "title": record.title,
        "abstract": record.abstract,
        "type": record.type,
        "subjects": record.subjects,
        "format": record.format,
        "creator": record.creator,
        "publisher": record.publisher,
        "language": record.language,
        "rights": record.rights,
        "source": record.source,
        "relation": record.relation,
        "modified": record.modified,
        "date": record.date,
        "references": record.references,
        # Convert the complex BoundingBox object into readable JSON coordinates
        "bbox": {
            "minx": record.bbox.minx,
            "miny": record.bbox.miny,
            "maxx": record.bbox.maxx,
            "maxy": record.bbox.maxy,
            "crs": str(record.bbox.crs) if record.bbox.crs else None,
        }
        if record.bbox
        else None,
    }


def get_imos_collection_csw_record(
    metadata_uuids: str | list[str],
    chunk_size: int = 20,
) -> dict[str, owslib.csw.CswRecord | None]:
    """
    Retrieves titles for a list of IMOS metadata UUIDs in optimized batches.

    Args:
        metadata_uuids (list): A list of metadata UUID strings.
        chunk_size (int): Number of UUIDs to query per request (default: 20).

    Returns:
        dict: A dictionary mapping each UUID to its title (or None if not found).
    """
    csw_url = "https://catalogue-imos.aodn.org.au/geonetwork/srv/eng/csw"
    results = {}

    # Resolve single string input
    metadata_uuids = (
        [metadata_uuids] if isinstance(metadata_uuids, str) else metadata_uuids
    )

    try:
        # Initialize the CSW client once outside the loop
        csw = owslib.csw.CatalogueServiceWeb(csw_url, version="2.0.2")

        # Process the UUIDs in chunks
        for i in range(0, len(metadata_uuids), chunk_size):
            chunk = metadata_uuids[i : i + chunk_size]

            # Request multiple records at once
            csw.getrecordbyid(id=chunk)

            # Map the results from the response dictionary
            for uuid in chunk:
                if uuid in csw.records:
                    results[uuid] = csw.records[uuid]
                else:
                    results[uuid] = None

    except Exception as e:  # noqa
        print(f"An error occurred during bulk CSW retrieval: {e}")

    return results
