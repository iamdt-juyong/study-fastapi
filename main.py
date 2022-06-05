from fastapi import FastAPI, Path, Query, Body
from enum import Enum
from typing import Union, List, Set, Dict
from pydantic import BaseModel, Field, HttpUrl


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str = Field(example="Foo")
    description: Union[str, None] = Field(
        default=None, title="The description of the item", example="A very nice Item", max_length=300
    )
    price: float = Field(
        gt=0, description="The price must be greater than zero", example=35.4
    )
    tax: Union[float, None] = Field(default=None, example=3.2)
    tags: Set[str] = set()
    # images: Union[List[Image], None] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


class User(BaseModel):
    username: str
    full_name: Union[str, None] = None


class Offer(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    items: List[Item]


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"},
]

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.get("/items2/")
async def read_items(q: List[str] = Query(default=["foo", "bar"])):
    query_items = {"q": q}
    return query_items


@app.get("/items3/")
async def read_items(q: Union[str, None] = Query(
    default=None,
    alias="item-query",
    title="Query string",
    description="Query string for the items to search in the database that have a good match",
    min_length=3,
    max_length=50,
    regex="^fixed-query$",
    deprecated=True,
    include_in_schema=False)
):
    query_items = {"q": q}
    return query_items


@app.get("/items/{item_id}")
async def read_item(item_id: str, q: Union[str, None] = Query(default=None, min_length=3, max_length=50,
                                                              regex="^fixed-query$"), short: bool = False):
    item = {"item_id": item_id}
    if q:
        # return {"item_id": item_id, "q": q}
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.put("/items/{item_id}")
async def create_item(item_id: int, item: Item = Body(embed=True), q: Union[str, None] = None):
    # result = {"item_id": item_id, **item.dict()}
    result = {"item_id": item_id, "item": item}
    if q:
        result.update({"q": q})
    return result


@app.get("/items2/{item_id")
async def read_items(
        item_id: int = Path(title="The ID of the item go get"),
        q: Union[str, None] = Query(default=None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.put("/items2/{item_id}")
async def update_item(
        *,
        item_id: int = Path(title="The ID of the item to get", ge=0, le=1000),
        q: Union[str, None] = None,
        item: Union[Item, None] = None):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results


@app.get("/items3/{item_id")
async def read_items(
        *,
        item_id: int = Path(title="The ID of the item go get",  gt=0, le=1000),
        q: str,
        size: float = Query(gt=0, lt=10.5)):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.put("/items3/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results


@app.put("/items4/{item_id}")
async def update_item(item_id: int, item: Item, user: User, importance: int = Body()):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results


@app.put("/items5/{item_id}")
async def update_item(
        item_id: int,
        item: Item = Body(
            example={
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 4.2,
            },
        ),
):
    results = {"item_id": item_id, "item": item}
    return results


@app.put("/items6/{item_id}")
async def update_item(
        item_id: int,
        item: Item = Body(
            examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 5.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price 'strings' to actual 'numbers' automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },

        ),
):
    results = {"item_id": item_id, "item": item}
    return results


@app.post("/images/multiple")
async def create_multiple_images(*, images: List[Image]):
    return images


@app.post("/index-weights")
async def create_index_weights(weights: Dict[int, float]):
    return weights


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
        user_id: int, item_id: str, q: Union[str, None] = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
