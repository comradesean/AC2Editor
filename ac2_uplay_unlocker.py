#!/usr/bin/env python3
"""
AC2 Assassin's Creed II uPlay Rewards Unlocker
===============================================

A tool for toggling DLC unlocks in AC2 OPTIONS files.
Supports both PC and PS3 formats with a console UI.

Usage:
    python ac2_uplay_unlocker.py OPTIONS
    python ac2_uplay_unlocker.py OPTIONS.PS3
"""

import sys
import os
import struct

try:
    import curses
    HAS_CURSES = True
except ImportError:
    HAS_CURSES = False

# =============================================================================
# CONSTANTS
# =============================================================================

PS3_FILE_SIZE = 4096  # Typical PS3 OPTIONS file size (may vary)

# =============================================================================
# UNLOCK DEFINITIONS
# =============================================================================

# Standard boolean unlocks (18-byte structure: type + hash + 8 zeros + 0B + value)
# Structure: 0E 00 00 00 [HASH:4] 00 00 00 00 00 00 00 00 0B [VALUE]
BOOL_UNLOCKS = [
    # Templar Lairs / Exclusive Maps
    (0x41027E09, "Palazzo Medici - Home Invasion", "TEMPLAR LAIRS"),
    (0x788F42CC, "Santa Maria Dei Frari - Over Beams, Under Stone", "TEMPLAR LAIRS"),
    (0x6FF4568F, "Arsenal Shipyard - Shipwrecked", "TEMPLAR LAIRS"),

    # Uplay Rewards
    (0x1854EC5A, "Bonus Skin (Verizon Promotion)", "PROMOTIONAL"),
    (0xC25CE923, "Additional Throwing Knives", "UPLAY REWARDS"),
    (0x196CAF1F, "Altair Outfit", "UPLAY REWARDS"),
    (0x55BEEF7D, "Auditore Family Crypt - Paying Respects", "UPLAY REWARDS"),
]

# PSP Bloodlines weapons - special structure with 6 boolean values
# Structure: 17 00 00 00 [HASH:4] 00 00 00 00 06 00 17 00 0B 06 00 00 00 [6 BOOLS]
PSP_WEAPONS_HASH = 0xD92D49F7
PSP_WEAPONS = [
    (0, "Maria Thorpe's Longsword"),
    (1, "Fredrick's Hammer"),
    (2, "Mace of the Bull"),
    (3, "Dark Oracle's Bone Dagger"),
    (4, "Twin's Rapier"),
    (5, "Bouchart's Blade"),
]

# =============================================================================
# CRC32 CHECKSUM
# =============================================================================

def crc32_ac2_options(data: bytes) -> int:
    """
    CRC32 for AC2 OPTIONS files.
    Polynomial: 0x4C11DB7
    Initial: 0x00000000
    XOR Out: 0x1BF3278A
    Reflect Input: Yes
    Reflect Output: Yes
    """
    def reflect_byte(b):
        return int('{:08b}'.format(b)[::-1], 2)

    def reflect_32(val):
        return int('{:032b}'.format(val)[::-1], 2)

    crc = 0x00000000

    for byte in data:
        byte = reflect_byte(byte)
        crc ^= (byte << 24)
        for _ in range(8):
            if crc & 0x80000000:
                crc = ((crc << 1) ^ 0x04C11DB7) & 0xFFFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFFFF

    crc = reflect_32(crc)
    return (crc ^ 0x1BF3278A) & 0xFFFFFFFF


# =============================================================================
# FORMAT DETECTION
# =============================================================================

def detect_format(data: bytes) -> str:
    """Detect PC or PS3 format based on file structure."""
    if len(data) < 16:
        return 'unknown'

    # PS3 format: 8-byte header with size + CRC
    # Try big-endian (typical PS3)
    try:
        prefix_size_be = struct.unpack('>I', data[0:4])[0]
        if prefix_size_be == len(data) - 8:
            # Verify CRC
            prefix_crc = struct.unpack('>I', data[4:8])[0]
            actual_crc = crc32_ac2_options(data[8:8 + prefix_size_be])
            if actual_crc == prefix_crc:
                return 'PS3'
    except:
        pass

    # Try little-endian header
    try:
        prefix_size_le = struct.unpack('<I', data[0:4])[0]
        if prefix_size_le == len(data) - 8:
            prefix_crc = struct.unpack('<I', data[4:8])[0]
            actual_crc = crc32_ac2_options(data[8:8 + prefix_size_le])
            if actual_crc == prefix_crc:
                return 'PS3_LE'
    except:
        pass

    # Check for unlock patterns to verify it's a valid OPTIONS file
    # Look for type prefix 0x0E followed by known hash
    for hash_val, _, _ in BOOL_UNLOCKS:
        pattern = struct.pack('<I', 0x0E) + struct.pack('<I', hash_val)
        if pattern in data:
            return 'PC'

    # Check for PSP weapons hash
    pattern = struct.pack('<I', 0x17) + struct.pack('<I', PSP_WEAPONS_HASH)
    if pattern in data:
        return 'PC'

    return 'unknown'


