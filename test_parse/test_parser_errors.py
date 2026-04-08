from parser import parse_file

files = [
    "bad_dup_start.txt",
    "bad_dup_end.txt",
    "bad_zone_name.txt",
    "bad_zone_type.txt",
    "bad_max_drones.txt",
    "bad_dup_connection.txt",
    "bad_unknownzone_connection.txt",
    "bad_metadata.txt",
]

for filename in files:
    print(f"\n=== Testing {filename} ===")
    try:
        parse_file(filename)
        print("ERROR: should have failed, but passed")
    except Exception as e:
        print("Caught:", e)
