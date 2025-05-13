import base64
import uuid
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.types import ImageContent
from openai import OpenAI
from pydantic import Field

mcp = FastMCP("openai-image-generation")
client = OpenAI()


@mcp.tool(
    description="Generate an image with OpenAI model, save or display it. "
    "For saving, use the `output_dir` parameter."
)
def generate_image(
    prompt: str = Field(..., description=""),
    background: str | None = Field(
        None,
        description="Allows to set transparency for the background of the generated image(s). "
        "This parameter is only supported for `gpt-image-1`. "
        "Must be one of `transparent`, `opaque` or `auto` (default value). "
        "When `auto` is used, the model will automatically determine the best background for the image.",
    ),
    n: int | None = Field(
        1,
        description="The number of images to generate. Must be between 1 and 10. For `dall-e-3`, "
        "only `n=1` is supported.",
    ),
    model: str | None = Field(
        "gpt-image-1",
        description='Must be one of ["dall-e-2", "dall-e-3", "gpt-image-1"]',
    ),
    output_format: str | None = Field(
        "png",
        description="The format in which the generated images are returned. "
        "This parameter is only supported for `gpt-image-1`. Must be one of `png`, `jpeg`, or `webp`.",
    ),
    size: str | None = Field(
        "auto",
        description="The size of the generated images. "
        "Must be one of `1024x1024`, `1536x1024` (landscape), "
        "`1024x1536` (portrait), or `auto` (default value) for `gpt-image-1`, "
        "one of `256x256`, `512x512`, or `1024x1024` for `dall-e-2`, "
        "and one of `1024x1024`, `1792x1024`, or `1024x1792` for `dall-e-3`.",
    ),
    output_dir: str | None = Field(
        None,
        description="The directory to save the generated image(s). If not provided, the image(s) will be displayed.",
    ),
) -> list[ImageContent] | dict:
    result = client.images.generate(
        prompt=prompt,
        background=background,
        model=model,
        output_format=output_format,
        size=size,
    )
    case_id = uuid.uuid4().hex
    result = []
    for count, image in enumerate(result.data):
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
                    data=image_base64,
                    mimeType=f"image/{output_format}",
                    annotations={"case_id": case_id, "count": count, "prompt": prompt},
                )
            )
    return result if output_dir else {"generated_images": result}