# =============================================================================
# PROPERTY ACCESS
# =============================================================================

def find_bool_value_offset(data: bytes, hash_value: int) -> int:
    """
    Find boolean property by hash and return offset to value byte.
    Structure: 0E 00 00 00 [HASH:4] 00 00 00 00 00 00 00 00 0B [VALUE]
    """
    hash_bytes = struct.pack('<I', hash_value)
    pos = 0

    while True:
        found = data.find(hash_bytes, pos)
        if found == -1:
            return -1

        # Check type prefix before hash
        if found >= 4:
            type_prefix = struct.unpack('<I', data[found-4:found])[0]
            if type_prefix == 0x0E:
                # Value is 13 bytes after hash start (8 zeros + 0B + value)
                value_offset = found + 13
                if value_offset < len(data):
                    return value_offset

        pos = found + 1

    return -1


def find_psp_weapons_offset(data: bytes) -> int:
    """
    Find PSP weapons structure and return offset to first weapon bool.
    Structure: 17 00 00 00 [HASH:4] 00 00 00 00 06 00 17 00 0B 06 00 00 00 [6 BOOLS]
    """
    hash_bytes = struct.pack('<I', PSP_WEAPONS_HASH)
    pos = 0

    while True:
        found = data.find(hash_bytes, pos)
        if found == -1:
            return -1

        # Check type prefix
        if found >= 4:
            type_prefix = struct.unpack('<I', data[found-4:found])[0]
            if type_prefix == 0x17:
                # 6 bools start 17 bytes after hash position
                # Hash(4) + zeros(4) + len(2) + type(2) + marker(1) + count(4) = 17
                weapons_offset = found + 17
                if weapons_offset + 6 <= len(data):
                    return weapons_offset

        pos = found + 1

    return -1


def get_bool_state(data: bytes, hash_value: int) -> bool:
    """Get boolean unlock state."""
    offset = find_bool_value_offset(data, hash_value)
    if offset == -1:
        return False
    return data[offset] != 0


def set_bool_state(data: bytearray, hash_value: int, unlocked: bool):
    """Set boolean unlock state."""
    offset = find_bool_value_offset(data, hash_value)
    if offset != -1:
        data[offset] = 0x01 if unlocked else 0x00


def get_psp_weapon_state(data: bytes, weapon_index: int) -> bool:
    """Get PSP weapon unlock state."""
    offset = find_psp_weapons_offset(data)
    if offset == -1 or offset + weapon_index >= len(data):
        return False
    return data[offset + weapon_index] != 0


def set_psp_weapon_state(data: bytearray, weapon_index: int, unlocked: bool):
    """Set PSP weapon unlock state."""
    offset = find_psp_weapons_offset(data)
    if offset != -1 and offset + weapon_index < len(data):
        data[offset + weapon_index] = 0x01 if unlocked else 0x00


# =============================================================================
# FILE I/O
# =============================================================================

def load_options_file(filepath: str) -> tuple:
    """Load OPTIONS file and return (data, platform)."""
    with open(filepath, 'rb') as f:
        raw_data = f.read()

    platform = detect_format(raw_data)

    if platform == 'PS3':
        # Big-endian header, extract payload
        prefix_size = struct.unpack('>I', raw_data[0:4])[0]
        data = bytearray(raw_data[8:8 + prefix_size])
        return data, platform, len(raw_data)
    elif platform == 'PS3_LE':
        # Little-endian header
        prefix_size = struct.unpack('<I', raw_data[0:4])[0]
        data = bytearray(raw_data[8:8 + prefix_size])
        return data, platform, len(raw_data)
    else:
        # PC format - no header
        return bytearray(raw_data), platform, len(raw_data)


def save_options_file(filepath: str, data: bytearray, platform: str, original_size: int = 0):
    """Save OPTIONS file with appropriate format."""
    if platform == 'PS3':
        # Big-endian header
        data_size = len(data)
        crc = crc32_ac2_options(bytes(data))

        output = bytearray()
        output.extend(struct.pack('>I', data_size))
        output.extend(struct.pack('>I', crc))
        output.extend(data)

        # Pad to original size if needed
        if original_size > 0 and len(output) < original_size:
            output.extend(bytes(original_size - len(output)))

        with open(filepath, 'wb') as f:
            f.write(output)

    elif platform == 'PS3_LE':
        # Little-endian header
        data_size = len(data)
        crc = crc32_ac2_options(bytes(data))

        output = bytearray()
        output.extend(struct.pack('<I', data_size))
        output.extend(struct.pack('<I', crc))
        output.extend(data)

        if original_size > 0 and len(output) < original_size:
            output.extend(bytes(original_size - len(output)))

        with open(filepath, 'wb') as f:
            f.write(output)

    else:
        # PC format - direct write
        with open(filepath, 'wb') as f:
            f.write(data)


