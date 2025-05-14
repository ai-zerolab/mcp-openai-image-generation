import base64
import os
import uuid
from pathlib import Path
from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent
from openai import OpenAI
from pydantic import Field

mcp = FastMCP("openai-image-generation")
client = OpenAI()
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-image-1")


@mcp.tool(
    description="Generate an image with OpenAI model, save or display it. "
    "For saving, use the `output_dir` parameter."
)
def generate_image(
    prompt: Annotated[str, Field(description="A text description of the desired image(s).")],
    background: Annotated[
        str | None,
        Field(
            description="Allows to set transparency for the background of the generated image(s). "
            "This parameter is only supported for `gpt-image-1`. "
            "Must be one of `transparent`, `opaque` or `auto` (default value). "
            "When `auto` is used, the model will automatically determine the best background for the image.",
        ),
    ] = None,
    n: Annotated[
        int | None,
        Field(
            description="The number of images to generate. Must be between 1 and 10. For `dall-e-3`, "
            "only `n=1` is supported.",
        ),
    ] = 1,
    quality: Annotated[
        str | None,
        Field(
            description="""The quality of the image that will be generated.

- `auto` (default value) will automatically select the best quality for the given model.
- `high`, `medium` and `low` are supported for `gpt-image-1`.
- `hd` and `standard` are supported for `dall-e-3`.
- `standard` is the only option for `dall-e-2`.
"""
        ),
    ] = "auto",
    model: Annotated[
        str,
        Field(
            description='Should be one of ["dall-e-2", "dall-e-3", "gpt-image-1"]',
        ),
    ] = DEFAULT_MODEL,
    output_format: Annotated[
        str,
        Field(
            description="The format in which the generated images are returned. "
            "This parameter is only supported for `gpt-image-1`. Must be one of `png`, `jpeg`, or `webp`.",
        ),
    ] = "png",
    size: Annotated[
        str,
        Field(
            description="The size of the generated images. "
            "Must be one of `1024x1024`, `1536x1024` (landscape), "
            "`1024x1536` (portrait), or `auto` (default value) for `gpt-image-1`, "
            "one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`, "
            "and one of `1024x1024`, `1792x1024`, or `1024x1792` for `dall-e-3`.",
        ),
    ] = "auto",
    output_dir: Annotated[
        str | None,
        Field(
            description="The directory to save the generated image(s). If not provided, the image(s) will be displayed.",
        ),
    ] = None,
) -> ImageContent | list[ImageContent] | dict:
    response = client.images.generate(
        prompt=prompt,
        background=background,
        n=n,
        quality=quality,
        model=model,
        output_format=output_format,
        size=size,
    )
    if not response.data:
        return {"generated_images": [], "message": "No images generated"}

    case_id = uuid.uuid4().hex
    result = []
    for count, image in enumerate(response.data):
        image_base64 = image.b64_json
        if output_dir:
            image_bytes = base64.b64decode(image_base64)
            output_dir: Path = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{case_id}-{count}.{output_format}"
            output_path.write_bytes(image_bytes)
            result.append(output_path.absolute().as_posix())
        else:
            result.append(
                ImageContent(
                    type="image",
                    data=image_base64,
                    mimeType=f"image/{output_format}",
                    annotations={"case_id": case_id, "count": count, "prompt": prompt},
                )
            )
    if len(result) == 1:
        result = result[0]
    return {"generated_images": result} if output_dir else result


# TODO: Edit, inpainting,


@mcp.tool(
    description="Edit an image with OpenAI model, save or display it. "
    "For saving, use the `output_dir` parameter."
    "You can use one or more images as a reference to generate a new image, "
    "or edit an image using a mask(inpainting). "
    "For inpainting, if you provide multiple input images, the `mask` will be applied to the first image."
)
def edit_image(
    prompt: Annotated[
        str,
        Field(
            description="The prompt to generate the image.",
        ),
    ],
    images: Annotated[
        list[str],
        Field(
            description="The image(s) to edit. Must be a supported image file or an array of images. Use absolute paths.",
        ),
    ],
    mask: Annotated[
        str | None,
        Field(
            description="The mask to apply to the image(s). Must be a supported image file. Use absolute paths.",
        ),
    ] = None,
    background: Annotated[
        str | None,
        Field(
            description="Allows to set transparency for the background of the generated image(s). "
            "This parameter is only supported for `gpt-image-1`. "
            "Must be one of `transparent`, `opaque` or `auto` (default value). "
            "When `auto` is used, the model will automatically determine the best background for the image.",
        ),
    ] = None,
    n: Annotated[
        int | None,
        Field(
            description="The number of images to generate. Must be between 1 and 10. For `dall-e-3`, "
            "only `n=1` is supported.",
        ),
    ] = 1,
    quality: Annotated[
        str | None,
        Field(
            description="""The quality of the image that will be generated.

- `auto` (default value) will automatically select the best quality for the given model.
- `high`, `medium` and `low` are supported for `gpt-image-1`.
- `hd` and `standard` are supported for `dall-e-3`.
- `standard` is the only option for `dall-e-2`.
"""
        ),
    ] = "auto",
    model: Annotated[
        str,
        Field(
            description='Should be one of ["dall-e-2", "dall-e-3", "gpt-image-1"]',
        ),
    ] = DEFAULT_MODEL,
    output_format: Annotated[
        str,
        Field(
            description="The format in which the generated images are returned. "
            "This parameter is only supported for `gpt-image-1`. Must be one of `png`, `jpeg`, or `webp`.",
        ),
    ] = "png",
    size: Annotated[
        str,
        Field(
            description="The size of the generated images. "
            "Must be one of `1024x1024`, `1536x1024` (landscape), "
            "`1024x1536` (portrait), or `auto` (default value) for `gpt-image-1`, "
            "one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`, "
            "and one of `1024x1024`, `1792x1024`, or `1024x1792` for `dall-e-3`.",
        ),
    ] = "auto",
    output_dir: Annotated[
        str | None,
        Field(
            description="The directory to save the generated images. "
            "If not provided, the generated images will be returned as a list of ImageContent objects.",
        ),
    ] = None,
) -> list[ImageContent] | ImageContent | dict:
    images = [open(image, "rb") for image in images]  # noqa: SIM115
    mask = open(mask, "rb") if mask else None  # noqa: SIM115
    response = client.images.edit(
        image=images,
        prompt=prompt,
        background=background,
        mask=mask,
        quality=quality,
        model=model,
        n=n,
        response_format=output_format,
        size=size,
    )

    if not response.data:
        return {"generated_images": [], "message": "No images generated"}

    case_id = uuid.uuid4().hex
    result = []
    for count, image in enumerate(response.data):
        image_base64 = image.b64_json
        if output_dir:
            image_bytes = base64.b64decode(image_base64)
            output_dir: Path = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{case_id}-{count}.{output_format}"
            output_path.write_bytes(image_bytes)
            result.append(output_path.absolute().as_posix())
        else:
            result.append(
                ImageContent(
                    type="image",
                    data=image_base64,
                    mimeType=f"image/{output_format}",
                    annotations={"case_id": case_id, "count": count, "prompt": prompt},
                )
            )
    if len(result) == 1:
        result = result[0]
    return {"generated_images": result} if output_dir else result
