# Loading .map files

def load_map(map_path):
    map = [] # blank map array

    # opens .map file based on the path
    fp = open(map_path, 'r', encoding="UTF8")

    # first line of the file is set as type_octile, just reads that line and prints
    octile_check = fp.readline().replace("\n", "")
    # print is for debugging
    print(f"\nchecking file... : {octile_check}")

    # gets height
    height = fp.readline().split()
    height = int(height[1])

    # gets width
    width = fp.readline().split()
    width = int(width[1])

    # another type
    map_check = fp.readline().replace("\n", "")
    print(f"file type.. : {map_check}\n")
    
    for _ in range(height):
        raw_str = fp.readline().replace("\n", "")
        map.append(list(raw_str))
    
    print(f"map loaded successfully; height = {height}, width = {width}\n")
    
    fp.close()
    return height, width, map

load_map("dao-map/arena.map")