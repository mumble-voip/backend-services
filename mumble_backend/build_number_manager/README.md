### Build Number Manager

#### API v1:

Endpoint: ``/build-number/v1/<series>/<commit>?token=<token>``
| HTTP <br> Method| Parameters | Response |
| :-----: | ----- | ---- |
| ``POST`` | ``<series>``: The Mumble series e.g. ``1.4`` <br> ``<commit>``: The commit hash <br> ``<token>``: An authorized password | ``201``: New build number created <br> ``400``: Invalid parameters <br> ``401``: Unauthorized token <br> ``409``: Commit already exists in series <br> ``422``: New build number exceeds 2 bytes |
| ``GET`` | ``<series>``: The Mumble series e.g. ``1.4`` <br> ``<commit>``: The commit hash <br> ``<token>``: An authorized password | ``200``: Found <br> ``400``: Invalid parameters <br> ``401``: Unauthorized token <br> ``404``: Series or build not found |

Returned JSON:
```
{
    "commit_hash": <The commit hash>,
    "series": <The Mumble version series e.g. "1.4.x">,
    "series_id": <The series DB id>,
    "build_number": <The new build number>,
    "series_created": <Series creation datetime>,
    "build_created": <Build number creation datetime>
}
```

---

Endpoint: ``/build-number/v1/<series>?token=<token>``
| HTTP <br> Method| Parameters | Response |
| :-----: | ----- | ---- |
| ``GET`` | ``<series>``: The Mumble series e.g. ``1.4`` <br> ``<token>``: An authorized password | ``200``: Found <br> ``400``: Invalid parameters <br> ``401``: Unauthorized token <br> ``404``: Series not found |

Returned JSON:
```
{
    "series": <The Mumble version series e.g. "1.4.x">,
    "series_id": <The series DB id>,
    "series_created": <Series creation datetime>,
    "builds": <List of all builds>
}
```
Build object:
```
{
    "commit_hash": <The commit hash>,
    "build_number": <The build number>,
    "build_created": <Build number creation datetime>
}
```
