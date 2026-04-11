from graph import Graph, Zone

VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}


def parse_error(line_no: int, message: str) -> ValueError:
    """Return the maximum number of drones allowed on a connection."""
    return ValueError(f"Line {line_no}: {message}")


def split_metadata(line: str, line_no: int) -> tuple[str, str | None]:
    """
    Split a line into its main statement and optional metadata block.

    Returns:
        A tuple of (main_part, metadata_part).
        metadata_part is None if no [...] block exists.
    """
    open_count = line.count("[")
    close_count = line.count("]")

    # no metadata
    if open_count == 0 and close_count == 0:
        return line.strip(), None

    # must be 1 []
    if open_count != 1 or close_count != 1:
        raise parse_error(line_no, "meta must contain exactly one [...]block")

    open_index = line.index("[")
    close_index = line.index("]")

    # [] sequence correct
    if close_index < open_index:
        raise parse_error(line_no, "invalid metadata order")

    # after metadata no extra content
    after = line[close_index + 1:].strip()
    if after:
        raise parse_error(line_no,
                          "metadata must appear at the end of the line")
    main_part = line[:open_index].strip()
    meta_part = line[open_index: close_index + 1].strip()

    # must have main part
    if not main_part:
        raise parse_error(line_no, "missing statement before metadata")

    return main_part, meta_part


def parse_metadata(meta: str, line_no: int) -> dict[str, str]:
    """
    Parse a metadata blcok
    Input:
    "[zone=restricted max_drones=2]"
    Output:
    {"zone": "restricted", "max_drones": "2"}
    """

    # defensive double check
    if not (meta.startswith("[") and meta.endswith("]")):
        raise parse_error(line_no, "invalid metadata block")

    result: dict[str, str] = {}
    content = meta[1:-1]

    if not content:
        return result

    # split based on space
    parts: list[str] = content.split()

    for part in parts:
        if "=" not in part:
            raise parse_error(line_no, f"invalid metadata entry: {part}")

        k, v = part.split("=", 1)
        if not k or not v:
            raise parse_error(line_no, f"invalid metadata entry: {part}")
        if k in result:
            raise parse_error(line_no, f"duplicate metadata key: {k}")
        result[k] = v
    return result


def validate_zone_name(name: str, line_no: int) -> None:  # connection 用 "-" 分割
    """Validate a zone name."""
    if "-" in name or " " in name:
        raise parse_error(line_no, f"invalid zone name: {name}")


def parse_positive_int(value: str, field: str, line_no: int) -> int:  # field?
    """Parse a strictly positive integer field."""
    try:
        number = int(value)
    except ValueError as exc:
        raise parse_error(line_no, f"{field} must be an integer") from exc

    if number <= 0:
        raise parse_error(line_no, f"{field} must be a positive integer")
    return number


def parse_coordinate(value: str, field: str, line_no: int) -> int:
    """Parse a coordinate as an integer."""
    try:
        return int(value)
    except ValueError as exc:
        raise parse_error(line_no, f"{field} must be an integer") from exc