# =============================================================================
# UI HELPERS
# =============================================================================

class UnlockItem:
    def __init__(self, name: str, category: str, hash_value: int = None,
                 weapon_index: int = None, is_psp_weapon: bool = False):
        self.name = name
        self.category = category
        self.hash_value = hash_value
        self.weapon_index = weapon_index
        self.is_psp_weapon = is_psp_weapon
        self.checked = False
        self.available = True  # Whether this unlock exists in the file


def build_unlock_items() -> list:
    """Build list of all unlock items."""
    items = []

    for hash_val, name, category in BOOL_UNLOCKS:
        items.append(UnlockItem(name, category, hash_value=hash_val))

    for idx, name in PSP_WEAPONS:
        items.append(UnlockItem(name, "PSP BLOODLINES WEAPONS",
                                weapon_index=idx, is_psp_weapon=True))

    return items


def load_unlock_states(items: list, data: bytes):
    """Load current unlock states from file data."""
    for item in items:
        if item.is_psp_weapon:
            offset = find_psp_weapons_offset(data)
            item.available = offset != -1
            if item.available:
                item.checked = get_psp_weapon_state(data, item.weapon_index)
        else:
            offset = find_bool_value_offset(data, item.hash_value)
            item.available = offset != -1
            if item.available:
                item.checked = get_bool_state(data, item.hash_value)


def save_unlock_states(items: list, data: bytearray):
    """Save unlock states to file data."""
    for item in items:
        if not item.available:
            continue

        if item.is_psp_weapon:
            set_psp_weapon_state(data, item.weapon_index, item.checked)
        else:
            set_bool_state(data, item.hash_value, item.checked)


# =============================================================================
# CURSES UI
# =============================================================================

