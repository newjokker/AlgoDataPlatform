import gradio as gr
from PIL import Image, ImageDraw
import io

def draw_boxes(image, boxes):
    """
    在图片上画出矩形框。

    参数:
    - image: PIL.Image 对象
    - boxes: 包含矩形框坐标 (左上角 x, 左上角 y, 右下角 x, 右下角 y) 的列表
    """
    draw = ImageDraw.Draw(image)
    for box in boxes:
        draw.rectangle(box, outline="red", width=5)
    return image

def process_image(img, boxes_str):
    """
    处理图像并画出框。

    参数:
    - img: PIL.Image 对象
    - boxes_str: 包含矩形框坐标的字符串，例如 '100,100,200,200;150,150,250,250'
    """
    boxes = [list(map(int, box.split(','))) for box in boxes_str.split(';')]
    return draw_boxes(img, boxes)

iface = gr.Interface(
    fn=process_image,
    inputs=[
        gr.Image(type='pil', label="上传图片"),
        gr.Textbox(lines=1, placeholder="输入框的位置, 例如: 100,100,200,200;150,150,250,250", label="框的位置")
    ],
    outputs=gr.Image(type='pil', label="处理后的图片"),
    title="在图片上画框",
    description="上传一张图片，并输入框的位置，将在图片上画出这些框。",
    article="<p>输入框的位置格式为: 左上角 x, 左上角 y, 右下角 x, 右下角 y</p>"
)

iface.launch(server_name="0.0.0.0")

