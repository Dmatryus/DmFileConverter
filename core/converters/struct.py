from .base import Converter

from pathlib import Path
from typing import Optional


class OpmToTxtConverter(Converter):
    """
    Converter for converting OPML files to TXT format.
    """

    _supported_formats: dict[str, tuple[str]] = {"input": ("opml",), "output": ("txt",)}

    def __repr__(self) -> str:
        return "OPML to TXT Converter"

    def convert_function(
        self, source_path: Path, output_path: Path, target_format: Optional[str] = None
    ):
        """
        Конвертирует содержимое OPML в формат TXT.
        """
        import xml.etree.ElementTree as ET

        def traverse_outline(element, level=1):
            text = element.get("text", "")
            line = f"{'    ' * (level - 1)}{text}"

            if element.get("type"):
                line += f" [{element.get('type')}]"

            output_lines.append(line)

            for child in element.findall("outline"):
                traverse_outline(child, level + 1)

        with open(source_path, "r", encoding="utf-8") as file:
            opml_content = file.read()

        root = ET.fromstring(opml_content)

        title = (
            root.find(".//title").text
            if root.find(".//title") is not None
            else "Untitled"
        )

        output = f"::title {title}\n\n"

        output_lines = []
        traverse_outline(root.find(".//body"), level=0)

        content = output + "\n".join(output_lines)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(content)


class TxtToOpmConverter(Converter):
    """
    Converter for converting TXT files to OPML format.
    """

    _supported_formats: dict[str, tuple[str]] = {"input": ("txt",), "output": ("opml",)}

    def __repr__(self) -> str:
        return "TXT to OPML Converter"

    def convert_function(
        self, source_path: Path, output_path: Path, target_format: Optional[str] = None
    ):
        """
        Конвертирует содержимое TXT в формат OPML.
        """
        import xml.etree.ElementTree as ET

        def build_outline(parent, level=0):
            while lines:
                current_line = lines[0]

                if current_line.startswith("::"):
                    text = current_line.split("::")[1].strip()
                    new_element = ET.SubElement(parent, "outline", text=text)
                    build_outline(new_element, level + 1)
                else:
                    break

                lines.pop(0)

        with open(source_path, "r", encoding="utf-8") as file:
            mm_content = file.read()

        lines = [line.strip() for line in mm_content.splitlines() if line.strip()]

        title = "Untitled"
        if lines and lines[0].startswith("::title"):
            title = lines[0].split("::title ")[1]
            lines = lines[1:]

        root = ET.Element("opml", version="1.0")
        head = ET.SubElement(root, "head")
        body = ET.SubElement(root, "body")

        title_element = ET.SubElement(head, "title")
        title_element.text = title

        build_outline(body)

        content = ET.tostring(root, encoding="utf-8", method="xml").decode()

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(content)


class OpmlToMmConverter(Converter):
    _supported_formats = {"input": ("opml",), "output": ("mm",)}

    def convert_function(
        self, source_path: Path, output_path: Path, target_format: Optional[str] = None
    ):
        import uuid
        from lxml import etree

        # Создаем корень FreeMind
        freemind = etree.Element("map", version="1.0")
        root_node = etree.SubElement(freemind, "node", ID=str(uuid.uuid4()), TEXT="")

        # Парсим OPML файл
        opml_tree = etree.parse(source_path)
        opml_root = opml_tree.getroot()

        def process_outline(outline_element, parent_node):
            """Рекурсивно обрабатываем каждый outline и создаем node в FreeMind."""
            # Генерируем уникальный ID
            node_id = str(uuid.uuid4())

            # Создаем новый узел
            new_node = etree.SubElement(parent_node, "node", ID=node_id)

            # Устанавливаем текст узла
            text = outline_element.get("text", "")
            if text:
                new_node.set("TEXT", text)

            # Определяем стиль на основе типа (например, для rss используем rectangle)
            type_attr = outline_element.get("type")
            style = "rectangle" if type_attr == "rss" else "fork"
            new_node.set("STYLE", style)

            # Устанавливаем позицию
            new_node.set("POSITION", "right")

            # Обрабатываем подузлы
            for child in outline_element:
                if child.tag == "outline":
                    process_outline(child, new_node)

        # Начинаем с корневого outline
        for outline_child in opml_root.find("body"):
            if outline_child.tag == "outline":
                process_outline(outline_child, root_node)

        with open(output_path, "wb") as f:
            f.write(etree.tostring(freemind, encoding="utf-8", pretty_print=True))


class MmToOpmlConverter(Converter):
    _supported_formats = {"input": ("mm",), "output": ("opml",)}

    def convert_function(
        self, source_path: Path, output_path: Path, target_format: Optional[str] = None
    ):
        from lxml import etree
        import uuid

        def traverse_freemind_node(freemind_node, parent_outline):
            # Create an outline element for the current FreeMind node
            outline = etree.SubElement(parent_outline, "outline")

            # Set the text attribute from FreeMind's TEXT property
            if "TEXT" in freemind_node.attrib:
                outline.set("text", freemind_node.attrib["TEXT"])

            # Optionally set type based on FreeMind's STYLE (if needed)
            style = freemind_node.get("STYLE", "")
            if style == "rectangle":
                outline.set("type", "rss")

            # Recursively process child nodes
            for child in freemind_node:
                traverse_freemind_node(child, outline)

        # Parse the FreeMind file
        freemind_tree = etree.parse(source_path)
        root = freemind_tree.getroot()

        # Create the OPML structure
        opml = etree.Element("opml", version="1.0")
        head = etree.SubElement(opml, "head")
        body = etree.SubElement(opml, "body")

        # Process the root node's children and add them to OPML body
        for child in root[0]:
            traverse_freemind_node(child, body)

        etree.indent(opml, space="    ")

        # Write to file
        with open(output_path, "wb") as f:
            f.write(etree.tostring(opml, encoding="utf-8", xml_declaration=True))
