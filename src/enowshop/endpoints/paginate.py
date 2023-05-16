from pydantic import BaseModel


def paginate(result, offset: int, total: int) -> dict:
    return {
        'data': result,
        'total': total,
        'offset': offset,
        'count': len(result)
    }