def parse_file(filename: str) -> tuple[int, Graph]:
    """
    Parse a Fly_in map file.

    Returns:
        A tuple of (nb_drones, graph).
    """

    graph = Graph()
    nb_drones: int | None = None  # 初始状态（还没解析）

    seen_names: set[str] = set()
    seen_start = False
    seen_end = False

    with open(filename, "r", encoding="utf-8") as f:

        for line_no, raw_line in enumerate(f, start=1):
            # enumerate 内置函数，它会为可迭代对象（如文件对象 f）中的每个元素生成一个索引和元素本身。
            # 默认索引从 0 开始，但可以通过 start 参数指定起始值。
            line = raw_line.strip()

            # jump over empty line & notes
            if not line or line.startswith("#"):
                continue

            # drones check: nb_drones: 2
            if line.startswith("nb_drones:"):
                if nb_drones is not None:  # it must be none at the beginning
                    raise parse_error(line_no,
                                      "duplicate nb_drones definition")
                value = line.split(":", 1)[1].strip()  # slice only once
                nb_drones = parse_positive_int(value, "nb_drones", line_no)
                continue
            if nb_drones is None:
                raise parse_error(line_no,
                                  "nb_drones must be defined "
                                  "before other entries")

            # zone check: start_hub: start 0 0
            if (
                line.startswith("start_hub:")
                or line.startswith("end_hub:")
                or line.startswith("hub:")
            ):
                main_part, meta_part = split_metadata(line, line_no)
                parts = main_part.split()
                if len(parts) != 4:
                    raise parse_error(line_no, "invalid zone definition")
                prefix = parts[0]
                name = parts[1]

                validate_zone_name(name, line_no)

                if name in seen_names:
                    raise parse_error(line_no, f"duplicate zone name: {name}")
                x = parse_coordinate(parts[2], "x", line_no)
                y = parse_coordinate(parts[3], "y", line_no)

                # zone metadata check: [zone=restricted]
                zone_type = "normal"
                max_drones = 1
                color = None

                if meta_part is not None:
                    metadata = parse_metadata(meta_part, line_no)
                    for key in metadata:
                        if key not in {"zone", "max_drones", "color"}:
                            raise parse_error(line_no,
                                              f"invalid metadata"
                                              f"key for zone: {key}")

                    if "zone" in metadata:
                        zone_type = metadata["zone"]
                        if zone_type not in VALID_ZONE_TYPES:
                            raise parse_error(line_no,
                                              f"invalid zone"
                                              f"type: {zone_type}")

                    if "max_drones" in metadata:
                        max_drones = parse_positive_int(
                            metadata["max_drones"], "max_drones", line_no
                        )

                    if "color" in metadata:
                        color = metadata["color"]

                zone = Zone(name, x, y, zone_type, max_drones, color)
                graph.add_zone(zone)
                seen_names.add(name)

                # start/end uniquity check
                if prefix == "start_hub:":
                    if seen_start:
                        raise parse_error(line_no, "duplicate start_hub")
                    graph.start = name
                    seen_start = True

                elif prefix == "end_hub:":
                    if seen_end:
                        raise parse_error(line_no, "duplicate end_hub")
                    graph.end = name
                    seen_end = True

                continue

            # connection check: connection: start-a
            if line.startswith("connection"):
                main_part, meta_part = split_metadata(line, line_no)
                parts = main_part.split()

                if len(parts) != 2:
                    raise parse_error(line_no,
                                      "invalid connection definition")
                if "-" not in parts[1]:
                    raise parse_error(line_no,
                                      "connection must use "
                                      "zone1-zone2 format")
                z1, z2 = parts[1].split("-", 1)

                if z1 not in graph.zones:
                    raise parse_error(line_no,
                                      f"unknown zone in connection: {z1}")
                if z2 not in graph.zones:
                    raise parse_error(line_no,
                                      f"unknown zone in connection: {z2}")

                capacity = 1

                # connection metadata check
                if meta_part is not None:
                    metadata = parse_metadata(meta_part, line_no)

                    for key in metadata:  # keep the same structure as Zone
                        if key != "max_link_capacity":
                            raise parse_error(
                                line_no, f"invalid metadata"
                                f"key for connection: {key}"
                            )
                    if "max_link_capacity" in metadata:
                        capacity = parse_positive_int(
                            metadata["max_link_capacity"],
                            "max_link_capacity",
                            line_no,
                        )

                graph.add_connection(z1, z2, capacity)
                continue
            #  unknown syntax: other unmeaningful cases e.g. room 1-2-3
            # 这一行已经检查完所有合法语法了，还是不匹配，那就报错
            raise parse_error(line_no, f"unknown statement: {line}")

            # final check
        if nb_drones is None:  # defensive, the whole text is empty
            raise ValueError("Missing nb_drones definition")
        if not seen_start:
            raise ValueError("Missing start_hub definition")
        if not seen_end:
            raise ValueError("Missing end_hub definition")

        return nb_drones, graph

# parse_file(filename) 做的事情是：

# 创建一个空 Graph

# 逐行读地图文件

# 跳过空行和注释

# 读到 nb_drones 就保存无人机数量

# 读到 start_hub / end_hub / hub 就创建 Zone

# 读到 connection 就添加连接

# 最后返回 (nb_drones, graph)

# [testmain]???