def run_curses_ui(stdscr, filepath: str, data: bytearray, platform: str) -> bool:
    """Run the curses UI. Returns True if user wants to save."""
    curses.curs_set(0)
    curses.use_default_colors()

    if curses.has_colors():
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)

    items = build_unlock_items()
    load_unlock_states(items, data)

    # Filter to only available items for navigation
    available_items = [i for i in items if i.available]
    if not available_items:
        stdscr.addstr(0, 0, "No unlocks found in file!", curses.A_BOLD)
        stdscr.addstr(2, 0, "Press any key to exit...")
        stdscr.refresh()
        stdscr.getch()
        return False

    selected = 0
    modified = False
    scroll_offset = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Title
        title = " AC2 Assassin's Creed II - uPlay Rewards Unlocker "
        stdscr.addstr(0, max(0, (width - len(title)) // 2), title,
                      curses.A_BOLD | curses.A_REVERSE)

        # File info
        filename = os.path.basename(filepath)
        info = f" File: {filename} ({platform} format) "
        stdscr.addstr(2, 2, info, curses.color_pair(1) if curses.has_colors() else 0)

        if modified:
            stdscr.addstr(2, 2 + len(info) + 1, "[MODIFIED]",
                          curses.color_pair(3) if curses.has_colors() else curses.A_BOLD)

        # Count available/total
        available_count = len([i for i in items if i.available])
        total_count = len(items)
        stdscr.addstr(3, 2, f" Found {available_count}/{total_count} unlocks ",
                      curses.color_pair(2) if curses.has_colors() else 0)

        # Items display
        max_display = height - 8
        if selected >= scroll_offset + max_display:
            scroll_offset = selected - max_display + 1
        elif selected < scroll_offset:
            scroll_offset = selected

        row = 5
        current_category = None
        display_idx = 0

        for item in items:
            if not item.available:
                continue

            if display_idx < scroll_offset:
                if item.category != current_category:
                    current_category = item.category
                display_idx += 1
                continue

            if row >= height - 3:
                break

            # Category header
            if item.category != current_category:
                current_category = item.category
                if row > 5:
                    row += 1
                if row < height - 3:
                    stdscr.addstr(row, 2, current_category,
                                  curses.A_BOLD | (curses.color_pair(2) if curses.has_colors() else 0))
                    row += 1

            if row >= height - 3:
                break

            # Checkbox
            checkbox = "[x]" if item.checked else "[ ]"
            is_selected = display_idx == selected
            attr = curses.A_REVERSE if is_selected else 0

            stdscr.addstr(row, 4, checkbox, attr)
            stdscr.addstr(row, 8, item.name[:width-10], attr)
            row += 1
            display_idx += 1

        # Footer
        footer_row = height - 2
        footer = " [Space] Toggle  [A] All On  [N] All Off  [S] Save  [Q] Quit "
        stdscr.addstr(footer_row, max(0, (width - len(footer)) // 2), footer, curses.A_REVERSE)

        stdscr.refresh()

        # Input
        key = stdscr.getch()

        if key in (ord('q'), ord('Q'), 27):  # Q or Escape
            if modified:
                stdscr.addstr(height - 3, 2, "Discard changes? (y/n) ", curses.A_BOLD)
                stdscr.refresh()
                confirm = stdscr.getch()
                if confirm not in (ord('y'), ord('Y')):
                    continue
            return False

        elif key in (ord('s'), ord('S')):
            save_unlock_states(items, data)
            return True

        elif key in (curses.KEY_UP, ord('k')):
            selected = max(0, selected - 1)

        elif key in (curses.KEY_DOWN, ord('j')):
            selected = min(len(available_items) - 1, selected + 1)

        elif key in (ord(' '), curses.KEY_ENTER, 10):
            available_items[selected].checked = not available_items[selected].checked
            modified = True

        elif key in (ord('a'), ord('A')):
            for item in available_items:
                item.checked = True
            modified = True

        elif key in (ord('n'), ord('N')):
            for item in available_items:
                item.checked = False
            modified = True

    return False


# =============================================================================
# TEXT UI (fallback)
# =============================================================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def run_text_ui(filepath: str, data: bytearray, platform: str) -> bool:
    """Run simple text-based UI. Returns True if user wants to save."""
    items = build_unlock_items()
    load_unlock_states(items, data)

    available_items = [i for i in items if i.available]
    if not available_items:
        print("No unlocks found in file!")
        return False

    while True:
        clear_screen()
        print("=" * 70)
        print(" AC2 Assassin's Creed II - uPlay Rewards Unlocker")
        print("=" * 70)
        print(f" File: {os.path.basename(filepath)} ({platform} format)")
        print(f" Found {len(available_items)}/{len(items)} unlocks")
        print("=" * 70)
        print()

        # Display items
        current_category = None
        item_num = 1

        for item in items:
            if not item.available:
                continue

            if item.category != current_category:
                current_category = item.category
                print(f"\n  {current_category}")
                print("  " + "-" * 50)

            checkbox = "[x]" if item.checked else "[ ]"
            print(f"  {item_num:2d}. {checkbox} {item.name}")
            item_num += 1

        print()
        print("=" * 70)
        print(f" Commands: 1-{len(available_items)} toggle | A=all on | N=all off | S=save | Q=quit")
        print("=" * 70)

        try:
            choice = input("\n> ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return False

        if choice == 'Q':
            return False
        elif choice == 'S':
            save_unlock_states(items, data)
            return True
        elif choice == 'A':
            for item in available_items:
                item.checked = True
        elif choice == 'N':
            for item in available_items:
                item.checked = False
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(available_items):
                available_items[idx].checked = not available_items[idx].checked

    return False


# =============================================================================
# MAIN
# =============================================================================

def main():
    if len(sys.argv) < 2:
        print("AC2 Assassin's Creed II - uPlay Rewards Unlocker")
        print()
        print("Usage: python ac2_uplay_unlocker.py <OPTIONS_FILE>")
        print()
        print("Examples:")
        print("  python ac2_uplay_unlocker.py OPTIONS")
        print("  python ac2_uplay_unlocker.py OPTIONS.PS3")
        return 1

    filepath = sys.argv[1]

    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        return 1

    print(f"Loading {filepath}...")

    try:
        data, platform, original_size = load_options_file(filepath)
    except Exception as e:
        print(f"Error loading file: {e}")
        return 1

    if platform == 'unknown':
        print("Warning: Could not auto-detect format, assuming PC")
        platform = 'PC'

    print(f"Detected format: {platform}")
    print(f"Data size: {len(data)} bytes")

    # Run UI
    if HAS_CURSES and sys.stdin.isatty():
        try:
            save = curses.wrapper(
                lambda stdscr: run_curses_ui(stdscr, filepath, data, platform))
        except KeyboardInterrupt:
            print("\nCancelled.")
            return 0
        except Exception as e:
            # Fall back to text UI if curses fails
            print(f"Curses UI failed ({e}), using text mode...")
            save = run_text_ui(filepath, data, platform)
    else:
        save = run_text_ui(filepath, data, platform)

    if save:
        print(f"\nSaving to {filepath}...")
        save_options_file(filepath, data, platform, original_size)
        print("Done!")
    else:
        print("\nNo changes saved.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
